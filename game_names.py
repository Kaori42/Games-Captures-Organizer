import os
import re
from collections import Counter


def clean_filename(filename):
    """
    Cleans up a filename by removing certain patterns.

    Args:
        filename (str): The name of the file to be cleaned.

    Returns:
        cleaned_filename (str): The cleaned version of the input filename.

    Examples:
        >>> filename = "1_2_2022 10_30_45 - Example File (1).txt"
        >>> clean_filename(filename)
        'Example File.txt'
    """
    if re.fullmatch(r"\d+(_\d+)*", filename):
        return re.search(r"\d+", filename).group()

    pattern = (
        r"(\s*\d{1,2}_\d{1,2}_\d{2,4}(?:\s*\d{1,2}_\d{1,2}_\d{1,2})?\s*)"
        r"|(\s*-\s*\d+\.\d+\.\d+\.\d+\s*\(.*?\)\s*)"
        r"|(\s-.*|Screenshot.*)"
    )
    cleaned_filename = re.sub(pattern, "", filename).strip()

    cleaned_filename = cleaned_filename.replace("_", " ")

    cleaned_filename = re.sub(r"\s+", " ", cleaned_filename).strip()

    return cleaned_filename


def common_filename_part(folder_path):
    """
    Returns a list of common parts of filenames in the specified folder.

    Args:
        folder_path (str): The path of the folder containing the files.

    Returns:
        common_parts (list): A list of common parts of filenames in the specified folder.
    """
    files = os.listdir(folder_path)

    counter = Counter(
        [
            re.match(r"(.*?\D)\d", f).group(1).strip()
            for f in files
            if re.match(r"(.*?\D)\d", f)
        ]
    )

    common_strings = [s for s in counter.keys() if counter[s] > 2]

    common_parts = []
    for s in common_strings:
        matches = [f for f in files if f.startswith(s)]
        common_part = os.path.commonprefix(matches).rsplit(" ", 1)[0].strip()

        cleaned_common_part = clean_filename(common_part)

        common_parts.append(cleaned_common_part)

    return common_parts


def find_game_name(filename, common_parts):
    """
    Finds the name of the game in the specified common_parts.

    Args:
        filename (str): The name of the current file.
        common_parts (list): A list of common parts of filenames in the specified folder.

    Returns:
        str: The name of the game in the specified common_parts.
    """
    cleaned_filename = clean_filename(filename)

    if any(cleaned_filename.startswith(s) for s in ["Ce PC", "Photos", "Screenshot"]):
        return "Default"

    for game_name in common_parts:
        if game_name in cleaned_filename:
            return game_name

    return "Default"
