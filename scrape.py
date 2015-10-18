#!/usr/bin/env python

import argparse
import json
import os

from pprint import pprint

def get_blob_path_from_sha(sha, data_dir):
    sha_type, sha = sha.split(':')
    path = os.path.join(data_dir,
                        'docker/registry/v2/blobs/',
                        sha_type,
                        sha[:2],
                        sha,
                        'data')
    assert os.path.exists(path), "Could not find file at {}".format(path)
    return path
    

def get_layer_path_from_sha(sha, image, data_dir):
    sha_type, sha = sha.split(':')
    path = os.path.join(data_dir,
                        'docker/registry/v2/repositories/',
                        image,
                        '_layers',
                        sha_type,
                        sha,
                        'link')
    assert os.path.exists(path), "Could not find file at {}".format(path)
    return path
    

def get_index_path_from_sha(sha, image, tag, data_dir):
    sha_type, sha = sha.split(':')
    path = os.path.join(data_dir,
                        'docker/registry/v2/repositories/',
                        image,
                        '_manifests/tags',
                        tag,
                        'index',
                        sha_type,
                        sha,
                        'link')
    assert os.path.exists(path), "Could not find file at {}".format(path)
    return path
    

def get_revision_path_from_sha(sha, image, data_dir):
    sha_type, sha = sha.split(':')
    path = os.path.join(data_dir,
                        'docker/registry/v2/repositories/',
                        image,
                        '_manifests/revisions',
                        sha_type,
                        sha)
    assert os.path.exists(path), "Could not find file at {}".format(path)
    return path


def get_signature_blob_paths(revision_path, data_dir, paths):
    signatures_path = os.path.join(revision_path,
                                   'signatures')
    for dirpath, _, link in os.walk(signatures_path):
        if link:
            with open(os.path.join(dirpath, link[0]), 'r') as f:
                sha = f.read()
            blob = get_blob_path_from_sha(sha, data_dir)
            paths.add(blob)
    

def get_manifest(image, tag, data_dir, paths):
    manifest_link = os.path.join(data_dir,
                                 'docker/registry/v2/repositories',
                                 image,
                                 '_manifests/tags/',
                                 tag,
                                 'current/link')
    paths.add(manifest_link)
    with open(manifest_link, 'r') as link:
        sha = link.read()
    blob = get_blob_path_from_sha(sha, data_dir)
    paths.add(blob)
    
    with open(blob, 'r') as manifest_file:
        manifest = json.load(manifest_file)

    index_path = get_index_path_from_sha(sha, image, tag, data_dir)
    paths.add(index_path)

    revision_path = get_revision_path_from_sha(sha, image, data_dir)
    paths.add(revision_path)

    signature_path = get_signature_blob_paths(revision_path, data_dir, paths)
    paths.add(signature_path)

    return manifest



def get_paths_to_copy(image, tag, data_dir):
    paths = set()

    paths.add(get_uploads_path(image, data_dir))

    manifest = get_manifest(image, tag, data_dir, paths)
    for item in manifest['fsLayers']:
        blob_path = get_blob_path_from_sha(item['blobSum'], data_dir)
        paths.add(blob_path)
        layer_path = get_layer_path_from_sha(item['blobSum'], image, data_dir)
        paths.add(layer_path)

    pprint(paths)
    return paths


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

    def get_paths(self, image, tag):
        paths = set()
        
        paths.add(self._get_uploads_path(image))
        return paths

    def copy_paths(self, paths, output_dir):
        for path in paths:
            if path:
                self.storage.check_path(path)
                rel_path = os.path.relpath(path, self.storage.data_dir)
                new_path = os.path.join(output_dir, rel_path)
                new_dir = os.path.dirname(new_path)
                try:
                    os.makedirs(new_dir)
                except OSError:
                    pass
                if os.path.isdir(path):
                    os.makedirs(new_path)
                self.storage.copy(path, new_path)


def split_image_and_tag(full_image_name):
    if ':' in full_image_name:
        return full_image_name.split(':')
    return full_image_name, 'latest'


def main(args):
    scraper = Scraper(args)
    paths = set()

    for img in args.image:
        image, tag = split_image_and_tag(img)
        paths.update(scraper.get_paths(image, tag))

    pprint(paths)

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
