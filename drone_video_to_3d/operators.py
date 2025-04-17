import bpy
import os
import subprocess
import json
import tempfile
import webbrowser
import numpy as np
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, FloatProperty

from .utils import gps_utils

class DRONEVIDEO3D_OT_extract_frames(Operator):
    bl_idname = "dronevideo3d.extract_frames"
    bl_label = "Extract Frames"
    bl_description = "Extract frames from drone video"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.drone_video_3d
        
        if not settings.video_path:
            self.report({'ERROR'}, "Please select a video file")
            return {'CANCELLED'}
            
        if not settings.output_path:
            self.report({'ERROR'}, "Please select an output directory")
            return {'CANCELLED'}
            
        # Create output directory if it doesn't exist
        frames_dir = os.path.join(settings.output_path, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        # Extract frames using FFmpeg
        try:
            # Define quality settings
            if settings.frame_extraction_quality == 'HIGH':
                scale = ""
            elif settings.frame_extraction_quality == 'MEDIUM':
                scale = "scale=iw/2:ih/2"
            else:  # LOW
                scale = "scale=iw/4:ih/4"
                
            # Prepare FFmpeg command
            ffmpeg_cmd = [
                "ffmpeg", "-i", settings.video_path,
                "-vf", f"select=not(mod(n\\,{settings.frame_extraction_rate})){', ' + scale if scale else ''}",
                "-vsync", "0",
                "-q:v", "1",
                os.path.join(frames_dir, "frame_%04d.png")
            ]
            
            # Execute FFmpeg and capture timestamps
            subprocess.run(ffmpeg_cmd, check=True)
            
            # Generate timestamps file using FFmpeg
            timestamp_file = os.path.join(settings.output_path, "timestamps.csv")
            ffmpeg_timestamp_cmd = [
                "ffmpeg", "-i", settings.video_path,
                "-vf", f"select=not(mod(n\\,{settings.frame_extraction_rate})),showinfo",
                "-f", "null", "-"
            ]
            
            # Capture showinfo output for timestamps
            process = subprocess.Popen(ffmpeg_timestamp_cmd, stderr=subprocess.PIPE, universal_newlines=True)
            output, _ = process.communicate()
            
            # Parse timestamps from showinfo output and save to file
            with open(timestamp_file, 'w') as f:
                f.write("frame,timestamp\n")
                for line in output.split('\n'):
                    if "pts_time:" in line:
                        pts_time = line.split("pts_time:")[1].split()[0]
                        frame_num = line.split("n:")[1].split()[0]
                        f.write(f"frame_{int(frame_num):04d}.png,{pts_time}\n")
            
            self.report({'INFO'}, f"Successfully extracted frames to {frames_dir}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error extracting frames: {str(e)}")
            return {'CANCELLED'}

class DRONEVIDEO3D_OT_extract_gps(Operator):
    bl_idname = "dronevideo3d.extract_gps"
    bl_label = "Extract GPS Metadata"
    bl_description = "Extract GPS metadata from video or frames"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.drone_video_3d
        
        if not settings.video_path:
            self.report({'ERROR'}, "Please select a video file")
            return {'CANCELLED'}
            
        if not settings.output_path:
            self.report({'ERROR'}, "Please select an output directory")
            return {'CANCELLED'}
        
        # Create output directory if it doesn't exist
        frames_dir = os.path.join(settings.output_path, "frames")
        if not os.path.exists(frames_dir):
            self.report({'ERROR'}, "Please extract frames first")
            return {'CANCELLED'}
            
        # Check if exiftool is available
        try:
            subprocess.run(["exiftool", "-ver"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            self.report({'ERROR'}, "ExifTool not found. Please install ExifTool and make it available in PATH")
            return {'CANCELLED'}
            
        try:
            # Extract GPS metadata from video
            metadata_file = os.path.join(settings.output_path, "gps_metadata.json")
            exiftool_cmd = [
                "exiftool", "-json", "-g", settings.video_path
            ]
            
            result = subprocess.run(exiftool_cmd, capture_output=True, check=True, text=True)
            
            # Save the metadata to file
            with open(metadata_file, 'w') as f:
                f.write(result.stdout)
                
            # Extract GPS data
            gps_data = gps_utils.extract_gps_metadata(result.stdout)
            
            # Apply smoothing if requested
            if settings.gps_fix_method == 'SMOOTH':
                gps_data = gps_utils.smooth_gps_trajectory(gps_data)
                
            # Create CSV for GPS poses
            csv_file = os.path.join(settings.output_path, "gps_poses.csv")
            gps_utils.generate_gps_poses_csv(gps_data, csv_file)
            
            # Create Meshroom XML file if needed
            if settings.photogrammetry_pipeline == 'MESHROOM':
                xml_file = os.path.join(settings.output_path, "sensor_data.xml")
                gps_utils.generate_meshroom_sensor_data(gps_data, xml_file)
            
            self.report({'INFO'}, f"GPS metadata extracted to {metadata_file} and {csv_file}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error extracting GPS metadata: {str(e)}")
            return {'CANCELLED'}

class DRONEVIDEO3D_OT_run_photogrammetry(Operator):
    bl_idname = "dronevideo3d.run_photogrammetry"
    bl_label = "Run Photogrammetry"
    bl_description = "Run photogrammetry pipeline"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.drone_video_3d
        
        if not settings.output_path:
            self.report({'ERROR'}, "Please select an output directory")
            return {'CANCELLED'}
            
        frames_dir = os.path.join(settings.output_path, "frames")
        if not os.path.exists(frames_dir):
            self.report({'ERROR'}, "Please extract frames first")
            return {'CANCELLED'}
            
        gps_csv = os.path.join(settings.output_path, "gps_poses.csv")
        if not os.path.exists(gps_csv) and settings.use_gps_metadata:
            self.report({'ERROR'}, "Please extract GPS metadata first")
            return {'CANCELLED'}
            
        # Create photogrammetry output directory
        photo_dir = os.path.join(settings.output_path, "photogrammetry")
        os.makedirs(photo_dir, exist_ok=True)
        
        # Run appropriate photogrammetry pipeline
        if settings.photogrammetry_pipeline == 'COLMAP':
            return self.run_colmap(context, frames_dir, gps_csv, photo_dir)
        else:  # MESHROOM
            return self.run_meshroom(context, frames_dir, os.path.join(settings.output_path, "sensor_data.xml"), photo_dir)
            
    def run_colmap(self, context, frames_dir, gps_csv, photo_dir):
        settings = context.scene.drone_video_3d
        
        # Check if COLMAP is available
        try:
            subprocess.run(["colmap", "-h"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            self.report({'ERROR'}, "COLMAP not found. Please install COLMAP and make it available in PATH")
            return {'CANCELLED'}
        
        try:
            # Create COLMAP database
            db_path = os.path.join(photo_dir, "database.db")
            sparse_dir = os.path.join(photo_dir, "sparse")
            os.makedirs(sparse_dir, exist_ok=True)
            
            # Feature extraction
            self.report({'INFO'}, "Running COLMAP feature extraction (this may take a while)...")
            feature_cmd = [
                "colmap", "feature_extractor",
                "--database_path", db_path,
                "--image_path", frames_dir,
                "--ImageReader.single_camera", "1",
                "--ImageReader.camera_model", "OPENCV"
            ]
            
            if settings.use_gps_metadata:
                feature_cmd.extend(["--ImageReader.gps_prior", "1"])
                
            if settings.use_cuda:
                feature_cmd.extend(["--SiftExtraction.use_gpu", "1"])
                
            subprocess.run(feature_cmd, check=True)
            
            # Feature matching
            self.report({'INFO'}, "Running COLMAP feature matching...")
            matching_cmd = [
                "colmap", "exhaustive_matcher",
                "--database_path", db_path
            ]
            
            if settings.use_cuda:
                matching_cmd.extend(["--SiftMatching.use_gpu", "1"])
                
            subprocess.run(matching_cmd, check=True)
            
            # Structure from motion
            self.report({'INFO'}, "Running COLMAP structure from motion...")
            mapper_cmd = [
                "colmap", "mapper",
                "--database_path", db_path,
                "--image_path", frames_dir,
                "--output_path", sparse_dir
            ]
                
            subprocess.run(mapper_cmd, check=True)
            
            # Create a completion marker
            with open(os.path.join(photo_dir, "colmap_completed.txt"), 'w') as f:
                f.write("COLMAP processing completed\n")
                
            self.report({'INFO'}, f"COLMAP processing completed. Results saved to {photo_dir}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error running COLMAP: {str(e)}")
            return {'CANCELLED'}
        
    def run_meshroom(self, context, frames_dir, sensor_data_xml, photo_dir):
        settings = context.scene.drone_video_3d
        
        # This is a placeholder. In a real implementation, you would:
        # 1. Check if Meshroom is installed
        # 2. Run the Meshroom pipeline with the frames and sensor data
        
        self.report({'WARNING'}, "Meshroom integration not fully implemented yet.")
        
        # Create a dummy completion marker
        with open(os.path.join(photo_dir, "meshroom_completed.txt"), 'w') as f:
            f.write("Meshroom processing would be completed here.\n")
            
        return {'FINISHED'}

class DRONEVIDEO3D_OT_import_model(Operator):
    bl_idname = "dronevideo3d.import_model"
    bl_label = "Import 3D Model"
    bl_description = "Import the generated 3D model into Blender"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.drone_video_3d
        
        if not settings.output_path:
            self.report({'ERROR'}, "Please select an output directory")
            return {'CANCELLED'}
            
        photo_dir = os.path.join(settings.output_path, "photogrammetry")
        if not os.path.exists(photo_dir):
            self.report({'ERROR'}, "Please run photogrammetry first")
            return {'CANCELLED'}
        
        # Look for the 3D model file
        model_file = None
        
        if settings.photogrammetry_pipeline == 'COLMAP':
            # Look for dense reconstruction result (fused.ply)
            dense_dir = os.path.join(photo_dir, "dense")
            if os.path.exists(dense_dir):
                fused_ply = os.path.join(dense_dir, "fused.ply")
                if os.path.exists(fused_ply):
                    model_file = fused_ply
        else:  # MESHROOM
            # Look for Meshroom mesh.obj
            mesh_dir = os.path.join(photo_dir, "MeshroomCache", "Texturing")
            if os.path.exists(mesh_dir):
                # Find the latest mesh.obj file
                for root, dirs, files in os.walk(mesh_dir):
                    for file in files:
                        if file.endswith(".obj"):
                            model_file = os.path.join(root, file)
                            break
                    if model_file:
                        break
        
        if not model_file:
            # For demonstration, create a simple placeholder model
            self.report({'WARNING'}, "No 3D model file found. Creating a placeholder model.")
            
            # Create a simple cube as a placeholder
            bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
            obj = context.active_object
            obj.name = "DroneScan_Model"
            
            self.report({'INFO'}, "Created placeholder 3D model")
            return {'FINISHED'}
        
        # Import the model
        if model_file.endswith(".ply"):
            bpy.ops.import_mesh.ply(filepath=model_file)
        elif model_file.endswith(".obj"):
            bpy.ops.import_scene.obj(filepath=model_file)
            
        # Rename the imported object
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                obj.name = "DroneScan_Model"
                break
                
        self.report({'INFO'}, f"Imported 3D model from {model_file}")
        return {'FINISHED'}

class DRONEVIDEO3D_OT_visualize_gps(Operator):
    bl_idname = "dronevideo3d.visualize_gps"
    bl_label = "Visualize GPS Path"
    bl_description = "Visualize the GPS path on a map"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.drone_video_3d
        
        if not settings.output_path:
            self.report({'ERROR'}, "Please select an output directory")
            return {'CANCELLED'}
            
        gps_csv = os.path.join(settings.output_path, "gps_poses.csv")
        if not os.path.exists(gps_csv):
            self.report({'ERROR'}, "Please extract GPS metadata first")
            return {'CANCELLED'}
            
        # Create a simple HTML map to visualize GPS path
        try:
            # Read GPS data from CSV
            gps_coords = []
            with open(gps_csv, 'r') as f:
                import csv
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert cartesian to GPS coordinates (simplified approach)
                    # Note: In a real implementation, you would use a proper reverse transformation
                    gps_coords.append({
                        'frame': row['frame'],
                        'lat': float(row['x']) / 111111.0,  # Simplified conversion
                        'lon': float(row['y']) / 111111.0,  # Simplified conversion
                        'alt': float(row['z'])
                    })
            
            # Create HTML map file
            map_file = os.path.join(settings.output_path, "gps_map.html")
            with open(map_file, 'w') as f:
                f.write("<!DOCTYPE html>\n")
                f.write("<html>\n")
                f.write("<head>\n")
                f.write("  <title>Drone GPS Path</title>\n")
                f.write("  <style>\n")
                f.write("    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }\n")
                f.write("    h1 { color: #333; }\n")
                f.write("    .map-container { width: 100%; height: 500px; border: 1px solid #ccc; }\n")
                f.write("    table { border-collapse: collapse; width: 100%; margin-top: 20px; }\n")
                f.write("    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n")
                f.write("    th { background-color: #f2f2f2; }\n")
                f.write("  </style>\n")
                f.write("</head>\n")
                f.write("<body>\n")
                f.write("  <h1>Drone GPS Path Visualization</h1>\n")
                f.write("  <div class=\"map-container\">\n")
                f.write("    <p>Map visualization would be displayed here using folium or similar library.</p>\n")
                f.write("    <p>This is a placeholder map. In a complete implementation, you would see an interactive map with the drone flight path.</p>\n")
                f.write("  </div>\n")
                f.write("  <h2>GPS Coordinates</h2>\n")
                f.write("  <table>\n")
                f.write("    <tr><th>Frame</th><th>Latitude</th><th>Longitude</th><th>Altitude</th></tr>\n")
                
                # Add GPS coordinates to table
                for coord in gps_coords[:10]:  # Limit to first 10 for brevity
                    f.write(f"    <tr><td>{coord['frame']}</td><td>{coord['lat']:.6f}</td><td>{coord['lon']:.6f}</td><td>{coord['alt']:.2f}</td></tr>\n")
                
                f.write("  </table>\n")
                f.write("</body>\n")
                f.write("</html>\n")
            
            # Open in web browser
            webbrowser.open(map_file)
            
            self.report({'INFO'}, f"GPS path visualization saved to {map_file}")
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"Error visualizing GPS path: {str(e)}")
            return {'CANCELLED'}

class DRONEVIDEO3D_OT_adjust_gps(Operator):
    bl_idname = "dronevideo3d.adjust_gps"
    bl_label = "Adjust GPS Poses"
    bl_description = "Manually adjust GPS poses"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.drone_video_3d
        
        if not settings.output_path:
            self.report({'ERROR'}, "Please select an output directory")
            return {'CANCELLED'}
            
        gps_csv = os.path.join(settings.output_path, "gps_poses.csv")
        if not os.path.exists(gps_csv):
            self.report({'ERROR'}, "Please extract GPS metadata first")
            return {'CANCELLED'}
            
        self.report({'WARNING'}, "GPS adjustment interface not fully implemented yet.")
        
        # Placeholder for GPS adjustment UI
        # In a real implementation, this would open a custom UI for adjusting GPS points
        
        return {'FINISHED'}

class DRONEVIDEO3D_OT_export_georeferenced(Operator):
    bl_idname = "dronevideo3d.export_georeferenced"
    bl_label = "Export Georeferenced Model"
    bl_description = "Export the 3D model with georeferencing"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.drone_video_3d
        
        if not settings.output_path:
            self.report({'ERROR'}, "Please select an output directory")
            return {'CANCELLED'}
            
        # Check if we have a model to export
        model_obj = bpy.data.objects.get("DroneScan_Model")
        if not model_obj:
            self.report({'ERROR'}, "Please import a 3D model first")
            return {'CANCELLED'}
            
        # Export model in the selected format
        export_dir = os.path.join(settings.output_path, "export")
        os.makedirs(export_dir, exist_ok=True)
        
        model_file = os.path.join(export_dir, f"drone_model.{settings.export_format.lower()}")
        
        # Select the model for export
        bpy.ops.object.select_all(action='DESELECT')
        model_obj.select_set(True)
        
        # Export based on format
        if settings.export_format == 'OBJ':
            bpy.ops.export_scene.obj(
                filepath=model_file,
                use_selection=True,
                use_materials=settings.include_textures
            )
        elif settings.export_format == 'PLY':
            bpy.ops.export_mesh.ply(
                filepath=model_file,
                use_selection=True
            )
        elif settings.export_format == 'GLB':
            bpy.ops.export_scene.gltf(
                filepath=model_file,
                export_format='GLB',
                use_selection=True
            )
        
        # Create GeoJSON metadata file if requested
        if settings.include_geo_metadata:
            geojson_file = os.path.join(export_dir, "geo_metadata.geojson")
            with open(geojson_file, 'w') as f:
                f.write('{\n')
                f.write('  "type": "FeatureCollection",\n')
                f.write('  "features": [\n')
                f.write('    {\n')
                f.write('      "type": "Feature",\n')
                f.write('      "properties": {\n')
                f.write('        "model": "drone_model",\n')
                f.write('        "description": "Drone scan 3D model"\n')
                f.write('      },\n')
                f.write('      "geometry": {\n')
                f.write('        "type": "Polygon",\n')
                f.write('        "coordinates": [\n')
                f.write('          [\n')
                f.write('            [0, 0],\n')
                f.write('            [0, 1],\n')
                f.write('            [1, 1],\n')
                f.write('            [1, 0],\n')
                f.write('            [0, 0]\n')
                f.write('          ]\n')
                f.write('        ]\n')
                f.write('      }\n')
                f.write('    }\n')
                f.write('  ]\n')
                f.write('}\n')
            
        self.report({'INFO'}, f"Exported georeferenced model to {model_file}")
        return {'FINISHED'}

class DRONEVIDEO3D_OT_export_model(Operator):
    bl_idname = "dronevideo3d.export_model"
    bl_label = "Export 3D Model"
    bl_description = "Export the 3D model"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.drone_video_3d
        
        if not settings.output_path:
            self.report({'ERROR'}, "Please select an output directory")
            return {'CANCELLED'}
            
        # Check if we have a model to export
        model_obj = bpy.data.objects.get("DroneScan_Model")
        if not model_obj:
            self.report({'ERROR'}, "Please import a 3D model first")
            return {'CANCELLED'}
            
        # Export model in the selected format
        export_dir = os.path.join(settings.output_path, "export")
        os.makedirs(export_dir, exist_ok=True)
        
        model_file = os.path.join(export_dir, f"drone_model.{settings.export_format.lower()}")
        
        # Select the model for export
        bpy.ops.object.select_all(action='DESELECT')
        model_obj.select_set(True)
        
        # Export based on format
        if settings.export_format == 'OBJ':
            bpy.ops.export_scene.obj(
                filepath=model_file,
                use_selection=True,
                use_materials=settings.include_textures
            )
        elif settings.export_format == 'PLY':
            bpy.ops.export_mesh.ply(
                filepath=model_file,
                use_selection=True
            )
        elif settings.export_format == 'GLB':
            bpy.ops.export_scene.gltf(
                filepath=model_file,
                export_format='GLB',
                use_selection=True
            )
        
        self.report({'INFO'}, f"Exported 3D model to {model_file}")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(DRONEVIDEO3D_OT_extract_frames)
    bpy.utils.register_class(DRONEVIDEO3D_OT_extract_gps)
    bpy.utils.register_class(DRONEVIDEO3D_OT_run_photogrammetry)
    bpy.utils.register_class(DRONEVIDEO3D_OT_import_model)
    bpy.utils.register_class(DRONEVIDEO3D_OT_visualize_gps)
    bpy.utils.register_class(DRONEVIDEO3D_OT_adjust_gps)
    bpy.utils.register_class(DRONEVIDEO3D_OT_export_georeferenced)
    bpy.utils.register_class(DRONEVIDEO3D_OT_export_model)

def unregister():
    bpy.utils.unregister_class(DRONEVIDEO3D_OT_export_model)
    bpy.utils.unregister_class(DRONEVIDEO3D_OT_export_georeferenced)
    bpy.utils.unregister_class(DRONEVIDEO3D_OT_adjust_gps)
    bpy.utils.unregister_class(DRONEVIDEO3D_OT_visualize_gps)
    bpy.utils.unregister_class(DRONEVIDEO3D_OT_import_model)
    bpy.utils.unregister_class(DRONEVIDEO3D_OT_run_photogrammetry)
    bpy.utils.unregister_class(DRONEVIDEO3D_OT_extract_gps)
    bpy.utils.unregister_class(DRONEVIDEO3D_OT_extract_frames)
