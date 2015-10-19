#!/usr/bin/env python

import argparse
import json
import os

from pprint import pprint

def _ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

class Scraper():

    def __init__(self, args):
        if args.storage_type == 'local':
            from storage_drivers.local import LocalStorage
            self.storage = LocalStorage(args.data_dir)
        elif args.storage_type == 's3':
            from storage_drivers import S3Storage
            self.storage = S3Storage(args.data_dir)

    def _get_uploads_path(self, image):
        return os.path.join(self.storage.data_dir,
                            'docker/registry/v2/repositories',
                            image,
                            '_uploads')

    def _get_manifests_path(self, image, tag):
        return os.path.join(self.storage.data_dir,
                            'docker/registry/v2/repositories',
                            image,
                            '_manifests/tags',
                            tag)

    def _get_blob_path_from_sha(self, sha):
        sha_type, sha = sha.split(':')
        return os.path.join(self.storage.data_dir,
                            'docker/registry/v2/blobs/',
                            sha_type,
                            sha[:2],
                            sha,
                            'data')
    
    def _get_layer_link_from_sha(self, image, sha):
        sha_type, sha = sha.split(':')
        return os.path.join(self.storage.data_dir,
                            'docker/registry/v2/repositories/',
                            image,
                            '_layers',
                            sha_type,
                            sha,
                            'link')

    def _get_layers(self, image, manifest):
        layer_shas = set()
        for elem in manifest['fsLayers']:
            layer_shas.add(elem['blobSum'])

        layer_paths = set()
        for layer_sha in layer_shas:
            layer_paths.add(self._get_blob_path_from_sha(layer_sha))
            layer_paths.add(self._get_layer_link_from_sha(image, layer_sha))

        return layer_paths

    def _get_revision_path_from_sha(self, sha, image):
        sha_type, sha = sha.split(':')
        return os.path.join(self.storage.data_dir,
                            'docker/registry/v2/repositories/',
                            image,
                            '_manifests/revisions',
                            sha_type,
                            sha)

    def _get_signature_blob_paths(self, sha, image):
        revision_path = self._get_revision_path_from_sha(sha, image)
        signatures_path = os.path.join(revision_path,
                                       'signatures')
        paths = set()
        for dirpath, _, link in os.walk(signatures_path):
            if link:
                sha = self.storage.read_file(os.path.join(dirpath, link[0]))
                blob = self._get_blob_path_from_sha(sha)
                paths.add(blob)

        paths.add(revision_path)
        return paths
    
    def get_paths(self, image, tag):
        paths = set()
        
        paths.add(self._get_uploads_path(image))

        manifests_path = self._get_manifests_path(image, tag)
        paths.add(manifests_path)

        manifest_link = os.path.join(manifests_path, 'current/link')
        manifest_sha = self.storage.read_file(manifest_link)
        manifest_path = self._get_blob_path_from_sha(manifest_sha)
        paths.add(manifest_path)

        manifest = json.loads(self.storage.read_file(manifest_path))
        paths.update(self._get_layers(image, manifest))

        paths.update(self._get_signature_blob_paths(manifest_sha, image))

        return paths
    
    def copy_paths(self, paths, output_dir):
        for path in paths:
            if path:
                # ORANGE:
                # Still needs some refactoring to make non-local storage work
                self.storage.check_path(path)
                rel_path = os.path.relpath(path, self.storage.data_dir)
                new_path = os.path.join(output_dir, rel_path)
                new_dir = os.path.dirname(new_path)
                _ensure_dir(new_dir)
                if self.storage.isdir(path):
                    _ensure_dir(new_path)
                self.storage.copy(path, new_path)


def _split_image_and_tag(full_image_name):
    if ':' in full_image_name:
        return full_image_name.split(':')
    return full_image_name, 'latest'


def main(args):
    scraper = Scraper(args)
    paths = set()
    for img in args.image:
        image, tag = _split_image_and_tag(img)
        paths.update(scraper.get_paths(image, tag))
    scraper.copy_paths(paths, args.output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=str, nargs='+',
                        help="Name of image to scrape. Don't include registry name.\
                                eg. myimage:mytag. Tag defaults to latest")
    parser.add_argument('-s', '--storage-type', type=str, choices=['local','s3'],
                        default='local',
                        help="Registry storage backend.")
    parser.add_argument('-d', '--data-dir', type=str, default='data',
                        help="Registry data directory or S3 bucket")
    parser.add_argument('-o', '--output-dir', type=str, default='data-copy',
                        help="Path to copy to")
    
    args = parser.parse_args()

    main(args)
