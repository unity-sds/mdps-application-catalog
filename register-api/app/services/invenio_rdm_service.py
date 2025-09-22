import string
from typing import Optional, Tuple
import os
from datetime import datetime, timezone
import requests
from fastapi.logger import logger
import logging
from types import SimpleNamespace


from app.models.application_package import ApplicationPackageDetails, ApplicationPackageVersion
from app.models.job import Job, JobStatus
from app.core.config import settings
from ap_validator.app_package import AppPackage
import json


class IvenioRDMService:

    # # Uncomment this block if you'd like way too much info on the http requests being made to RDM

    # try:
    #     import http.client as http_client
    # except ImportError:
    #     # Python 2
    #     import httplib as http_client
    # http_client.HTTPConnection.debuglevel = 1
    # # You must initialize logging, otherwise you'll not see debug output.
    # logging.basicConfig()
    # logging.getLogger().setLevel(logging.DEBUG)
    # requests_log = logging.getLogger("requests.packages.urllib3")
    # requests_log.setLevel(logging.DEBUG)
    # requests_log.propagate = True
    

    def __init__(self, url: string, token:string):
        self.invenio_root = url
        self.token = token
        self.h = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.fh = {
            "Accept": "application/json",
            "Content-Type": "application/octet-stream",
            "Authorization": f"Bearer {self.token}"
        }   


    def get_package(self, namespace, package_name) -> ApplicationPackageDetails:
        logger.error(f"fetching {namespace}/{package_name}")
        query_string = f"metadata.title:\"{package_name}\""  
        params = {
            "q":query_string
        }
        headers = {
            "Authorization":f"Bearer {self.token}"
        }
        resp = requests.get(f'{self.invenio_root}/api/communities/{namespace}/records', params=params, headers=self.h, verify=False)
        community_items = resp.json()['hits']['hits']
        if len(community_items) > 1:
            logger.error("too many packages returned?!")
            raise ValueError("Multiple Pacakges found with title in given namespace")
        elif len(community_items) == 0:
            logger.error(f"No Packages found matching {namespace}/{package_name}")
            return None
        else:
            return ApplicationPackageDetails.from_rdm_package(community_items[0])
    

    def get_community_id(self, namespace):
        headers = {
            "Authorization":f"Bearer {self.token}"
        }
        resp = requests.get(f'{self.invenio_root}/api/communities/{namespace}', headers=headers, verify=False)
        if resp.status_code == 200:
            return resp.json()['id']
        elif resp.status_code == 404:
            return None


    def get_package_version(self, namespace, package_name, package_version=None) -> ApplicationPackageDetails:
        query_string = f"metadata.title:\"{package_name}\""
        params = {}
        # if package version is specified, add it here.
        if package_version:
            query_string = query_string + f" metadata.version:\"{package_version}\""
            params['allversions']='true'
            params['size']=100

        params['q'] = query_string
            
        headers = {
            "Authorization":f"Bearer {self.token}"
        }
        resp = requests.get(f'{self.invenio_root}/api/communities/{namespace}/records', params=params, headers=headers, verify=False)
        community_items = resp.json()['hits']['hits']
        if  len(community_items) == 0:
            return None
        else:
            for item in community_items:
                if item['metadata']['version'] == package_version:
                    app_package_version = ApplicationPackageVersion.from_rdm_package_version(item)
                    return app_package_version
            
            return None

    def add_package_version(self, app_package_version: ApplicationPackageVersion):
        # Setup the requests


        current_module_dir = os.path.dirname(__file__)

        # Construct the absolute path to the file
        # Replace 'data' and 'my_file.txt' with your actual directory and file names
        file_path = os.path.join(current_module_dir, 'rdm_record.templ.json')
        
        with open(file_path) as fp:
            data = json.load(fp)

        # Updated templated data:

        if app_package_version.uploader is None:
            user = "UNKNOWN"
        else:
            user = app_package_version.uploader


        data['parent']['review']['receiver']['community'] = self.get_community_id(app_package_version.app_package.namespace)
        data['metadata']['creators'][0]['person_or_org']['family_name'] = user
        data['metadata']['title'] = app_package_version.app_package.artifactName
        data['metadata']['version'] = app_package_version.artifact_version
        data['metadata']['publication_date'] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        logger.error(data)
        logger.error(json.dumps(data))

        #if the app package already exists, create a new version
        if app_package_version.app_package.id is not None:
            logger.error("Package exists, creating new version")
            r = requests.post(
                f"{self.invenio_root}/api/records/{app_package_version.app_package.id}/versions", headers=self.h, verify=False)
            assert r.status_code == 201, \
                f"Failed to create new record version (code: {r.status_code}, response: {r.json()})"
            links = r.json()['links']
            logger.error(r.json())
            # new returned id:
            new_rev_id = r.json()['id']

            # now add the metadata to the new draft
            # Create a new record
            r = requests.put(
                f"{self.invenio_root}/api/records/{new_rev_id}/draft", data=json.dumps(data), headers=self.h, verify=False)
            assert r.status_code == 200, \
                f"Failed to update draft  record (code: {r.status_code}, response: {r.json()})"
            links = r.json()['links']
            logger.error(r.json())


        else:
            # Create a new record
            logger.error("Package does not exists, creating new pacakge and version")
            r = requests.post(
                f"{self.invenio_root}/api/records", data=json.dumps(data), headers=self.h, verify=False)
            assert r.status_code == 201, \
                f"Failed to create new record (code: {r.status_code}, response: {r.json()})"
            links = r.json()['links']
            logger.error(r.json())

        logger.error(links)
        # Initiate the file
        f = app_package_version.cwl_url
        data = json.dumps([{"key": os.path.basename(f)}])
        r = requests.post(links["files"].replace("https://127.0.0.1:5000", self.invenio_root), data=data, headers=self.h, verify=False)
        logger.error(r.json())
        assert r.status_code == 201, \
            f"Failed to create file {f} (code: {r.status_code})"
        
        # when running invenvio locally (127.0.0.1), we cannot use these as we need to address `self.invenio_root` and not 127.0.0.1
        file_links = r.json()["entries"][0]["links"]

        # Upload file content by streaming the data
        with open(f, 'rb') as fp:
            r = requests.put(
                file_links["content"].replace("https://127.0.0.1:5000", self.invenio_root), data=fp, headers=self.fh, verify=False)
        assert r.status_code == 200, \
            f"Failed to upload file contet {f} (code: {r.status_code})"

        # Commit the file.
        r = requests.post(file_links["commit"].replace("https://127.0.0.1:5000", self.invenio_root), headers=self.h, verify=False)
        assert r.status_code == 200, \
            f"Failed to commit file {f} (code: {r.status_code})"
        
        # Publish the package?
        # for RDM, this makes sense as it's not "viewable" outside the initial user unless its published.
        r = requests.post(links["publish"].replace("https://127.0.0.1:5000", self.invenio_root), headers=self.h, verify=False)
        logger.error(r.json())
        assert r.status_code == 202, \
            f"Failed to publish record (code: {r.status_code})"
        # submit files
            

    

    
