from django.core.files import File
from django.core.files.storage import Storage, default_storage


def save(path: str, file: File, overwrite=False, storage: Storage = default_storage):  # noqa: FBT002
    """Export a file directly to a project storage.

    Args:
        path (str): The destination path.
        file (File): The file to be saved.
        overwrite (bool, optional): If the destination should be overwritten.
        Defaults to False.
        storage (Storage, optional): The storage instance to be used.
        Defaults to `default_storage`.
    """
    if overwrite is True and storage.exists(path):
        storage.delete(path)
    storage.save(path, file)
