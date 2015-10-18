pull-test-image-internet:
	sudo docker pull debian:jessie
	sudo docker tag debian:jessie localhost:5000/debian:jessie

run-initial-registry:
	sudo docker run -d -p 5000:5000 --restart=always --name registry \
		-v `pwd`/data:/var/lib/registry \
		registry:2
	sleep 3

push-images:
	sudo docker push localhost:5000/debian:jessie

delete-images:
	-sudo docker rmi -f debian:jessie localhost:5000/debian:jessie

stop-initial-registry:
	-sudo docker stop registry
	-sudo docker rm registry

scrape:
	./scrape.py debian:jessie

run-final-registry:
	sudo docker run -d -p 5000:5000 --restart=always --name registry \
		-v `pwd`/data-copy:/var/lib/registry \
		registry:2
	sleep 3
	
diff:
	diff -r data data-copy

pull-test-image-local:
	sudo docker pull localhost:5000/debian:jessie

test: pull-test-image-internet run-initial-registry push-images delete-images stop-initial-registry scrape run-final-registry diff pull-test-image-local

clean: stop-initial-registry delete-images
	sudo rm -rf data data-copy