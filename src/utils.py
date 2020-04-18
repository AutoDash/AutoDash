import os

def get_parent_dir(cur_dir):
    return os.path.abspath(os.path.join(cur_dir, os.pardir))

def get_project_root():
    return get_parent_dir(get_parent_dir(os.path.abspath(__file__)))
