import tkinter as tk
from tkinter import ttk

# ==========================================================
#  ITEM SELECTION DIALOG
# ==========================================================

def select_items(item_list, title="Select Items"):
    """
    Display a modal dialog containing a checkbox for each item.

    Args:
        item_list (list): List of strings to display.
        title (str): Window title.

    Returns:
        list: Zero-based indices of checked items.
    """

    result = []

    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)

    vars_ = []

    # Checkboxes
    for item in item_list:
        var = tk.BooleanVar(value=False)
        vars_.append(var)

        chk = ttk.Checkbutton(
            root,
            text=str(item),
            variable=var
        )
        chk.pack(anchor="w", padx=10, pady=2)

    def on_ok():
        nonlocal result
        result = [i for i, var in enumerate(vars_) if var.get()]
        root.destroy()

    btn = ttk.Button(root, text="OK", command=on_ok)
    btn.pack(pady=10)

    root.mainloop()

    return result


# ==========================================================
# PROJECT SELECTION DIALOG
# ==========================================================

def select_projects(
    projects,
    title="Select Bentley projects",
):
    """
    Display a checkbox dialog for Bentley projects.

    Each checkbox is labelled using the project display name.

    Parameters
    ----------
    projects : list[dict]
        Bentley iTwin/project records.

    title : str
        Dialog window title.

    Returns
    -------
    list[str]
        IDs of the selected projects.
    """

    selected_project_ids = []

    root = tk.Tk()
    root.title(title)
    root.geometry("700x600")
    root.minsize(500, 350)

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    header_frame = ttk.Frame(root)
    header_frame.pack(
        fill="x",
        padx=10,
        pady=(10, 5),
    )

    ttk.Label(
        header_frame,
        text="Select the projects to process:",
    ).pack(
        side="left",
    )

    selection_status = ttk.Label(
        header_frame,
        text="0 selected",
    )

    selection_status.pack(
        side="right",
    )

    # ------------------------------------------------------
    # SELECT ALL / NONE
    # ------------------------------------------------------

    all_selected = tk.BooleanVar(
        value=False
    )

    project_variables = []

    def update_selection_status():
        selected_count = sum(
            variable.get()
            for variable in project_variables
        )

        selection_status.config(
            text=(
                f"{selected_count} of "
                f"{len(project_variables)} selected"
            )
        )

        all_selected.set(
            bool(project_variables)
            and selected_count == len(project_variables)
        )

    def set_all_projects(selected):
        for variable in project_variables:
            variable.set(selected)

        update_selection_status()

    def toggle_all_projects():
        set_all_projects(
            all_selected.get()
        )

    controls_frame = ttk.Frame(root)
    controls_frame.pack(
        fill="x",
        padx=10,
        pady=5,
    )

    ttk.Checkbutton(
        controls_frame,
        text="All / None",
        variable=all_selected,
        command=toggle_all_projects,
    ).pack(
        side="left",
    )

    ttk.Button(
        controls_frame,
        text="Select all",
        command=lambda: set_all_projects(True),
    ).pack(
        side="left",
        padx=(15, 5),
    )

    ttk.Button(
        controls_frame,
        text="Select none",
        command=lambda: set_all_projects(False),
    ).pack(
        side="left",
        padx=5,
    )

    # ------------------------------------------------------
    # SCROLLABLE PROJECT LIST
    # ------------------------------------------------------

    list_container = ttk.Frame(root)
    list_container.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5,
    )

    canvas = tk.Canvas(
        list_container,
        highlightthickness=0,
    )

    scrollbar = ttk.Scrollbar(
        list_container,
        orient="vertical",
        command=canvas.yview,
    )

    project_frame = ttk.Frame(canvas)

    project_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(
            scrollregion=canvas.bbox("all")
        ),
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=project_frame,
        anchor="nw",
    )

    def resize_project_frame(event):
        canvas.itemconfigure(
            canvas_window,
            width=event.width,
        )

    canvas.bind(
        "<Configure>",
        resize_project_frame,
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True,
    )

    scrollbar.pack(
        side="right",
        fill="y",
    )

    # ------------------------------------------------------
    # PROJECT CHECKBOXES
    # ------------------------------------------------------

    valid_projects = []

    for project in projects:
        project_id = project.get("id")

        project_name = (
            project.get("displayName")
            or project.get("name")
            or project_id
            or "<unnamed project>"
        )

        if not project_id:
            continue

        valid_projects.append(project)

        variable = tk.BooleanVar(
            value=False
        )

        project_variables.append(variable)

        checkbox = ttk.Checkbutton(
            project_frame,
            text=str(project_name),
            variable=variable,
            command=update_selection_status,
        )

        checkbox.pack(
            anchor="w",
            fill="x",
            padx=10,
            pady=3,
        )

    # ------------------------------------------------------
    # DIALOG BUTTONS
    # ------------------------------------------------------

    def accept_selection():
        nonlocal selected_project_ids

        selected_project_ids = [
            project["id"]
            for project, variable in zip(
                valid_projects,
                project_variables,
            )
            if variable.get()
        ]

        root.destroy()

    def cancel_selection():
        nonlocal selected_project_ids

        selected_project_ids = []
        root.destroy()

    button_frame = ttk.Frame(root)
    button_frame.pack(
        fill="x",
        padx=10,
        pady=(5, 10),
    )

    ttk.Button(
        button_frame,
        text="Cancel",
        command=cancel_selection,
    ).pack(
        side="right",
        padx=(5, 0),
    )

    ttk.Button(
        button_frame,
        text="OK",
        command=accept_selection,
    ).pack(
        side="right",
    )

    root.protocol(
        "WM_DELETE_WINDOW",
        cancel_selection,
    )

    update_selection_status()

    root.mainloop()

    return selected_project_ids
