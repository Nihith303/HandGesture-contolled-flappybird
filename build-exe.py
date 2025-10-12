import PyInstaller.__main__
import os

# Get the current directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Data files to include (images, etc.)
data_files = [
    (os.path.join(base_dir, 'images'), 'images'),
    (os.path.join(base_dir, '.env'), '.')  # Include .env file if it exists
]

# Add data files to the command
add_data = []
for src, dst in data_files:
    if os.path.exists(src):
        add_data.extend(['--add-data', f'{os.path.normpath(src)}{os.pathsep}{dst}'])

# PyInstaller configuration
PyInstaller.__main__.run([
    'game.py',
    '--name=HandGestureFlappyBird',
    '--onefile',
    '--windowed',  # Prevents console window from appearing
    '--icon=images/bird.png',  # Using the existing bird.png file
    *add_data,
    '--clean',
    '--noconfirm'
])
