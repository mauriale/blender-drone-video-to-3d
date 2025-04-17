#!/usr/bin/env python

import os
import zipfile
import shutil
import sys
import subprocess
import importlib.util

def create_addon_zip():
    """Create a ZIP file of the Blender add-on for installation"""
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the addon directory and files to include
    addon_dir = os.path.join(current_dir, 'drone_video_to_3d')
    zip_name = os.path.join(current_dir, 'drone_video_to_3d.zip')
    
    # Check if the addon directory exists
    if not os.path.exists(addon_dir):
        print(f"Error: Add-on directory '{addon_dir}' not found.")
        return False
    
    # Create ZIP file
    try:
        print(f"Creating add-on ZIP file: {zip_name}")
        
        # Remove existing ZIP if it exists
        if os.path.exists(zip_name):
            os.remove(zip_name)
        
        # Create the ZIP file
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add files from addon directory
            for root, dirs, files in os.walk(addon_dir):
                for file in files:
                    if file.endswith('.py') or file.endswith('.md') or file.endswith('.txt'):
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, current_dir)
                        print(f"Adding {arc_name}")
                        zipf.write(file_path, arc_name)
            
            # Add README.md to the root of the ZIP
            readme_path = os.path.join(current_dir, 'README.md')
            if os.path.exists(readme_path):
                print(f"Adding README.md")
                zipf.write(readme_path, os.path.join('drone_video_to_3d', 'README.md'))
        
        print(f"Add-on ZIP file created successfully: {zip_name}")
        return True
    
    except Exception as e:
        print(f"Error creating ZIP file: {str(e)}")
        return False

def install_dependencies(user_mode=False):
    """Install Python dependencies required by the add-on"""
    
    dependencies = [
        'pyproj',
        'numpy',
        'opencv-contrib-python-headless',
    ]
    
    print("Installing Python dependencies...")
    
    for package in dependencies:
        try:
            print(f"Installing {package}...")
            if user_mode:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', package])
            else:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {str(e)}")
            print("Trying with --user flag...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', package])
            except subprocess.CalledProcessError as e2:
                print(f"Still failed: {str(e2)}")
                return False
    
    print("Python dependencies installed successfully.")
    return True

def prepare_bundled_addon():
    """Prepare a bundled version of the addon with all dependencies included"""
    # Check if we have the prepare_bundle.py script
    if not os.path.exists('prepare_bundle.py'):
        print("Error: prepare_bundle.py script not found.")
        return False
    
    try:
        print("Preparing bundled version of the addon...")
        subprocess.check_call([sys.executable, 'prepare_bundle.py'])
        print("Bundled addon preparation completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error preparing bundled addon: {str(e)}")
        return False

if __name__ == '__main__':
    # Parse arguments
    user_mode = '--user' in sys.argv
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--install-deps':
            install_dependencies(user_mode)
        elif sys.argv[1] == '--package':
            create_addon_zip()
        elif sys.argv[1] == '--bundle':
            prepare_bundled_addon()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Available options:")
            print("  --install-deps  Install Python dependencies")
            print("  --package       Create the add-on ZIP file")
            print("  --bundle        Create bundled version with dependencies included")
            print("Add --user to install dependencies in user mode")
    else:
        # If no arguments given, suggest the bundle option
        print("No arguments provided. Suggested usage:")
        print("  python setup.py --bundle   Create a bundled version with dependencies included")
        print("  python setup.py --install-deps  Install dependencies (add --user if permission denied)")
        print("  python setup.py --package   Create addon ZIP (without bundled dependencies)")
