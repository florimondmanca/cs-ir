import os


def find_files(root: str):
    return (
        (e.name, os.path.join(root, e.name))
        for e in os.scandir(root)
        if e.is_file()
    )


def find_dirs(root: str):
    return (
        (e.name, os.path.join(root, e.name))
        for e in os.scandir(root)
        if e.is_dir()
    )
