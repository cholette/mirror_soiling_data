"""
mirror_soiling_data — access packaged mirror soiling datasets.

Provides helper functions to list and access dataset files distributed
with the package, regardless of whether it's installed as a wheel,
editable install, or zipapp.
"""

from importlib import resources
from typing import List


def get_dataset_path(dataset:str):

    pkg_root = resources.files(__package__)

    dataset_path = pkg_root.joinpath(dataset)
    if not dataset_path.is_dir():
        raise FileNotFoundError(
            f"Dataset folder '{dataset}' not found in package '{__package__}'.\n"
            f"Available datasets: {list_available_datasets()}"
        )
    
    return dataset_path


def get_datafile_path(dataset: str, filename: str):
    """
    Return a Traversable path to a data file inside a dataset subfolder.

    Parameters
    ----------
    dataset : str
        Name of the dataset subfolder (e.g., "ablrf").
    filename : str
        File name within that dataset folder (e.g., "data.xlsx").

    Returns
    -------
    Traversable
        A Traversable object (Path-like) pointing to the requested file.

    Raises
    ------
    FileNotFoundError
        If the dataset or file does not exist.
    """
    pkg_root = resources.files(__package__)

    dataset_path = pkg_root.joinpath(dataset)
    if not dataset_path.is_dir():
        raise FileNotFoundError(
            f"Dataset folder '{dataset}' not found in package '{__package__}'.\n"
            f"Available datasets: {list_available_datasets()}"
        )

    file_path = dataset_path.joinpath(filename)
    if not file_path.exists():
        raise FileNotFoundError(
            f"File '{filename}' not found in dataset '{dataset}'.\n"
            f"Available files: {list_dataset_files(dataset)}"
        )

    return file_path


def list_dataset_files(dataset: str) -> List[str]:
    """
    List all files in a given dataset subfolder.

    Parameters
    ----------
    dataset : str
        Name of the dataset subfolder.

    Returns
    -------
    list of str
        Filenames contained within that dataset folder.

    Raises
    ------
    FileNotFoundError
        If the dataset folder does not exist.
    """
    pkg_root = resources.files(__package__)
    dataset_path = pkg_root.joinpath(dataset)

    if not dataset_path.is_dir():
        raise FileNotFoundError(
            f"Dataset folder '{dataset}' not found in package '{__package__}'.\n"
            f"Available datasets: {list_available_datasets()}"
        )

    return [p.name for p in dataset_path.iterdir() if p.is_file()]


def list_available_datasets() -> List[str]:
    """
    List all dataset subfolders available in the package.

    Returns
    -------
    list of str
        Names of available dataset directories.
    """
    pkg_root = resources.files(__package__)
    return [p.name for p in pkg_root.iterdir() if p.is_dir()]
