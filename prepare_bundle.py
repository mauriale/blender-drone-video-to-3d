#!/usr/bin/env python

import os
import sys
import subprocess
import shutil
import zipfile
import platform
import tempfile
import site
import importlib.util

# Define the dependencies we need to bundle
DEPENDENCIES = [
    "pyproj",
    "numpy",
]

def get_python_executable():
    """Get the current Python executable path"""
    return sys.executable

def create_lib_directory():
    """Create lib directory if it doesn't exist"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = os.path.join(current_dir, 'drone_video_to_3d', 'lib')
    
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)
        
    # Create an __init__.py to make it a package
    init_file = os.path.join(lib_dir, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# Bundled dependencies package\n')
    
    return lib_dir

def install_dependencies(lib_dir):
    """Install dependencies to the lib directory"""
    python_exe = get_python_executable()
    temp_dir = tempfile.mkdtemp()
    
    print(f"Installing dependencies to: {lib_dir}")
    print(f"Using temporary directory: {temp_dir}")
    
    for package in DEPENDENCIES:
        print(f"Installing {package}...")
        try:
            # Download the package and its dependencies to a temporary directory
            subprocess.check_call([
                python_exe, '-m', 'pip', 'download',
                '--dest', temp_dir,
                '--no-deps',  # Avoid downloading dependencies of dependencies
                package
            ])
            
            # Install the downloaded package to the lib directory
            for wheel_file in os.listdir(temp_dir):
                if wheel_file.endswith('.whl') and package.lower() in wheel_file.lower():
                    wheel_path = os.path.join(temp_dir, wheel_file)
                    subprocess.check_call([
                        python_exe, '-m', 'pip', 'install',
                        '--target', lib_dir,
                        '--no-deps',
                        wheel_path
                    ])
                    os.remove(wheel_path)  # Clean up the wheel file
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            continue
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    # Create a README file explaining the bundled libraries
    with open(os.path.join(lib_dir, 'README.txt'), 'w') as f:
        f.write("Bundled Dependencies\n")
        f.write("===================\n\n")
        f.write("This directory contains Python libraries that are bundled with the Drone Video to 3D plugin.\n")
        f.write("These libraries are necessary for the plugin to function correctly.\n\n")
        f.write("Included libraries:\n")
        for package in DEPENDENCIES:
            f.write(f"- {package}\n")

def remove_unnecessary_files(lib_dir):
    """Remove unnecessary files to reduce size"""
    # Extensions that are not needed
    remove_extensions = ['.c', '.h', '.cpp', '.hpp', '.html', '.md', '.rst', '.txt']
    # Directories that are not needed
    remove_dirs = ['__pycache__', 'tests', 'test', 'docs', 'examples']
    
    for root, dirs, files in os.walk(lib_dir):
        # Remove unnecessary directories
        for dir_name in dirs[:]:
            if dir_name in remove_dirs:
                dir_path = os.path.join(root, dir_name)
                print(f"Removing directory: {dir_path}")
                try:
                    shutil.rmtree(dir_path)
                    dirs.remove(dir_name)  # Remove from list to avoid descending into it
                except Exception as e:
                    print(f"Error removing directory {dir_path}: {e}")
        
        # Remove unnecessary files
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # Check if file has an extension to remove
            _, ext = os.path.splitext(file_name)
            if ext in remove_extensions:
                print(f"Removing file: {file_path}")
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")

def create_addon_zip():
    """Create a ZIP file with the addon and bundled dependencies"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    addon_dir = os.path.join(current_dir, 'drone_video_to_3d')
    zip_name = os.path.join(current_dir, 'drone_video_to_3d.zip')
    
    print(f"Creating addon ZIP: {zip_name}")
    
    # Remove existing ZIP if it exists
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    # Create the ZIP file
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(addon_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate the relative path for the file in the ZIP
                rel_path = os.path.relpath(file_path, os.path.dirname(addon_dir))
                print(f"Adding: {rel_path}")
                zipf.write(file_path, rel_path)
    
    print(f"Addon ZIP created: {zip_name}")
    return zip_name

if __name__ == "__main__":
    # Create the lib directory
    lib_dir = create_lib_directory()
    
    # Install dependencies
    install_dependencies(lib_dir)
    
    # Remove unnecessary files to reduce size
    remove_unnecessary_files(lib_dir)
    
    # Create the addon ZIP
    zip_file = create_addon_zip()
    
    print("\nDone! The addon is now bundled with its dependencies.")
    print(f"Install the addon in Blender using the file: {zip_file}")
