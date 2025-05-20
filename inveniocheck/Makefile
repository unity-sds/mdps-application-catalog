export IMAGE_PREFIX = docker.io
export USERNAME = alexandye
export NAME = invenio-test
export NAMESPACE = invenio
export VERSION ?= test

all: build push

build:
	docker build -t ${IMAGE_PREFIX}/${USERNAME}/${NAME}:${VERSION} .

push:
	docker push ${IMAGE_PREFIX}/${USERNAME}/${NAME}:${VERSION}

deploy:
	find manifests -name '*.yaml' | xargs -I {} sh -c "eval_file {} | kubectl apply -f - --namespace=${NAMESPACE}"
