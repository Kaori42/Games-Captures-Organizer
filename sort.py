import os
import time
import subprocess

from game_names import common_filename_part, find_game_name
from folders import create_folder_structure


def sort_files(
    src_folder,
    dst_folder,
    do_convert,
    update_progress,
    file_list,
    total_files,
    check_cancel=False,
):
    """
    Sorts the files in the specified source folder and moves them to the specified destination folder.

    Args:
        src_folder (str): The path of the source folder.
        dst_folder (str): The path of the destination folder.
        do_convert (bool): Whether to convert the JXR images to PNG.
        update_progress (function): A function to update the progress bar.
        file_list (list): A list of files to sort.
        total_files (int): The total number of files to sort.
        check_cancel (bool, optional): Whether to check if the user has cancelled the sorting operation. Defaults to False.
    """
    common_part = common_filename_part(src_folder)
    start_time = time.time()

    for current_file, entry in enumerate(file_list, start=1):
        if check_cancel:
            from gui import cancel_sorting

            if cancel_sorting:
                break

        filename = entry.name
        file_ext = os.path.splitext(filename)[1].lower()[1:]
        game_name = find_game_name(filename, common_part)

        create_folder_structure(dst_folder, game_name, file_ext)
        src_path = os.path.join(src_folder, filename)
        dst_path = os.path.join(dst_folder, game_name, file_ext.upper(), filename)

        if file_ext in ["jxr", "png"]:
            os.rename(src_path, dst_path)
            if file_ext == "jxr" and do_convert:
                conv_path = os.path.join(
                    dst_folder,
                    game_name,
                    "Conv",
                    os.path.splitext(filename)[0] + "-sdr.png",
                )
                script_dir = os.path.dirname(os.path.realpath(__file__))
                hdrfix_path = os.path.join(script_dir, "hdrfix.exe")
                subprocess.call(
                    [hdrfix_path, dst_path, conv_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )

        elapsed_time = time.time() - start_time
        estimated_time_remaining = (elapsed_time / current_file) * (
            total_files - current_file
        )

        update_progress(
            current_file, total_files, elapsed_time, estimated_time_remaining
        )
