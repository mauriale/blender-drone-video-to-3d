# Drone Video to 3D Blender Plugin

A Blender plugin that converts drone videos into georeferenced 3D models using GPS metadata and GPU (CUDA) acceleration.

## Features

- Extract frames and GPS metadata from drone videos
- Georeference frames using GPS coordinates
- Integrate with photogrammetry pipelines (COLMAP/Meshroom)
- GPU acceleration using CUDA
- User-friendly Blender interface

## Installation

1. Download the latest release from the GitHub repository
2. In Blender, go to Edit > Preferences > Add-ons > Install
3. Select the downloaded ZIP file and click "Install Add-on"
4. Enable the add-on by checking the box next to it

## Requirements

- Blender 3.0+
- Python 3.9+
- CUDA-capable GPU (for acceleration)
- FFmpeg
- ExifTool

## Dependencies

- pyexiftool
- pyproj
- opencv-contrib-python-headless (with CUDA)
- folium/plotly (for map visualization)

## License

MIT
