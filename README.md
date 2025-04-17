# Drone Video to 3D Blender Plugin

A Blender plugin that converts drone videos into georeferenced 3D models using GPS metadata and GPU (CUDA) acceleration.

## Overview

This plugin integrates video processing, GPS metadata extraction, and photogrammetry pipelines directly into Blender, allowing you to create accurate 3D models from drone footage with minimal effort. By leveraging the GPS data captured by most modern drones, the plugin can create properly scaled and georeferenced 3D reconstructions.

*Note: The UI screenshot will be added once the first version is released.*

## Key Features

- **Frame Extraction**: Extract high-quality frames from drone videos using FFmpeg
- **GPS Metadata Processing**: Extract and process GPS coordinates from video metadata
- **Coordinate Conversion**: Convert GPS coordinates to cartesian coordinates for accurate scaling
- **Multiple Photogrammetry Options**: Integrate with COLMAP or Meshroom pipelines
- **GPU Acceleration**: Utilize CUDA for faster processing when available
- **Georeferenced Export**: Export 3D models with proper geographic metadata
- **User-Friendly Interface**: All functionality accessible through a clean Blender UI

## Installation

### Prerequisites

- Blender 3.0+
- Python 3.9+
- FFmpeg
- ExifTool
- COLMAP and/or Meshroom
- CUDA-capable GPU (recommended but not required)

### Installation Steps

1. Download the latest release ZIP file from the [Releases page](https://github.com/mauriale/blender-drone-video-to-3d/releases)
2. In Blender, go to Edit > Preferences > Add-ons > Install
3. Select the downloaded ZIP file and click "Install Add-on"
4. Enable the add-on by checking the box next to "Drone Video to 3D"

### Getting the Code

You can clone this repository using git:

```bash
git clone https://github.com/mauriale/blender-drone-video-to-3d.git
cd blender-drone-video-to-3d
```

Or download the code as a ZIP file from GitHub by clicking the "Code" button and selecting "Download ZIP".

### Building the Plugin

There are two ways to build the plugin:

#### Option 1: Standard Build (Dependencies Need to be Installed Separately)

```bash
python setup.py --package
```

This will create a `drone_video_to_3d.zip` file. When you install this in Blender, you'll need to make sure all dependencies (pyproj, numpy, etc.) are installed in Blender's Python environment.

#### Option 2: Bundled Build (Dependencies Included)

```bash
python setup.py --bundle
```

This creates a standalone ZIP with all dependencies bundled inside the plugin. This is the recommended method, as it avoids dependency issues with Blender's Python environment.

### Troubleshooting Dependency Issues

If you encounter `No module named 'pyproj'` or similar errors in Blender:

1. Use the bundled build option above, which includes all dependencies
2. Or, install dependencies directly into Blender's Python:

```bash
/path/to/blender/python/bin/python -m pip install pyproj numpy
```

## Quick Start Guide

1. **Prepare**: Capture drone video with GPS data enabled
2. **Extract Frames**: Import your video and extract frames 
3. **Extract GPS**: Process the GPS metadata from your video
4. **Run Photogrammetry**: Generate a 3D model using your preferred pipeline
5. **Import & Refine**: Import the resulting model into Blender and refine as needed
6. **Export**: Export your final model with proper georeferencing

For detailed usage instructions, please see the [Usage Documentation](USAGE.md).

## Why Use This Plugin?

- **Streamlined Workflow**: Perform the entire process within Blender
- **GPS Integration**: Better accuracy with GPS-guided photogrammetry
- **Scale Accuracy**: Properly scaled models based on real-world coordinates
- **GPU Acceleration**: Faster processing with CUDA support
- **Flexibility**: Multiple quality options and photogrammetry pipelines

## Technical Details

### GPS Processing

The plugin extracts GPS metadata (latitude, longitude, altitude) from drone videos and converts them to cartesian coordinates for accurate scaling and positioning. This significantly improves the quality of the 3D reconstruction by providing reliable initial camera poses.

### Photogrammetry Integration

The plugin supports both COLMAP and Meshroom (AliceVision) photogrammetry pipelines:

- **COLMAP**: Excellent for detailed, high-quality reconstructions
- **Meshroom**: User-friendly and works well with consumer-grade hardware

### CUDA Acceleration

When a compatible NVIDIA GPU is available, the plugin can utilize CUDA for:

- Faster image preprocessing
- Accelerated feature extraction and matching
- Improved dense reconstruction

### Bundled Dependencies

The plugin can be built with dependencies included, which simplifies installation and avoids dependency issues with Blender's Python environment. The bundled dependencies include:

- pyproj (for GPS coordinate transformation)
- numpy (for numerical computations)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The FFmpeg team for their excellent video processing library
- COLMAP and Meshroom/AliceVision teams for their photogrammetry software
- The Blender Foundation for an amazing 3D creation suite
