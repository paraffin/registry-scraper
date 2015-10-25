from unittest import TestCase
from mock import patch

from registry_scraper.scraper import Scraper, _split_image_and_tag
from registry_scraper.storage_drivers.s3 import S3Storage


class TestScraper(TestCase):
    """
    Test the Scraper
    """

    def test_split_image_and_tag(self):
        expected = ['user/image', 'tag']
        rv = _split_image_and_tag('user/image:tag')
        self.assertEquals(rv, expected)

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
            'data-copy/docker/registry/v2/blobs/sha256/fo/foo/data',
            'data-copy/docker/registry/v2/blobs/sha256/ba/bar/data',
            'data-copy/docker/registry/v2/repositories/someimage/'
            '_layers/sha256/foo/link',
            'data-copy/docker/registry/v2/repositories/someimage/'
            '_layers/sha256/bar/link'
            ])
        s = Scraper('local', 'data-copy')
        layer_paths = s._get_layers(image, manifest)

        self.assertEqual(layer_paths, true_paths)

    @patch.object(S3Storage, 'walk_files')
    def test_get_signature_blob_paths(self, mock_storage):
        expected = set(['fakebucket/docker/registry/v2/repositories/someimage/'
                       '_manifests/revisions/sha256/foo'])

        mock_storage.walk_files.return_value = list(expected)[0]

        s = Scraper('s3', 'fakebucket')
        rv = s._get_signature_blob_paths('sha256:foo', 'someimage')

        self.assertEqual(rv, expected)
