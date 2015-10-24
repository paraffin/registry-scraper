# Registry Scraper

This is a simple tool to pull particular images from a Docker registry, preserving the Docker
registry file structure, in essence creating a 'shallow clone' of a registry. This is useful for
example if you want to ship a registry containing only a subset of the images contained in a
privately hosted registry (Docker registry currently only allows mirroring of Docker Hub, not
private registries).

It requires direct access to the storage backend of the registry; it does not use the registry API.

## Running the Scraper

Currently only the local file storage backend is supported and the script must be run on the same
machine as the registry.

### Run a Local Registry

The first step should be to run the registry. If you haven't already, ensure that your Docker daemon
is running with the option `--insecure-registry localhost:5000`.

To run a registry, run `make run-initial-registry` or do it manually with

```bash
docker run -d -p 5000:5000 --restart=always --name registry \
	-v `pwd`/data:/var/lib/registry \
	registry:2
```

### Populate With Images

Now you can push images to it:

```bash
docker pull someimage
docker tag someimage localhost:5000/someimage:mytag
docker push localhost:5000/someimage:mytag
```

### Scrape Images

Now just run the `scrape.py` script:

```bash
./scrape.py someimage:mytag --data-dir `pwd`/data --output-dir `pwd`/data-copy
```

If you don't specify a tag it will default to the `latest` tag.

### Ship the Registry

Now you can ship the registry. Simply tar up the output directory, extract it on your target system,
and run a local storage registry using the extracted path as the backend. You should be able to pull
your images from it.

```bash
docker run -d -p 5000:5000 --restart=always --name registry \
	-v /path/you/extracted:/var/lib/registry \
	registry:2
```

## Testing

Currently there are no unit tests for this script, only end-to-end tests.

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

