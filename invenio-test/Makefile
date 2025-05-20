# export IMAGE_PREFIX
export NAME = invenio-test
export NAMESPACE = invenio
export VERSION ?= test

all: build push

build:
	docker build -t ${NAME}:${VERSION} .

push:
	docker push ${NAME}:${VERSION}

deploy:
	find manifests -name '*.yaml' | xargs -I {} sh -c "eval_file {} | kubectl apply -f - --namespace=${NAMESPACE}"
