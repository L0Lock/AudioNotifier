"""
Simple print coloring module.
"""

colors: dict[str, str] = {
    # Cool colors
    'Blue': '\033[94m',
    'Cyan': '\033[96m',             # Info
    'LightCyan': '\033[96m',
    'Green': '\033[92m',
    'LightGreen': '\033[92m',       # Success
    # Warm Colors
    'Yellow': '\033[38;5;226m',     # Warnings
    'LightYellow': '\033[93m',
    'Orange': '\033[38;5;214m',
    'Red': '\033[91m',              # Errors
    # Accent Colors
    'Purple': '\033[95m',
    'Magenta': '\033[35m',          # Important notes
    # Neutrals
    'Grey': '\033[0m',              # Default
    'White': '\033[1m',
    # Special Characters
    'AlertSound': '\007'
}


def printcol(color, text, alert=False):
    """Prints text with the specified color.

    Args:
        color (str): Key to get the color code from the 'flavor' dict.
        text (str): Text run through print() but with the specified color.
        aler (bool): Optional, make a sound if True.
    """
    if color in colors:
        print(f'{colors[color]}{text}{colors["Grey"]}')
        if alert:
            print(colors["AlertSound"], end='')
    else:
        print(f"Color '{color}' not found!")
        print(f"Available colors are: {', '.join(colors.keys())}")


def test_colors():
    """Prints all color codes in the module to the console for quick reference

    This is useful for testing how the colors look on a dark background and to
    quickly copy-paste the color codes into any other script.
    """
    print("Testing Colors on Dark Background:")
    for color in colors:
        printcol(color, f'{color}')


# Run the test if the file is executed directly
if __name__ == "__main__":
    test_colors()
