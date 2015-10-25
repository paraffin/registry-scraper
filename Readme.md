# Registry Scraper

This is a simple tool to pull particular images from a Docker registry, preserving the Docker
registry file structure, in essence creating a 'shallow clone' of a registry. This is useful for
example if you want to ship a registry containing only a subset of the images contained in a
privately hosted registry (Docker registry currently only allows mirroring of Docker Hub, not
private registries).

It requires direct access to the storage backend of the registry; it does not use the registry API.
This means you must either run it on the same machine as a local storage backed registry or have
access rights to an S3-backed registry. Other file storage backends are not currently supported.

## Running the Scraper

### Install

Install with `make install`

### Usage

Now just run the `scrape` script:

```bash
scrape --storage local --data-dir `pwd`/data --output-dir `pwd`/data-copy someimage:mytag
```

Or for S3:

```bash
scrape --storage s3 --data-dir bucket-name --output-dir `pwd`/data-copy someimage:mytag
```

If you don't specify a tag it will default to the `latest` tag.

## Testing

This project has a test suite. To run it, follow the instructions for setting up the S3 Storage
Backend test and create a Python virtual environment. Then simply run `make test`.

### Local Storage Backend

To run a test using the local storage backend, simply rm `make clean && make test-local` in the tests
directory. This will download the latest progrium/busybox image, run a local-storage backed
registry, push the image to the registry, run the scrape command, and then test a pull from a
registry backed by the scraped image.

### S3 Storage Backend

If you have AWS credentials with access to an S3 bucket you can use for testing, you can also test
the S3 storage backend scraper.

First, copy `tests/registry-config.env.example` to `tests/registry-config.env` and fill in the
bucket details. Second, export your AWS access credentials to the environment variables
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_KEY`. Now you can run `make clean && make test-s3`. This will do
the same test as the local storage backend test, except it will create and scrape from a registry
backed by S3 storage.

## Registries

If you want to play around outside the e2e testing sandbox, you can use these instructions to create
your own registries.

### Run a Local Storage Registry

If you haven't already, ensure that your Docker daemon is running with the option
`--insecure-registry localhost:5000`.

To run a registry, run `make run-local-storage-registry` in the tests/e2e directory or do it manually
 with

```bash
docker run -d -p 5000:5000 --restart=always --name registry \
	-v `pwd`/data:/var/lib/registry \
	registry:2
```

### Run an S3-backed registry

If you haven't already, ensure that your Docker daemon
is running with the option `--insecure-registry localhost:5000`.

To run a registry, run `make run-s3-storage-registry` in the tests/e2e directory or do it manually with

```bash
docker run -d -p 5000:5000 --restart=always --name registry \
	-v `pwd`/data:/var/lib/registry \
	registry:2
```

Note that for testing purposes, the make target actually runs the registry on port 5002, so you
will need to change the commands below to use `localhost:5002`.

### Populate With Images

Now you can push images to it:

```bash
docker pull someimage
docker tag someimage localhost:5000/someimage:mytag
docker push localhost:5000/someimage:mytag
```

### Ship the Registry

Now you can ship the registry. Simply tar up the output directory, extract it on your target system,
and run a local storage registry using the extracted path as the backend. You should be able to pull
your images from it.

```bash
docker run -d -p 5000:5000 --restart=always --name registry \
	-v /path/you/extracted:/var/lib/registry \
	registry:2
```

## Contributing

This project is under active development and contributions of all kinds are welcome.

Pull requests will not be accepted if any tests are failing, including PEP8 and technical debt.

Use a maximum line width of 100 characters on any file that is not Python.
