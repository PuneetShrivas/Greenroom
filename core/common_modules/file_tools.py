import sys
import os
def get_abs_path(filename, selfpath):
    script_dir = os.path.dirname(os.path.abspath(selfpath))
    file_path = os.path.join(script_dir, filename)
    return file_path