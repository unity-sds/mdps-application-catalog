

## Configuration

Most configuration for the service is setup through environment variables.

### Auth Setup

### Auth Overview

Authorization within the register-api requires an openid (cognito) provider or oauth2 provider (keycloak). The auth controls a few items:
* Validation of the token used to authenticate (Bearer token)
* Ensures registering an API to a `namespace` requires that it either match the username or be in the list of auth `groups` that a user is a member of.

The register API supports 2 flavors of authorization: cognito and keycloak. While these are both "standard" implementations, they are different enough that we have two implementations of them.

#### AWS COGNITO configuration
```
export JWT_AUTH_TYPE=COGNITO
export JWT_VALIDATION_URL=https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USERPOOL_ID}/.well-known/jwks.json
export JWT_ISSUER_URL=https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USERPOOL_ID}
export JWT_CLIENT_ID={COGNITO_CLIENT_ID} #e.g. 40c2134mmf2....
# This should always be 'cognito:groups' for cognito auth
export JWT_GROUPS_KEY=cognito:groups
```
#### Keycloak configuration
```
export JWT_AUTH_TYPE=KEYCLOAK
export JWT_VALIDATION_URL=http://{KEYCLOAK_URL}:8080/realms/{REALM}/protocol/openid-connect/certs
export JWT_ISSUER_URL=http://{KEYCLOAK_URL}/realms/{REALM}
export JWT_CLIENT_ID={CLIENT_ID}
export JWT_GROUPS_KEY=groups
```
*Note: the JWT validation url must be _accessible_ from the register-api servier. The issuer_url must match what is in the token. These, in production, will almost certainly be the same, but if using docker containers, the validation url will often be 'host.docker.internal:8080...' while the issuer url will be 'localhost:8080' if running these on the same host machine.*

For setting this up in keycloack, a client must be created (e.g. register-api) and have the following items set:
* Direct access grants (allows the exchange of a user/password for a token)
* Client authentication is turned _off_
* a role of 'user' should be created. keycloack users must be added to this client role to have access to the register-api.
* a `client scopes` mapping, where `client-id-dedicated` (e.g. register-api-dedicated) has a keycloak `Group Membership` mapping titled `groups`. (controlled by the JWT_GROUPS key)


### Getting a token

For Keycloak, you'll need to hit the realm/client endpoint to generate a token:

```bash
curl -X POST -s {KEYCLOAK_URL}/realms/{REALM}}/protocol/openid-connect/token \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=password' \
--data-urlencode 'client_id={CLIENT_ID}' \
--data-urlencode 'username={USER}' \
--data-urlencode 'password={PASSWORD}' | jq .access_token
```

For MDPS/cognito, you can use the built in mdps/sds client libraries:

```
from unity_sds_client.unity import Unity
s = Unity(UnityEnvironments.DEV) # or TEST|PROD
token = s._session.get_auth().get_token()
```

## Development Setup

### Create a virtual env and install python

```python -m venv .venv 
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
### start up a postgres server

### update inis, env files

### Run the server
.venv/bin/uvicorn main:app --reload

## Docker Setup
`docker-compose up`


## Database Cleanup

```
# Stop the containers
docker-compose down

# Remove the volume
docker-compose down -v

# Start fresh
docker-compose up --build
```