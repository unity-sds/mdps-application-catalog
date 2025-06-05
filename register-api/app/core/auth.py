import app
from app.core.config import settings
from fastapi.logger import logger
from app.core.keycloak import jwt_authorizer_access_token as ky_auth
from app.core.cognito import jwt_authorizer_access_token as cog_auth


def get_authorizer():
    if settings.JWT_AUTH_TYPE == "COGNITO":
        return cog_auth
    elif settings.JWT_AUTH_TYPE == "KEYCLOAK":
        return ky_auth