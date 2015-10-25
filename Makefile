.PHONY: install

install:
	python setup.py install

test-unit:
	cd tests/unit && make test

test-e2e:
	cd tests/e2e && make test

test: test-unit test-e2e

