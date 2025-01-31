import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

def create_structure(tree_str, base_dir):
    """
    Given a tree-like string (with inline comments starting with '//') and a base directory,
    create the corresponding directory and file structure.
    
    The function uses a regex to remove tree-drawing characters (e.g., │, ├──, └──)
    and to compute the nesting (depth) level.
    
    Note: This code assumes that every indent level is represented by exactly 4 characters,
    either "│   " or "    ".
    """
    # Regex explanation:
    #   - (?P<indent>(?:(?:│   )|(?:    ))*) matches zero or more indent groups (each exactly 4 characters)
    #   - (?P<marker>(?:├── |└── ))? matches an optional tree marker.
    #   - (?P<name>.+?) lazily matches the file or folder name.
    #   - (?:\s*//.*)? ignores any inline comment that starts with '//' and trailing spaces.
    pattern = re.compile(
        r'^(?P<indent>(?:(?:│   )|(?:    ))*)(?P<marker>(?:├── |└── ))?(?P<name>.+?)(?:\s*//.*)?$'
    )
    
    # This stack will hold the full path at each depth level.
    stack = []
    
    for line in tree_str.splitlines():
        line = line.rstrip()  # Remove trailing whitespace.
        if not line:
            continue
        
        match = pattern.match(line)
        if not match:
            # If a line doesn't match, skip it.
            continue
        
        indent = match.group('indent')
        marker = match.group('marker')
        name = match.group('name').strip()  # Remove any extra spaces around the name.
        
        # Determine the nesting level.
        # - The root line (with no marker) is at depth 0.
        # - For lines with a marker, depth is: (number of indent groups) + 1.
        indent_level = len(indent) // 4
        depth = indent_level + 1 if marker else indent_level
        
        # Build the full path.
        if depth == 0:
            # For the root, join with the base directory.
            current_path = os.path.join(base_dir, name)
        else:
            # The parent is stored at stack[depth - 1]
            parent = stack[depth - 1]
            current_path = os.path.join(parent, name)
        
        # Create directory if name ends with a slash, else create an empty file.
        if name.endswith('/'):
            os.makedirs(current_path, exist_ok=True)
            # Update the stack at the current depth.
            if len(stack) > depth:
                stack[depth] = current_path
            else:
                stack.append(current_path)
        else:
            # For files, ensure the parent directory exists.
            parent_dir = os.path.dirname(current_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            # Create an empty file.
            with open(current_path, 'w') as f:
                pass

    return "Folder and file structure created successfully."

# --- Tkinter Application ---

def select_base_directory():
    """Open a dialog to select a target folder, update the entry widget with the selected path."""
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        base_dir_var.set(selected_dir)

def on_create_structure():
    """Callback when the 'Create Structure' button is clicked."""
    tree_data = text_input.get("1.0", tk.END).strip()
    if not tree_data:
        messagebox.showerror("Error", "Please enter the tree structure data.")
        return

    base_dir = base_dir_var.get()
    if not base_dir:
        base_dir = os.getcwd()  # Use current directory if none selected

    try:
        result = create_structure(tree_data, base_dir)
        messagebox.showinfo("Success", result)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window.
root = tk.Tk()
root.title("Folder & File Structure Creator")

# Variables.
base_dir_var = tk.StringVar(value=os.getcwd())

# Layout.
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

# Label for instructions.
instruction_label = tk.Label(frame, text="Paste your tree structure data below (comments starting with // are ignored):")
instruction_label.pack(anchor='w')

# Text widget for tree structure input.
text_input = tk.Text(frame, width=80, height=20)
text_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

# Frame for base directory selection.
dir_frame = tk.Frame(frame)
dir_frame.pack(fill=tk.X, pady=(0, 10))
tk.Label(dir_frame, text="Target Directory:").pack(side=tk.LEFT)
dir_entry = tk.Entry(dir_frame, textvariable=base_dir_var, width=60)
dir_entry.pack(side=tk.LEFT, padx=(5, 0))
select_button = tk.Button(dir_frame, text="Select...", command=select_base_directory)
select_button.pack(side=tk.LEFT, padx=(5, 0))

# Create Structure button.
create_button = tk.Button(frame, text="Create Structure", command=on_create_structure)
create_button.pack()

# Start the GUI event loop.
root.mainloop()
