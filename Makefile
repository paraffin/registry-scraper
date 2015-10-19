pull-test-image-internet:
	sudo docker pull busybox:latest
	sudo docker tag busybox:latest localhost:5000/busybox:latest

run-initial-registry:
	sudo docker run -d -p 5000:5000 --restart=always --name registry \
		-v `pwd`/data:/var/lib/registry \
		registry:2
	sleep 1

push-images:
	sudo docker push localhost:5000/busybox:latest

delete-images:
	-sudo docker rmi -f busybox:latest localhost:5000/busybox:latest

stop-initial-registry:
	-sudo docker stop registry
	-sudo docker rm registry

scrape:
	./scrape.py busybox:latest

run-final-registry:
	sudo docker run -d -p 5000:5000 --restart=always --name registry \
		-v `pwd`/data-copy:/var/lib/registry \
		registry:2
	sleep 1
	
diff:
	diff -r data data-copy

pull-test-image-local:
	sudo docker pull localhost:5000/busybox:latest

test: pull-test-image-internet run-initial-registry push-images delete-images stop-initial-registry scrape diff run-final-registry pull-test-image-local

clean: stop-initial-registry delete-images
	sudo rm -rf data data-copy
