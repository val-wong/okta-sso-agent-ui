APP?=okta-sso-agent
REGISTRY?=
IMAGE?=$(REGISTRY)$(APP)
TAG?=latest

build:
	docker build -t $(IMAGE):$(TAG) .

run:
	docker compose up -d --build

stop:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker exec -it $$(docker ps --filter name=api -q) sh

push:
	docker push $(IMAGE):$(TAG)