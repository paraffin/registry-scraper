#!/usr/bin/env python

import argparse
import json
import os

from pprint import pprint

def get_blob_path_from_sha(sha, data_dir):
    type, sha = sha.split(':')
    path = os.path.join(data_dir,
                        'docker/registry/v2/blobs/',
                        type,
                        sha[:2],
                        sha,
                        'data')
    assert os.path.exists(path), "Could not find file at {}".format(path)
    return path
    

def get_layer_path_from_sha(sha, image, data_dir):
    type, sha = sha.split(':')
    path = os.path.join(data_dir,
                        'docker/registry/v2/repositories/',
                        image,
                        '_layers',
                        type,
                        sha,
                        'link')
    assert os.path.exists(path), "Could not find file at {}".format(path)
    return path
    

def get_index_path_from_sha(sha, image, tag, data_dir):
    type, sha = sha.split(':')
    path = os.path.join(data_dir,
                        'docker/registry/v2/repositories/',
                        image,
                        '_manifests/tags',
                        tag,
                        'index',
                        type,
                        sha,
                        'link')
    assert os.path.exists(path), "Could not find file at {}".format(path)
    return path
    

def get_revision_path_from_sha(sha, image, data_dir):
    type, sha = sha.split(':')
    path = os.path.join(data_dir,
                        'docker/registry/v2/repositories/',
                        image,
                        '_manifests/revisions',
                        type,
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


def get_uploads_path(image, data_dir):
    return os.path.join(data_dir,
                        'docker/registry/v2/repositories',
                        image)


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


def split_image_and_tag(full_image_name):
    if ':' in full_image_name:
        return full_image_name.split(':')
    return full_image_name, 'latest'


def copy_paths(paths, data_dir, output_dir):
    for path in paths:
        if path:
            assert os.path.exists(path), "Path doesn't exist!"
            rel_path = os.path.relpath(path, data_dir)
            new_path = os.path.join(output_dir, rel_path)
            new_dir = os.path.dirname(new_path)
            if os.path.isdir(path):
                path = os.path.join(path, '*')
            try:
                os.makedirs(new_dir)
            except OSError:
                pass
            print("copying {} to {}".format(path, new_path))
            os.system('rsync -avzr {} {}'.format(
                path, new_path))


def main(args):
    image, tag = split_image_and_tag(args.image)
    paths = get_paths_to_copy(image, tag, args.data_dir)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    copy_paths(paths, args.data_dir, args.output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=str,
                        help="Name of image to scrape. Don't include registry name.")
    parser.add_argument('-d', '--data-dir', type=str, default='data/',
                        help="Registry data directory")
    parser.add_argument('-o', '--output-dir', type=str, default='data-copy/',
                        help="Path to copy to")
    
    args = parser.parse_args()

    main(args)
