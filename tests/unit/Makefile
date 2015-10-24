.PHONY: test

install-requirements:
	pip install -r requirements.txt

pytest: install-requirements
	py.test .

lint: install-requirements
	pep8 ../../registry_scraper/
	pep8 .

test: lint pytest

