import os
from tkinter import filedialog


def create_folder_structure(base_folder, folder_name, file_ext):
    """
    Creates the folder structure for the specified file extension and game name.

    Args:
        base_folder (str): The path of the base folder.
        folder_name (str): The name of the folder to create.
        file_ext (list): The file extension of the current file.
    """
    folders_to_create = {
        "jxr": ["JXR", "Conv"],
        "png": ["PNG"],
    }

    subfolders = folders_to_create.get(file_ext.lower(), [])

    for subfolder in subfolders:
        path = os.path.join(base_folder, folder_name, subfolder)
        if not os.path.exists(path):
            os.makedirs(path)


def select_folder(var):
    """
    Allows the user to select a folder and sets the specified variable to the path of the selected folder.

    Args:
        var (str): The variable to set to the path of the selected folder.
    """
    folder_path = filedialog.askdirectory()
    if folder_path != "":
        var.set(folder_path)
    else:
        var.set("Aucun dossier sélectionné")
