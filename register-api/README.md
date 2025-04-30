
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