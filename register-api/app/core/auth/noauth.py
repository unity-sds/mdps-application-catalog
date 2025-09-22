from enum import Enum
from typing import Annotated

import jwt
from fastapi import Header, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import settings
from fastapi.logger import logger

from app.core.auth.jwt_authorizer import JWTAuthorizer


# Modified from https://www.angelospanag.me/blog/verifying-a-json-web-token-from-cognito-in-python-and-fastapi
# https://github.com/angelospanag/python-fastapi-cognito-jwt-verification/tree/main

## TODO make this more generic as the JWT might not be a cognito one.

#uses the host.docker.internal to access an external server on the hsot machine
#jwt_validation_url = f"http://host.docker.internal:8080/realms/master/protocol/openid-connect/certs"

# don't use 'host.docker.internal' here as it needs to match the cert
#jwt_issuer = "http://localhost:8080/realms/master"

jwt_validation_url = settings.JWT_VALIDATION_URL
jwt_issuer = settings.JWT_ISSUER_URL

jwks_client = jwt.PyJWKClient(
    jwt_validation_url
)


class NoneJWTAuthorizer(JWTAuthorizer):
    def __init__(self):
        self.groups = []
        self.username = None

    def get_username(self) -> str:
        return self.username

    def get_groups(self) -> list[str]:
        return self.groups
    
    def is_valid_namespace_op(self, namespace) -> bool:
        return True

    
    def __init__(
            self
    ) -> None:
        """Verify an incoming JWT using official AWS guidelines.

        https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html#amazon-cognito-user-pools-using-tokens-manually-inspect

        Args:
            required_token_use (CognitoTokenUse): Required Cognito token type
            aws_default_region (str): AWS region
            cognito_user_pool_id (str): Cognito User Pool ID
            cognito_app_client_id (str): Cognito App Pool ID
            jwks_client (jwt.PyJWKClient): An instance of a JWKS client that has
                                           retrieved the public Cognito JWKS

        Raises:
            fastapi.HTTPException: Raised if a verification check of the incoming
                                     JWT fails
        """



    def __call__(self, authorization: Annotated[str | None, Header()] = None):
        
        self.username = "defaultUser"
        self.groups = []
        return self


jwt_authorizer_access_token = NoneJWTAuthorizer(
    
)
