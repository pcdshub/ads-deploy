VERSION=$(shell git describe --tags)

all: image

image:
	docker build -t pcdshub/ads-deploy:$(VERSION) .

push:
	docker push pcdshub/ads-deploy:$(VERSION)


.PHONY: all image push
