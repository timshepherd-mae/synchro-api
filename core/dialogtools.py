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

select_items(["Item 1", "Item 2", "Item 3"], title="Select Items")

