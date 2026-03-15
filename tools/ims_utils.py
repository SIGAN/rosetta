"""
IMS Utility Functions

Shared utility functions used across IMS CLI tools.
"""

from pathlib import Path


def get_workspace_root() -> Path:
    """
    Get the workspace root directory by searching for .git folder.
    
    Searches upward from both the script location and current working directory
    to find the git root.
    
    Returns:
        Path to workspace root (git root directory)
    
    Examples:
        >>> root = get_workspace_root()
        >>> print(root)
        /Users/username/project
    """
    # Strategy 1: Search upward from script's actual location
    # This ensures we find git root even if script is deep in subdirectories
    try:
        current = Path(__file__).parent.resolve()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
    except (NameError, OSError):
        # __file__ may not be available in some contexts
        pass
    
    # Strategy 2: Search upward from current working directory
    # Fallback in case script location doesn't lead to git root
    current = Path.cwd().resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    
    # Last resort: return current directory
    return Path.cwd().resolve()
