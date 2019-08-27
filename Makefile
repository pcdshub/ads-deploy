# VERSION=$(shell git describe --tags)
VERSION=v0.0.0

all: image

image:
	docker build -t pcdshub/ads-deploy:$(VERSION) .

push:
	docker push pcdshub/ads-deploy:$(VERSION)


.PHONY: all image push
