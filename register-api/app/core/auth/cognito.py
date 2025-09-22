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


class CognitoTokenUse(Enum):
    ID = "id"
    ACCESS = "access"


class CognitoJWTAuthorizer(JWTAuthorizer):
    def __init__(self):
        self.groups = []
        self.username = None

    def get_username(self) -> str:
        return self.username

    def get_groups(self) -> list[str]:
        return self.groups
    
    def __init__(
            self,
            required_token_use: CognitoTokenUse,
            cognito_app_client_id: str,
            jwks_client: jwt.PyJWKClient,
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
        self.required_token_use = required_token_use
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

        """
        Check the token_use claim
        * If you are only accepting the access token in your web API operations,
          its value must be access.
        * If you are only using the ID token, its value must be id.
        * If you are using both ID and access tokens,
          the token_use claim must be either id or access.
        """
        if self.required_token_use.value != claims["token_use"]:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )

        """
        The "aud" claim in an ID token and the "client_id" claim in an access token 
        should match the app client ID that was created in the Amazon Cognito user pool.
        """
        if self.required_token_use == CognitoTokenUse.ID:
            if "aud" not in claims:
                logger.error("not authorized -- id.aud")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            if claims["aud"] != self.cognito_app_client_id:
                logger.error("not authorized -- id.aud != client_id")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
        elif self.required_token_use == CognitoTokenUse.ACCESS:
            if "client_id" not in claims:
                logger.error("not authorized -- access.client_id ")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            if claims["client_id"] != self.cognito_app_client_id:
                logger.error(f"{claims['client_id']} != {self.cognito_app_client_id}")
                logger.error("not authorized -- access.client_id != client_id")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
        else:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        
        self.username = claims['username']
        self.groups = claims[settings.JWT_GROUPS_KEY]
        return self


jwt_authorizer_access_token = CognitoJWTAuthorizer(
    CognitoTokenUse.ACCESS,
    settings.JWT_CLIENT_ID,
    jwks_client,
)
