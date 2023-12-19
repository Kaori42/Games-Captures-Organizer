import os
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import tkinter as tk

from folders import select_folder
from start_sorting import start_gui_sorting


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

        start_gui_sorting(
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


def load_tk():
    root = ThemedTk(theme="arc")
    create_main_window(root)
    container = create_container(root)
    build_gui(root, container)
    root.mainloop()
