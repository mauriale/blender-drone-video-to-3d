bl_info = {
    "name": "Drone Video to 3D",
    "author": "Mauriale",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Drone Video to 3D",
    "description": "Convert drone videos into georeferenced 3D models using GPS metadata and GPU acceleration",
    "warning": "Requires external dependencies",
    "doc_url": "https://github.com/mauriale/blender-drone-video-to-3d",
    "category": "3D View",
}

import bpy
import importlib
import sys
import os

# Add lib directory to path for bundled dependencies
file_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(file_dir, "lib")
if os.path.exists(lib_dir) and lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

# Import the modules
from . import ui
from . import operators
from . import properties

# Reload modules when the add-on is reloaded
if "ui" in locals():
    importlib.reload(ui)
if "operators" in locals():
    importlib.reload(operators)
if "properties" in locals():
    importlib.reload(properties)

def register():
    properties.register()
    operators.register()
    ui.register()
    
def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()
    
if __name__ == "__main__":
    register()
