import os
import subprocess
import re
import time
import tkinter as tk
from collections import Counter
from tkinter import filedialog, messagebox, ttk
from ttkthemes import ThemedTk
import argparse
import sys
from tqdm import tqdm
from colorama import Fore, Style


def parse_args():
    """
    Parse command line arguments using the argparse module and return the parsed arguments.

    Returns:
        argparse.Namespace or None: The parsed command line arguments as an argparse.Namespace object if there are any arguments, otherwise None.
    """
    parser = argparse.ArgumentParser(description="Organisateur de fichiers")
    parser.add_argument("--src", help="Chemin du dossier source")
    parser.add_argument("--dst", help="Chemin du dossier de destination")
    parser.add_argument(
        "--convert", help="Convertir les images JXR", action="store_true"
    )
    parser.add_argument(
        "--same_folder", help="Trier dans le même dossier", action="store_true"
    )
    return parser.parse_args() if len(sys.argv) > 1 else None


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


def create_main_window(root):
    """
    Creates the main window.

    Args:
        root (ThemedTk): The root window.
    """
    root.title("Organisateur de fichiers")
    root.tk.call("lappend", "auto_path", "./awthemes-10.4.0")
    root.tk.call("package", "require", "awdark")
    root.tk.call(
        "::themeutils::setThemeColors",
        "arc",
        "style.progressbar",
        "rounded-line",
        "style.scale",
        "circle-rev",
        "style.scrollbar-grip",
        "none",
        "scrollbar.has.arrows",
        "false",
    )
    style = ttk.Style()
    style.theme_use("awdark")
    style.configure("TProgressbar", background="green", troughcolor="grey")


def create_container(root):
    """
    Creates the container for the widgets.

    Args:
        root (ThemedTk): The root window.

    Returns:
        container (Frame): The container for the widgets.
    """
    container = ttk.Frame(root, padding=20)
    container.pack(fill="both", expand=True)
    container.columnconfigure(0, weight=1)
    container.columnconfigure(1, weight=1)
    container.rowconfigure(0, weight=1)
    container.rowconfigure(1, weight=1)
    container.rowconfigure(2, weight=1)
    container.rowconfigure(3, weight=1)
    container.rowconfigure(4, weight=1)
    container.rowconfigure(5, weight=1)
    container.rowconfigure(6, weight=1)
    return container


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
        if check_cancel and cancel_sorting:
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


def args_tri(src_folder, dst_folder, do_convert, total_files, file_list):
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


def tri(
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


def build_gui(root, container):
    """
    Builds the gui. This function is only used when the script is run without command line arguments.
    Set all the widgets to the container and binds the events.
    Creates the sorting operation and starts it when the start button is clicked.

    Args:
        root (ThemedTk): The root window.
        container (Frame): The container for the widgets.
    """
    src_button = ttk.Button(
        container,
        text="Sélectionner le dossier source",
        command=lambda: select_folder(src_var),
    )
    src_button.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

    src_var = tk.StringVar()
    src_var.set("Aucun dossier sélectionné")
    src_entry = ttk.Entry(container, textvariable=src_var, state="readonly")
    src_entry.grid(row=0, column=1, sticky="nsew", pady=(0, 10), padx=(0, 10))

    dst_button = ttk.Button(
        container,
        text="Sélectionner le dossier de destination",
        command=lambda: select_folder(dst_var),
    )
    dst_button.grid(row=1, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10))

    dst_var = tk.StringVar()
    dst_var.set("Aucun dossier sélectionné")
    dst_entry = ttk.Entry(container, textvariable=dst_var, state="readonly")
    dst_entry.grid(row=1, column=1, sticky="nsew", pady=(0, 10), padx=(0, 10))

    def dis():
        dst_entry.configure(state="readonly" if same_dir.get() else "disabled")
        dst_button.configure(state="normal" if same_dir.get() else "disabled")

    same_dir = tk.BooleanVar(value=False)
    same_dir_check = ttk.Checkbutton(
        container, text="Trier dans le même dossier", variable=same_dir
    )
    same_dir_check.grid(row=2, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10))
    same_dir_check.bind("<Button-1>", lambda event: dis())

    convert_var = tk.BooleanVar(value=True)
    convert_check = ttk.Checkbutton(
        container, text="Convertir les images JXR", variable=convert_var
    )
    convert_check.grid(row=3, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10))

    def sort():
        if same_dir.get():
            dst_var.set(src_var.get())
        start_sorting(src_var.get(), dst_var.get(), convert_var.get())

    start_button = ttk.Button(
        container,
        text="Démarrer le tri",
        command=lambda: sort()
        if start_button["text"] == "Démarrer le tri"
        else cancel_sorting_operation(),
    )
    start_button.grid(row=4, column=1, sticky="nsew", pady=(0, 10), padx=(0, 10))

    progress_bar = ttk.Progressbar(container, orient="horizontal", mode="determinate")
    progress_bar.grid(
        row=5, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10), columnspan=2
    )
    progress_label = ttk.Label(container, text="")
    progress_label.grid(
        row=6, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10), columnspan=2
    )

    widgets = [
        src_button,
        src_entry,
        dst_button,
        dst_entry,
        same_dir_check,
        convert_check,
    ]

    def update_progress_bar(
        current_value, max_value, elapsed_time, estimated_time_remaining
    ):
        progress_bar["maximum"] = max_value
        progress_bar["value"] = current_value
        progress_label[
            "text"
        ] = f"Traités : {current_value}/{max_value} | Temps écoulé : {elapsed_time:.2f} s | ETA : {estimated_time_remaining:.2f} s"
        progress_bar.update()

    saved_states = {}

    def save_widget_states(widgets):
        for widget in widgets:
            saved_states[widget] = widget["state"]
        return saved_states

    def restore_widget_states(widgets, saved_states):
        for widget in widgets:
            widget.configure(state=saved_states[widget])
            same_dir_check.bind("<Button-1>", lambda event: dis())

    def set_widget_state(widgets, state):
        for widget in widgets:
            widget.configure(state=state)
            same_dir_check.bind("<Button-1>", lambda event: None)

    def cancel_sorting_operation():
        global cancel_sorting
        cancel_sorting = True
        start_button.configure(text="Démarrer le tri", command=lambda: sort())
        restore_widget_states(widgets, saved_states)

    def start_sorting(src_folder, dst_folder, do_convert):
        global cancel_sorting
        cancel_sorting = False

        if not os.path.exists(src_folder):
            messagebox.showerror("Erreur", "Le dossier source n'existe pas.")
            return

        if not os.path.exists(dst_folder):
            messagebox.showerror("Erreur", "Le dossier de destination n'existe pas.")
            return

        file_list = [
            entry
            for entry in os.scandir(src_folder)
            if entry.is_file()
            and not entry.name.startswith(".")
            and entry.name != "desktop.ini"
        ]
        total_files = len(file_list)
        if total_files == 0:
            messagebox.showerror(
                "Erreur", "Le dossier source ne contient pas d'images à trier."
            )
            return

        root.title("Tri en cours...")
        start_button.configure(
            text="Annuler", command=lambda: cancel_sorting_operation()
        )

        saved_states = save_widget_states(widgets)
        set_widget_state(widgets, "disabled")

        tri(
            src_folder,
            dst_folder,
            do_convert,
            update_progress_bar,
            total_files,
            file_list,
        )

        restore_widget_states(widgets, saved_states)
        root.title("Organisateur de fichiers")
        start_button.configure(text="Démarrer le tri")

        if cancel_sorting:
            messagebox.showinfo("Annulé", "Le tri des fichiers a été annulé.")
        else:
            messagebox.showinfo("Terminé", "Le tri des fichiers est terminé !")


def start_args_sorting(src_folder, dst_folder, do_convert):
    if not os.path.exists(src_folder):
        print(Fore.RED + "Erreur ❌ Le dossier source n'existe pas." + Style.RESET_ALL)
        return

    if not os.path.exists(dst_folder):
        print(
            Fore.RED
            + "Erreur ❌ Le dossier de destination n'existe pas."
            + Style.RESET_ALL
        )
        return

    file_list = [
        entry
        for entry in os.scandir(src_folder)
        if entry.is_file()
        and not entry.name.startswith(".")
        and entry.name != "desktop.ini"
    ]
    total_files = len(file_list)
    if total_files == 0:
        print(
            Fore.RED
            + "Erreur ❌ Le dossier source ne contient pas d'images à trier."
            + Style.RESET_ALL
        )
        return

    print(Fore.YELLOW + "Tri en cours..." + Style.RESET_ALL)

    args_tri(
        src_folder,
        dst_folder,
        do_convert,
        total_files,
        file_list,
    )
    print(Fore.GREEN + "Le tri des fichiers est terminé !" + Style.RESET_ALL)


def main():
    """
    Handles the command line arguments and starts the gui or the sorting operation.
    Calls the start_args_sorting function if the script is run with command line arguments.
    Calls the build_gui function if the script is run without command line arguments.
    """
    args = parse_args()

    if args:
        if args.same_folder:
            if args.dst:
                print(
                    Fore.RED
                    + "Erreur ❌ Le chemin du dossier de destination ne doit pas être fourni."
                    + Style.RESET_ALL
                )
            if args.src:
                args.dst = args.src
            else:
                print(
                    Fore.RED
                    + "Erreur ❌ Le chemin du dossier source doit être fourni."
                    + Style.RESET_ALL
                )
                print(
                    Fore.YELLOW
                    + 'Exemple : python main.py --src "C:\\Users\\User\\Pictures\\Screenshots" --same_folder'
                    + Style.RESET_ALL
                )
                return
        if args.src and args.dst:
            start_args_sorting(args.src, args.dst, args.convert)
        else:
            print(
                Fore.RED
                + "Erreur ❌ Les chemins des dossiers source et de destination doivent être fournis."
                + Style.RESET_ALL
            )
            print(
                Fore.YELLOW
                + 'Exemple : python main.py --src "C:\\Users\\User\\Pictures\\Screenshots" --dst "C:\\Users\\User\\Pictures\\Sorted Screenshots"'
                + Style.RESET_ALL
            )
    else:
        root = ThemedTk(theme="arc")
        create_main_window(root)
        container = create_container(root)
        build_gui(root, container)
        root.mainloop()


if __name__ == "__main__":
    main()
