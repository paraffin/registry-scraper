import os

from boto import connect_s3
from boto.s3.key import Key
from boto.exception import S3ResponseError


class PathNotFound(Exception):
    pass


def _ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        pass


class S3Storage(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.conn = connect_s3()
        self.bucket = self.conn.get_bucket(data_dir)

    def _remove_bucket_name(self, path):
        return os.path.relpath(path, self.data_dir)

    def check_path(self, full_path):
        path = self._remove_bucket_name(full_path)
        for item in self.bucket.list(path):
            if item is not None:
                return True
        return False

    def _copy_file(self, path, new_path):
        if not os.path.exists(new_path):
            print("Copying {} to {}".format(path, new_path))
            key = Key(self.bucket)
            key.key = path
            key.get_contents_to_filename(new_path)
        else:
            print("Path already exists: {}".format(new_path))

    def copy(self, full_path, new_path):
        path = self._remove_bucket_name(full_path)
        if not self.isdir(full_path):
            new_file = os.path.join(new_path, os.path.basename(path))
            self._copy_file(path, new_path)
        else:
            for item in self.bucket.list(path+'/'):
                relative_path = os.path.relpath(item.name, path)
                new_file = os.path.join(new_path, relative_path)
                _ensure_dir(os.path.dirname(new_file))
                self._copy_file(item.name, new_file)

    def read_file(self, full_path):
        path = self._remove_bucket_name(full_path)
        key = Key(self.bucket)
        key.key = path
        try:
            return key.get_contents_as_string()
        except S3ResponseError as e:
            print("FATAL ERROR: Failed to find file at path {}".format(path))
            raise

    def isdir(self, full_path):
        path = self._remove_bucket_name(full_path)
        for item in self.bucket.list(path+'/'):
            return True
        return False

    def walk_files(self, full_path):
        path = self._remove_bucket_name(full_path)
        all_keys = self.bucket.list(path+'/')
        all_files = [os.path.join(self.data_dir, key.name) for key in all_keys]
        for f in all_files:
            yield f
