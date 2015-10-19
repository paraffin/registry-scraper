import os

class PathNotFound(Exception):
    pass


def _copy_file(path, new_path):
    os.system('rsync -azr {} {}'.format(
              path, new_path))


class LocalStorage(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def check_path(self, path):
        ''' Check that a path exists. '''
        if not os.path.exists(path):
            raise PathNotFound("The specified path was not found: {}".format(path))

    def copy(self, path, new_path):
        if os.path.isdir(path):
            for item in os.listdir(path):
                _copy_file(os.path.join(path, item), new_path)
        else:
            _copy_file(path, new_path)

    def read_file(self, path):
        with open(path, 'r') as f:
            out = f.read()
        return out

    def isdir(self, path):
        return os.path.isdir(path)
