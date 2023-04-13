import os
import subprocess
import re
import time
import threading
import tkinter as tk
from unidecode import unidecode
from collections import Counter
from tkinter import filedialog, messagebox, ttk
from ttkthemes import ThemedTk

def clean_filename(filename):
    cleaned_filename = filename
    
    # Supprimer les dates, la version, les parenthèses et les tirets entourés d'espaces en une seule étape
    cleaned_filename = re.sub(r'(\s*\d{1,2}_\d{1,2}_\d{4}\s*$)|(\s*-\s*\d+\.\d+\.\d+\.\d+\s*\(.*?\)\s*)|(\s-.*)|(Screenshot.*)', '', cleaned_filename).strip()

    # Supprimer les underscores et espaces multiples
    cleaned_filename = cleaned_filename.replace('_', '').replace('  ', ' ')

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

        cleaned_common_part = clean_filename(common_part)

        common_parts.append(cleaned_common_part)

    return common_parts

def find_game_name(filename, common_parts):
    cleaned_filename = clean_filename(filename)
    
    # Vérifie si le nom du fichier commence par "Ce PC", "Photos" ou "Screenshot"
    if any(cleaned_filename.startswith(s) for s in ["Ce PC", "Photos", "Screenshot"]):
        return "Default"

    for game_name in common_parts:
        if game_name in cleaned_filename:
            return game_name

    return "Default"

def create_folder_structure(base_folder, folder_name):
    for subfolder in ["JXR", "PNG", "Conv"]:
        path = os.path.join(base_folder, folder_name, subfolder)
        if not os.path.exists(path):
            os.makedirs(path)

def select_folder(var):
    folder_path = filedialog.askdirectory()
    if folder_path != "":
        var.set(folder_path)
    else: var.set("Aucun dossier sélectionné")

def create_main_window(root):
    root.title("Organisateur de fichiers")
    root.tk.call('lappend', 'auto_path', './awthemes-10.4.0')
    root.tk.call('package', 'require', 'awdark')
    root.tk.call("::themeutils::setThemeColors", "arc",
                 "style.progressbar", "rounded-line",
                 "style.scale", "circle-rev",
                 "style.scrollbar-grip", "none",
                 "scrollbar.has.arrows", "false")
    style = ttk.Style()
    style.theme_use("awdark")
    style.configure("TProgressbar", background='green', troughcolor='grey')

def create_container(root):
    container = ttk.Frame(root, padding=20)
    container.pack(fill="both", expand=True)
    for i in range(2):
        container.columnconfigure(i, weight=1)
    for i in range(7):
        container.rowconfigure(i, weight=1)
    return container

def main():
    root = ThemedTk(theme="arc")
    create_main_window(root)
    container = create_container(root)
    
    # Ajouter un bouton pour sélectionner le dossier source
    src_button = ttk.Button(container, text="Sélectionner le dossier source", command=lambda: select_folder(src_var))
    src_button.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

    # Ajouter un champ de texte pour afficher le dossier source sélectionné
    src_var = tk.StringVar()
    src_var.set("Aucun dossier sélectionné")
    src_entry = ttk.Entry(container, textvariable=src_var, state="readonly")
    src_entry.grid(row=0, column=1, sticky="nsew", pady=(0, 10), padx=(0, 10))

    # Ajouter un bouton pour sélectionner le dossier de destination
    dst_button = ttk.Button(container, text="Sélectionner le dossier de destination", command=lambda: select_folder(dst_var))
    dst_button.grid(row=1, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10))

    # Ajouter un champ de texte pour afficher le dossier de destination sélectionné
    dst_var = tk.StringVar()
    dst_var.set("Aucun dossier sélectionné")
    dst_entry = ttk.Entry(container, textvariable=dst_var, state="readonly")
    dst_entry.grid(row=1, column=1, sticky="nsew", pady=(0, 10), padx=(0, 10))

    def dis():
        dst_entry.configure(state="readonly" if same_dir.get() else "disabled") 
        dst_button.configure(state="normal" if same_dir.get() else "disabled")

    # Ajouter une case à cocher pour trier dans le même dossier
    same_dir = tk.BooleanVar(value=False)
    same_dir_check = ttk.Checkbutton(container, text="Trier dans le même dossier", variable=same_dir)
    same_dir_check.grid(row=2, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10))
    same_dir_check.bind("<Button-1>", lambda event: dis())

    # Ajouter une case à cocher pour désactiver la conversion des images
    convert_var = tk.BooleanVar(value=True)
    convert_check = ttk.Checkbutton(container, text="Convertir les images JXR", variable=convert_var)
    convert_check.grid(row=3, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10))

    def sort():
        if same_dir.get():
            dst_var.set(src_var.get())
        start_sorting(src_var.get(), dst_var.get(), convert_var.get())

    # Ajouter un bouton pour lancer le tri des fichiers
    start_button = ttk.Button(container, text="Démarrer le tri", command=lambda: sort() if start_button["text"] == "Démarrer le tri" else cancel_sorting_operation())
    start_button.grid(row=4, column=1, sticky="nsew", pady=(0, 10), padx=(0, 10))

    # Ajouter une barre de progression pour le tri des fichiers
    progress_bar = ttk.Progressbar(container, orient="horizontal", mode="determinate")
    progress_bar.grid(row=5, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10), columnspan=2)
    progress_label = ttk.Label(container, text="")
    progress_label.grid(row=6, column=0, sticky="nsew", pady=(0, 10), padx=(0, 10), columnspan=2)

    widgets = [src_button, src_entry, dst_button, dst_entry, same_dir_check, convert_check]

    def update_progress_bar(current_value, max_value, elapsed_time, estimated_time_remaining):
        progress_bar["maximum"] = max_value
        progress_bar["value"] = current_value
        progress_label["text"] = f"Traités : {current_value}/{max_value} | Temps écoulé : {elapsed_time:.2f} s | ETA : {estimated_time_remaining:.2f} s"
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
        
        
    max_threads = 1
    semaphore = threading.Semaphore(max_threads)


    def execute_hdrfix(dst_path, conv_path):
        semaphore.acquire()
        subprocess.call(['hdrfix.exe', dst_path, conv_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        semaphore.release()


    # Ajouter une fonction pour lancer le tri des fichiers
    def start_sorting(src_folder, dst_folder, do_convert):
        global cancel_sorting
        cancel_sorting = False
        # Vérifier si les dossiers source et destination existent
        if not os.path.exists(src_folder):
            messagebox.showerror("Erreur", "Le dossier source n'existe pas.")
            return

        if not os.path.exists(dst_folder):
            messagebox.showerror("Erreur", "Le dossier de destination n'existe pas.")
            return

        # Vérifier si le dossier source est vide
        total_files = len(os.listdir(src_folder))
        current_file = 0
        if total_files == 0:
            messagebox.showerror("Erreur", "Le dossier source est vide.")
            return
        
        root.title("Tri en cours...")
        start_button.configure(text="Annuler", command=lambda: cancel_sorting_operation())
        
        #Ajouter une indication que le programme est en train de travailler, et que l'utilisateur doit patienter, vérouiller les boutons, etc.
        saved_states = save_widget_states(widgets)
        set_widget_state(widgets, "disabled")

        # Recherche des noms de jeux communs
        common_part = common_filename_part(src_folder)

        # Tri des fichiers par nom de jeu
        start_time = time.time()
        for filename in os.listdir(src_folder):
            # Vérifiez si l'utilisateur a demandé d'annuler le tri à la fin de chaque itération
            if cancel_sorting:
                break
            
            # Récupération de l'extension du fichier
            file_ext = os.path.splitext(filename)[1].lower()[1:]

            # Recherche du nom de jeu dans le nom du fichier
            game_name = find_game_name(filename, common_part)

            # Création des dossiers nécessaires
            create_folder_structure(dst_folder, game_name)

            # Déplacement du fichier vers le dossier correspondant
            src_path = os.path.join(src_folder, filename)
            dst_path = os.path.join(dst_folder, game_name, file_ext.upper(), filename)

            if file_ext in ["jxr", "png"]:
                os.rename(src_path, dst_path)

                if file_ext == "jxr" and do_convert:
                    conv_path = os.path.join(dst_folder, game_name, "Conv", os.path.splitext(filename)[0] + '-sdr.png')
                    hdrfix_thread = threading.Thread(target=execute_hdrfix, args=(dst_path, conv_path))
                    hdrfix_thread.start()

            current_file += 1
            elapsed_time = time.time() - start_time
            estimated_time_remaining = (elapsed_time / current_file) * (total_files - current_file)
            update_progress_bar(current_file, total_files, elapsed_time, estimated_time_remaining)

        restore_widget_states(widgets, saved_states)
        root.title("Organisateur de fichiers") 
        start_button.configure(text="Démarrer le tri")
        
        # Afficher un message de fin
        if cancel_sorting: messagebox.showinfo("Annulé", "Le tri des fichiers a été annulé.")
        else: messagebox.showinfo("Terminé", "Le tri des fichiers est terminé !")

    # Afficher la fenêtre principale
    root.mainloop()


if __name__ == "__main__":
    main()