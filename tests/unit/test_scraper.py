import unittest

from registry_scraper.scraper import Scraper


class TestScraper(unittest.TestCase):
    """
    Test the Scraper
    """

    def test_get_blob_path_from_sha_basic(self):
        s = Scraper('local', 'data-copy')
        sha = 'sha256:abcd123'
        true_path = 'data-copy/docker/registry/v2/blobs/sha256/ab/abcd123/data'
        self.assertEqual(s._get_blob_path_from_sha(sha), true_path)

    def test_get_layer_link_from_sha_basic(self):
        s = Scraper('local', 'data-copy')
        sha = 'sha256:abcd123'
        true_path = 'data-copy/docker/registry/v2/repositories/someimage/'\
                    '_layers/sha256/abcd123/link'
        self.assertEqual(s._get_layer_link_from_sha('someimage', sha),
                         true_path)

    def test_get_layers_basic(self):
        image = 'someimage'
        manifest = {
            'fsLayers': [
                {'blobSum': 'sha256:foo'},
                {'blobSum': 'sha256:foo'},
                {'blobSum': 'sha256:bar'}
                ]
            }

        true_paths = set([
            'asdf'
            ])
        s = Scraper('local', 'data-copy')
        layer_paths = s._get_layers(image, manifest)

        self.assertEqual(layer_paths, true_paths)
