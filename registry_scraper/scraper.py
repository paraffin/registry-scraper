import json
import os

from storage_drivers.local import LocalStorage
from storage_drivers.s3 import S3Storage


def _ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        pass


def _split_image_and_tag(full_image_name):
    if ':' in full_image_name:
        return full_image_name.split(':')
    return full_image_name, 'latest'


class Scraper():

    def __init__(self, storage_type, data_dir):
        self.storage_type = storage_type
        self.data_dir = data_dir
        self._storage = None

    @property
    def storage(self):
        if self.storage_type == 'local':
            self._storage = LocalStorage(self.data_dir)
        elif self.storage_type == 's3':
            self._storage = S3Storage(self.data_dir)
        return self._storage

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
        for link in self.storage.walk_files(signatures_path):
            sha = self.storage.read_file(link)
            blob = self._get_blob_path_from_sha(sha)
            paths.add(blob)

        paths.add(revision_path)
        return paths

    def get_paths(self, image, tag):
        paths = set()

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
                self.storage.check_path(path)
                rel_path = os.path.relpath(path, self.storage.data_dir)
                new_path = os.path.join(output_dir, rel_path)
                new_dir = os.path.dirname(new_path)
                _ensure_dir(new_dir)
                if self.storage.isdir(path):
                    _ensure_dir(new_path)
                self.storage.copy(path, new_path)

    def check_paths(self, paths):
        paths_not_found = []
        for path in paths:
            if path:
                try:
                    self.storage.check_path(path)
                except PathNotFound:
                    paths_not_found.append(path)
        if paths_not_found:
            raise PathNotFound("The following paths were not found "
                               "in the registry storage: {}"
                               .format(paths_not_found))
