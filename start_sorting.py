from tqdm import tqdm

from sort import sort_files

def start_args_sorting(src_folder, dst_folder, do_convert, total_files, file_list):
    """
    Runs the sorting operation, only used when the script is run with command line arguments.

    Args:
        src_folder (str): The path of the source folder.
        dst_folder (str): The path of the destination folder.
        do_convert (bool): Whether to convert the JXR images to PNG.
        total_files (int): The total number of files to sort.
        file_list (list): A list of files to sort.
    """
    with tqdm(total=total_files, desc="Tri des fichiers", unit="fichier") as pbar:
        sort_files(
            src_folder,
            dst_folder,
            do_convert,
            lambda curr, total, _, __: pbar.update(1),
            file_list,
            total_files,
        )


def start_gui_sorting(
    src_folder, dst_folder, do_convert, update_progress_bar, total_files, file_list
):
    """
    Runs the sorting operation with gui.

    Args:
        src_folder (str): The path of the source folder.
        dst_folder (str): The path of the destination folder.
        do_convert (bool): Whether to convert the JXR images to PNG.
        update_progress_bar (function): A function to update the progress bar.
        total_files (int): The total number of files to sort.
        file_list (list): A list of files to sort.
    """
    sort_files(
        src_folder,
        dst_folder,
        do_convert,
        update_progress_bar,
        file_list,
        total_files,
        check_cancel=True,
    )
