import argparse
import sys
import os
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


def start_args_sorting(src_folder, dst_folder, do_convert):
    """
    Starts the sorting operation, only used when the script is run with command line arguments.

    Args:
        src_folder (_type_): _description_
        dst_folder (_type_): _description_
        do_convert (_type_): _description_
    """
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

    start_args_sorting(
        src_folder,
        dst_folder,
        do_convert,
        total_files,
        file_list,
    )
    print(Fore.GREEN + "Le tri des fichiers est terminé !" + Style.RESET_ALL)


def check_args(args):
    """
    Checks if the command line arguments are valid and starts the sorting operation if they are.

    Args:
        args (argparse.Namespace): The parsed command line arguments.
    """
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