import os
import subprocess
import re
from unidecode import unidecode
from collections import Counter
from tqdm import tqdm
from tkinter import filedialog, Tk
from colorama import Fore, Style

def clean_filename(filename):
    cleaned_filename = filename

    # Supprimer la version et les parenthèses
    cleaned_filename = re.sub(r'\s*-\s*\d+\.\d+\.\d+\.\d+\s*\(.*?\)\s*', '', cleaned_filename).strip()

    # Supprimer les underscores
    cleaned_filename = cleaned_filename.replace('_', '')

    # Remplacer les caractères Unicode problématiques
    cleaned_filename = unidecode(cleaned_filename)

    return cleaned_filename

def common_filename_part(folder_path):
    files = os.listdir(folder_path)

    counter = Counter([re.match(r'(.*?\D)\d', f).group(1).strip() for f in files if re.match(r'(.*?\D)\d', f)])

    common_strings = [s for s in counter.keys() if counter[s] > 2]

    common_parts = []
    for s in common_strings:
        matches = [f for f in files if f.startswith(s)]
        common_part = os.path.commonprefix(matches).rsplit(' ', 1)[0].strip()

        cleaned_common_part = re.sub(r'\s*\d{1,2}_\d{1,2}_\d{4}\s*$', '', common_part).strip()
        
        cleaned_common_part = clean_filename(cleaned_common_part)

        common_parts.append(cleaned_common_part)

    return common_parts

def find_game_name(filename, common_parts):
    cleaned_filename = clean_filename(filename)
        
    for game_name in common_parts:
        if game_name in cleaned_filename:
            return game_name
        
    return "Default"

def create_folder_structure(base_folder, folder_name):
    for subfolder in ["JXR", "PNG", "Conv"]:
        path = os.path.join(base_folder, folder_name, subfolder)
        if not os.path.exists(path):
            os.makedirs(path)

def organize_files(src_folder, dst_folder, common_parts):
    # Personnaliser l'apparence de la barre de progression
    tqdm_bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
    tqdm_kwargs = {"bar_format": tqdm_bar_format, "dynamic_ncols": True, "ncols": 100, "colour": "#00FF00"}

    # Boucle pour parcourir tous les fichiers dans le dossier source
    for filename in tqdm(os.listdir(src_folder), **tqdm_kwargs):
        # Récupération de l'extension du fichier
        file_ext = os.path.splitext(filename)[1].lower()[1:]

        # Recherche du nom de jeu dans le nom du fichier
        game_name = find_game_name(filename, common_parts)

        # Création des dossiers nécessaires
        create_folder_structure(dst_folder, game_name)

        # Déplacement du fichier vers le dossier correspondant
        src_path = os.path.join(src_folder, filename)
        dst_path = os.path.join(dst_folder, game_name, file_ext.upper(), filename)

        if file_ext in ["jxr", "png"]:
            os.rename(src_path, dst_path)

            if file_ext == "jxr":
                conv_path = os.path.join(dst_folder, game_name, "Conv", os.path.splitext(filename)[0] + '-sdr.png')
                subprocess.call(['hdrfix.exe', dst_path, conv_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def main():
    print("Bienvenue dans le programme de tri de fichiers !")
    print("Ce programme vous permet de trier automatiquement vos fichiers par nom de jeu.")
    print("Veuillez sélectionner le dossier contenant vos fichiers à trier.")
    print("---------------------------------------------------------------")
    
    root = Tk()
    root.withdraw()
    
    # Demander à l'utilisateur de sélectionner le dossier source
    src_folder = filedialog.askdirectory(title="Sélectionnez le dossier source")

    # Demander à l'utilisateur de sélectionner le dossier de destination
    dst_folder = filedialog.askdirectory(title="Sélectionnez le dossier de destination")

    # Fermer la fenêtre Tkinter
    root.destroy()

    # Vérifier si les dossiers source et destination existent
    if not os.path.exists(src_folder):
        print("Le dossier source n'existe pas.")
        return

    if not os.path.exists(dst_folder):
        print("Le dossier de destination n'existe pas.")
        return
    
    print(Fore.YELLOW + "Étape 1 : Recherche des noms de jeux communs..." + Style.RESET_ALL)
    common_part = common_filename_part(src_folder)
    print(Fore.GREEN + "Terminé !" + Style.RESET_ALL)
    
    print(Fore.YELLOW + "Étape 2 : Tri des fichiers par nom de jeu..." + Style.RESET_ALL)
    organize_files(src_folder, dst_folder, common_part)
    print(Fore.GREEN + "Terminé !" + Style.RESET_ALL)
    
if __name__ == '__main__':
    main()