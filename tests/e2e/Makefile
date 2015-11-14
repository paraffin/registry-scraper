.PHONY: \
    push-image-local-storage \
    push-image-s3-storage \
    scrape-local \
    scrape-s3 \
    run-local-storage-test-registry \
    run-s3-storage-test-registry \
    test-local-storage-image \
    test-s3-storage-image \
    test-local \
    test-s3 \
    test \
    clean \
    install-requirements \
    pull-test-image-internet \
    run-local-storage-registry \
    run-s3-storage-registry \
    delete-images \
    stop-registry \
    delete-directories

# Fake remote name so we can use docker hub for our source image
DOCKER_REMOTE ?= progrium
IMAGE_NAME ?= busybox

S3_BUCKET ?= $(shell grep -i s3_bucket registry-config.env | cut -d'=' -f2)

install-scrape:
	cd ../../ && make install

pull-test-image-internet:
	docker pull $(DOCKER_REMOTE)/$(IMAGE_NAME)

run-local-storage-registry:
	docker run -d -p 5000:5000 --restart=always --name registry \
		-v `pwd`/data:/var/lib/registry \
		registry:2
	sleep 1

run-s3-storage-registry:
	REGISTRY_STORAGE_S3_ACCESSKEY=$$AWS_ACCESS_KEY_ID \
	REGISTRY_STORAGE_S3_SECRETKEY=$$AWS_SECRET_ACCESS_KEY \
	REGISTRY_STORAGE_S3_BUCKET=$(S3_BUCKET) \
	docker run -d -p 5002:5000 --restart=always --name registry-s3 \
	    --env-file=registry-config.env \
		registry:2
	sleep 1

push-image-local-storage: run-local-storage-registry pull-test-image-internet
	docker tag -f $(DOCKER_REMOTE)/$(IMAGE_NAME) localhost:5000/$(IMAGE_NAME)
	docker push localhost:5000/$(IMAGE_NAME)

push-image-s3-storage: run-s3-storage-registry pull-test-image-internet
	docker tag -f $(DOCKER_REMOTE)/$(IMAGE_NAME) localhost:5002/$(IMAGE_NAME)
	docker push localhost:5002/$(IMAGE_NAME)

scrape-local: push-image-local-storage install-scrape
	scrape $(IMAGE_NAME)

scrape-s3: push-image-s3-storage install-scrape
	scrape -s s3 -d $(S3_BUCKET) -o s3-copy $(IMAGE_NAME)

run-local-storage-test-registry: scrape-local
	docker run -d -p 5001:5000 --restart=always --name registry-local \
		-v `pwd`/data-copy:/var/lib/registry \
		registry:2
	sleep 1
	
run-s3-storage-test-registry: scrape-s3
	docker run -d -p 5003:5000 --restart=always --name registry-s3-test \
		-v `pwd`/s3-copy:/var/lib/registry \
		registry:2
	sleep 1
	
test-local-storage-image: run-local-storage-test-registry
	docker run --rm localhost:5001/$(IMAGE_NAME) echo "I'm working!"

test-s3-storage-image: run-s3-storage-test-registry
	docker run --rm localhost:5003/$(IMAGE_NAME) echo "I'm working!"


test-local: clean test-local-storage-image

test-s3: clean test-s3-storage-image

test: test-local test-s3 

delete-images:
	-docker rmi -f \
         $(DOCKER_REMOTE)/$(IMAGE_NAME) \
         localhost:5000/$(IMAGE_NAME) \
         localhost:5001/$(IMAGE_NAME) \
         localhost:5002/$(IMAGE_NAME) \
	 localhost:5003/$(IMAGE_NAME)

stop-registry:
	-docker stop registry
	-docker rm registry
	-docker stop registry-local
	-docker rm registry-local
	-docker stop registry-s3
	-docker rm registry-s3
	-docker stop registry-s3-test
	-docker rm registry-s3-test

delete-directories:
	sudo rm -rf data data-copy s3-copy

clean: stop-registry delete-images delete-directories
