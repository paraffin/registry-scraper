.PHONY: test

install-requirements:
	pip install -r requirements.txt

pytest: install-requirements
	py.test .

lint: install-requirements
	cd ../../ && pep8 registry_scraper/
	cd ../../ && pep8 tests/unit

test: lint pytest

