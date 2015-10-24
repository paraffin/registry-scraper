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
        self.assertEqual(true_path, s._get_blob_path_from_sha(sha))
