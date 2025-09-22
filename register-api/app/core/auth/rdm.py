from enum import Enum
from typing import Annotated

import jwt
from fastapi import Header, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import settings
from fastapi.logger import logger

from app.core.auth.jwt_authorizer import JWTAuthorizer



class CognitoTokenUse(Enum):
    ID = "id"
    ACCESS = "access"


class RDMJWTAuthorizer(JWTAuthorizer):

    def __init__(self):
        self.groups = []
        self.username = None
        self.token = None

    def get_username(self) -> str:
        return self.username

    def get_groups(self) -> list[str]:
        return self.groups

    def get_token(self) -> str:
        return self.token

    def __call__(self, authorization: Annotated[str | None, Header()] = None):
        """Verify an embedded Cognito JWT token in the 'Authorization' header.

        Args:
            authorization (str | None): 'Authorization' header of a FastAPI endpoint
        """
        logger.error(authorization)
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
        self.token = token
        
        return self
    
    # Function to check mambership in a group for valid namespace ops
    # For RDM Auth, we rely on RDM to handle all of these items.
    def is_valid_namespace_op(self, namespace) -> bool:
            return True


rdm_access_token = RDMJWTAuthorizer()
