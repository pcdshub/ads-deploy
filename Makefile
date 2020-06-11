# VERSION=$(shell git describe --tags)
VERSION=v2.6.5

all: image

image:
	docker build -t pcdshub/ads-deploy:$(VERSION) .

push:
	docker push pcdshub/ads-deploy:$(VERSION)

latest:
	docker build -t pcdshub/ads-deploy:latest .
	docker push pcdshub/ads-deploy:latest


.PHONY: all image push latest
