DOCKER_REMOTE ?= progrium
IMAGE_NAME ?= busybox

pull-test-image-internet:
	docker pull $(DOCKER_REMOTE)/$(IMAGE_NAME)
	docker tag -f $(DOCKER_REMOTE)/$(IMAGE_NAME) localhost:5000/$(IMAGE_NAME)

run-initial-registry:
	docker run -d -p 5000:5000 --restart=always --name registry \
		-v `pwd`/data:/var/lib/registry \
		registry:2
	sleep 1

push-images:
	docker push localhost:5000/$(IMAGE_NAME)

delete-images:
	-docker rmi -f $(DOCKER_REMOTE)/$(IMAGE_NAME) localhost:5000/$(IMAGE_NAME)

stop-initial-registry:
	-docker stop registry
	-docker rm registry

scrape-local:
	./scrape.py $(IMAGE_NAME)

run-final-registry:
	docker run -d -p 5000:5000 --restart=always --name registry \
		-v `pwd`/data-copy:/var/lib/registry \
		registry:2
	sleep 1
	
diff:
	diff -r data data-copy

pull-test-image-local:
	docker pull localhost:5000/$(IMAGE_NAME)

test-image:
	docker run --rm localhost:5000/$(IMAGE_NAME) echo "I'm working!"

test: pull-test-image-internet run-initial-registry push-images delete-images stop-initial-registry scrape-local diff run-final-registry pull-test-image-local test-image

clean: stop-initial-registry delete-images
	sudo rm -rf data data-copy s3copy
