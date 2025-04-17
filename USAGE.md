# Drone Video to 3D - User Guide

This guide explains how to use the Drone Video to 3D Blender addon to convert drone videos into georeferenced 3D models.

## Prerequisites

Before using this addon, make sure you have the following installed:

1. **Blender 3.0+**: Download from [blender.org](https://www.blender.org/download/)
2. **FFmpeg**: Required for video processing. [Download FFmpeg](https://ffmpeg.org/download.html)
3. **ExifTool**: Required for extracting GPS metadata. [Download ExifTool](https://exiftool.org/)
4. **COLMAP** or **Meshroom**: For photogrammetry processing. 
   - [COLMAP installation](https://colmap.github.io/install.html)
   - [Meshroom download](https://alicevision.org/#meshroom)
5. **CUDA-compatible GPU** (recommended): For faster processing

## Installation

1. Download the addon ZIP file from the GitHub repository releases page
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install" and select the downloaded ZIP file
4. Enable the addon by checking the box next to "Drone Video to 3D"

## Workflow Steps

### 1. Prepare Your Drone Video

- Make sure your drone records GPS information in video metadata
- For best results, capture video with steady, slow drone movement
- Ensure there is sufficient overlap between frames
- Record in high resolution with good lighting conditions

### 2. Extract Frames

1. In Blender, open the "Drone Video to 3D" tab in the sidebar (press N if sidebar is hidden)
2. Select your drone video file in the "Video File" field
3. Choose an output directory for the extracted frames and processing data
4. Set your desired frame extraction quality and rate
5. Click "Extract Frames" button to process the video

### 3. Extract GPS Metadata

1. After frame extraction is complete, click "Extract GPS Metadata"
2. This will create files with GPS information from your video
3. If your drone video doesn't contain GPS metadata, you'll receive a warning

### 4. Run Photogrammetry

1. Select your preferred photogrammetry pipeline (COLMAP or Meshroom)
2. Enable/disable CUDA acceleration as needed
3. Click "Run Photogrammetry" to start the 3D reconstruction process
4. This step may take some time depending on your hardware and video complexity

### 5. Import and Refine the 3D Model

1. Once photogrammetry is complete, click "Import 3D Model" to load the result into Blender
2. Use Blender's tools to clean up and refine the model as needed
3. You can visualize the GPS path using the "Show GPS Path on Map" button

### 6. Export the Final Model

1. Select your preferred export format in the "Export Options" panel
2. Choose whether to include textures and georeference data
3. Click "Export Georeferenced Model" to save the final result
4. The model will be saved to the "export" folder inside your output directory

## Troubleshooting

### Missing Dependencies

If you receive errors about missing dependencies, make sure all required software is installed and accessible in your system PATH.

### GPS Metadata Issues

- If no GPS data is found, check if your drone records GPS information
- Some drones may store GPS data in a format not recognized by ExifTool
- Try using the drone's companion app to extract GPS data if available

### Photogrammetry Fails

- Ensure there is sufficient overlap between frames
- Try increasing the number of frames by reducing the frame extraction rate
- Check if your images have enough features and texture for reconstruction
- Make sure your photogrammetry software is correctly installed

### Performance Issues

- For large videos, consider using a lower frame extraction quality
- Enable CUDA acceleration if you have a compatible GPU
- Increase the frame extraction rate to process fewer frames

## Advanced Features

### GPS Trajectory Smoothing

If your GPS data contains noise or inaccuracies, set the "GPS Fix Method" to "Smooth" for better results.

### Manual GPS Adjustment

For fine control over the georeference data, use the "Manually Adjust GPS Poses" option to edit the positions.

## Support

For help, bug reports, or feature requests, please visit the GitHub repository at:
[https://github.com/mauriale/blender-drone-video-to-3d](https://github.com/mauriale/blender-drone-video-to-3d)
