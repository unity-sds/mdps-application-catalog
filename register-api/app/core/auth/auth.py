import app
from app.core.config import settings
from fastapi.logger import logger
from app.core.auth.keycloak import jwt_authorizer_access_token as ky_auth
from app.core.auth.cognito import jwt_authorizer_access_token as cog_auth
from app.core.auth.noauth import jwt_authorizer_access_token as no_auth


# NONE should only be used in local development environments
def get_authorizer():
    if settings.JWT_AUTH_TYPE == "COGNITO":
        return cog_auth
    elif settings.JWT_AUTH_TYPE == "KEYCLOAK":
        return ky_auth
    elif settings.JWT_AUTH_TYPE == "NONE":
        return no_auth