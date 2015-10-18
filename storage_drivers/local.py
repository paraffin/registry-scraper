import os

class PathNotFound(Exception):
    pass


def _copy_file(path, new_path):
    os.system('rsync -avzr {} {}'.format(
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
            for dirpath, dirs, files in os.walk(path):
                for f in files:
                    _copy_file(os.path.join(dirpath, f), new_path)
                for d in dirs:
                    _copy_file(os.path.join(dirpath, d), new_path)
        else:
            _copy_file(path, new_path)

