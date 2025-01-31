import os
import re

def create_structure(tree_str):
    """
    Given a tree-like string (with inline comments starting with '//'),
    create the corresponding directory and file structure.
    
    The function uses a regex to remove tree-drawing characters (e.g., │, ├──, └──)
    and to compute the nesting (depth) level.
    
    Note: This code assumes that every indent level is represented by exactly 4 characters,
    either "│   " or "    ".
    """
    # The regex explanation:
    # 1. (?P<indent>(?:(?:│   )|(?:    ))*) matches zero or more indent groups (each exactly 4 characters)
    # 2. (?P<marker>(?:├── |└── ))? matches an optional tree marker.
    # 3. (?P<name>.+?) lazily matches the file or folder name.
    # 4. (?:\s*//.*)? ignores any inline comment that starts with '//' and trailing spaces.
    pattern = re.compile(
        r'^(?P<indent>(?:(?:│   )|(?:    ))*)(?P<marker>(?:├── |└── ))?(?P<name>.+?)(?:\s*//.*)?$'
    )
    
    # Stack will hold the full directory path at each depth level.
    stack = []
    
    for line in tree_str.splitlines():
        line = line.rstrip()  # Remove trailing whitespace.
        if not line:
            continue
        
        match = pattern.match(line)
        if not match:
            # Skip lines that don't match the expected format.
            continue
        
        indent = match.group('indent')
        marker = match.group('marker')
        name = match.group('name').strip()  # Remove any extra spaces around the name.
        
        # Determine the depth (nesting level):
        # - The root line has no marker and is at depth 0.
        # - For lines with a marker, the depth is: (number of indent groups) + 1.
        indent_level = len(indent) // 4
        depth = indent_level + 1 if marker else indent_level
        
        # Build the full path.
        if depth == 0:
            # This is the root (for example, "agar-clone/")
            current_path = name
        else:
            # Its parent is the directory stored at stack[depth - 1]
            parent = stack[depth - 1]
            current_path = os.path.join(parent, name)
        
        # If the name ends with a slash, treat it as a directory.
        if name.endswith('/'):
            os.makedirs(current_path, exist_ok=True)
            # Update the stack for this depth.
            if len(stack) > depth:
                stack[depth] = current_path
            else:
                stack.append(current_path)
        else:
            # For files, ensure that the parent directory exists.
            parent_dir = os.path.dirname(current_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            # Create an empty file.
            with open(current_path, 'w') as f:
                pass

    print("Folder and file structure created successfully.")

if __name__ == '__main__':
    tree_structure = """agar-clone/
├── client/
│   ├── index.html       // Main HTML file
│   ├── main.js          // Client-side game logic and rendering
│   ├── style.css        // Basic styling for the canvas
│   └── assets/          // (Optional) images, sounds, etc.
│       ├── images/
│       └── sounds/
├── server/
│   ├── index.js         // Entry point for the Node.js server
│   ├── game.js          // Main game loop and world management
│   ├── player.js         // Player class and input handling
│   ├── cell.js          // Cell class (player cell objects)
│   ├── virus.js         // Virus class (causing cell splitting)
│   ├── massEject.js     // (Optional) Ejected mass mechanic
│   └── utils.js         // Utility functions
├── shared/
│   ├── config.js        // Game configuration (world size, speeds, etc.)
│   └── constants.js     // Shared constants (colors, etc.)
├── package.json         // npm configuration and dependencies
└── README.md            // Project overview and instructions"""

    create_structure(tree_structure)
