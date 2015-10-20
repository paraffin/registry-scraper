DOCKER_REMOTE ?= docker.hq.datarobot.com
IMAGE_NAME ?= datarobot/provisioner:latest
pull-test-image-internet:
	sudo docker pull $(DOCKER_REMOTE)/$(IMAGE_NAME)
	sudo docker tag $(DOCKER_REMOTE)/$(IMAGE_NAME) localhost:5000/$(IMAGE_NAME)

run-initial-registry:
	sudo docker run -d -p 5000:5000 --restart=always --name registry \
		-v `pwd`/data:/var/lib/registry \
		registry:2
	sleep 1

push-images:
	sudo docker push localhost:5000/$(IMAGE_NAME)

delete-images:
	-sudo docker rmi -f $(DOCKER_REMOTE)/$(IMAGE_NAME) localhost:5000/$(IMAGE_NAME)

stop-initial-registry:
	-sudo docker stop registry
	-sudo docker rm registry

scrape:
	./scrape.py $(IMAGE_NAME)

run-final-registry:
	sudo docker run -d -p 5000:5000 --restart=always --name registry \
		-v `pwd`/data-copy:/var/lib/registry \
		registry:2
	sleep 1
	
diff:
	diff -r data data-copy

pull-test-image-local:
	sudo docker pull localhost:5000/$(IMAGE_NAME)

test-image:
	docker run --rm localhost:5000/$(IMAGE_NAME) echo "I'm working!"

test: pull-test-image-internet run-initial-registry push-images delete-images stop-initial-registry scrape diff run-final-registry pull-test-image-local test-image

clean: stop-initial-registry delete-images
	sudo rm -rf data data-copy
