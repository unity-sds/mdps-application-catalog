from enum import Enum
from typing import Annotated

import jwt
from fastapi import Header, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.auth.jwt_authorizer import JWTAuthorizer
from app.core.config import settings
from fastapi.logger import logger


# Modified from https://www.angelospanag.me/blog/verifying-a-json-web-token-from-cognito-in-python-and-fastapi
# https://github.com/angelospanag/python-fastapi-cognito-jwt-verification/tree/main

## TODO make this more generic as the JWT might not be a cognito one. Add to env
jwt_validation_url = settings.JWT_VALIDATION_URL
jwt_issuer = settings.JWT_ISSUER_URL
#jwt_validation_url = f"https://cognito-idp.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
#jwt_issuer = f"https://cognito-idp.{self.aws_default_region}.amazonaws.com/{self.cognito_user_pool_id}"

jwks_client = jwt.PyJWKClient(
    jwt_validation_url
)


class CognitoTokenUse(Enum):
    ID = "id"
    ACCESS = "access"


class KeycloakJWTAuthorizer(JWTAuthorizer):
    def __init__(self):
        self.groups = []
        self.username = None

    def get_username(self) -> str:
        return self.username

    def get_groups(self) -> list[str]:
        return self.groups

    def __init__(
            self,
            cognito_app_client_id: str,
            jwks_client: jwt.PyJWKClient,
    ):
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
        self.cognito_app_client_id = cognito_app_client_id
        self.jwks_client = jwks_client

    def __call__(self, authorization: Annotated[str | None, Header()] = None):
        """Verify an embedded Cognito JWT token in the 'Authorization' header.

        Args:
            authorization (str | None): 'Authorization' header of a FastAPI endpoint
        """
        if not authorization:
            logger.error("not authorized!")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        split_authorization_tokens: list[str] = authorization.split("Bearer ")
        if len(split_authorization_tokens) < 2:
            logger.error("not authorized -- len")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )

        token: str = split_authorization_tokens[1]

        # Attempt to retrieve the signature of the incoming JWT
        try:
            #logger.error(f"https://cognito-idp.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json")
            signing_key: jwt.PyJWK = self.jwks_client.get_signing_key_from_jwt(token)
        except jwt.exceptions.InvalidTokenError as e:
            logger.error(e)
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            ) from e

        try:
            """
            * Verify the signature of the JWT
            * Verify that the algorithm used is RS256
            * Verification of audience 'aud' is taken care later when we examine if the
              token is 'id' or 'access'
            * Verify that the token hasn't expired. Decode the token and compare the 
              'exp' claim to the current time.
            * The issuer (iss) claim should match your user pool. For example, a user
              pool created in the eu-west-2 region
              will have the following iss value: https://cognito-idp.us-east-1.amazonaws.com/<userpoolID>.
            * Require the existence of claims: 'token_use', 'exp', 'iss', 'sub'
            """
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=jwt_issuer,
                options={
                    "verify_aud": False,
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                    "require": ["exp", "iss", "sub"],
                },
            )
            logger.debug(claims)
        except jwt.exceptions.ExpiredSignatureError as e:
            logger.exception(e)
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            ) from e
        except jwt.exceptions.InvalidTokenError as e:
            logger.exception(e)
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            ) from e


        # Check the token for access to the resources given the client_id:
        if "resource_access" not in  claims:
            logger.error("No resource_access entry in token" )
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        
        if self.cognito_app_client_id not in  claims['resource_access']:
            logger.error("No  " + self.cognito_app_client_id + " entry in token['resource_access']" )
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="You are unauthorized to access this resource. Please contact a service administrator for more info."
            )
        
        #self.roles = claims['resource_access'][self.cognito_app_client_id]['roles']
        self.username = claims['preferred_username']
        self.groups = claims[settings.JWT_GROUPS_KEY]
        return self



jwt_authorizer_access_token = KeycloakJWTAuthorizer(
    settings.JWT_CLIENT_ID,
    jwks_client
)

# cognito_jwt_authorizer_id_token = CognitoJWTAuthorizer(
#     CognitoTokenUse.ID,
#     settings.AWS_DEFAULT_REGION,
#     settings.COGNITO_USER_POOL_ID,
#     settings.COGNITO_APP_CLIENT_ID,
#     jwks_client,
# )