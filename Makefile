.PHONY: install build

include tests/tech-debt/tech-debt.mk

install:
	python setup.py install

build:
	python setup.py sdist

test-unit: install
	cd tests/unit && make test

test-e2e:
	cd tests/e2e && make test && make clean

test: test-unit test-e2e test-tech-debt
