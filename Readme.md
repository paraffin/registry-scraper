# Registry Scraper

This is a simple tool to pull particular images from a Docker registry, preserving the Docker
registry file structure. This is useful for example if you want to ship a registry containing only
a subset of the images contained in a registry.

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

Currently there are no unit tests for this script. To run a functional end-to-end test, simply run
`make clean && make test`. This will download the busybox:latest docker image, run a local storage
registry, push the image, run the scraper, test that the new directory structure is identical to
the original one, and finally attempt to pull the image from a new registry.
