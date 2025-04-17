import os
import subprocess
import json
from pathlib import Path

def check_dependencies():
    """Check if required external dependencies are available"""
    dependencies = {
        "ffmpeg": False,
        "exiftool": False,
        "colmap": False,
        "meshroom": False,
        "cuda": False
    }
    
    # Check FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        dependencies["ffmpeg"] = True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
        
    # Check ExifTool
    try:
        subprocess.run(["exiftool", "-ver"], capture_output=True, check=True)
        dependencies["exiftool"] = True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
        
    # Check COLMAP
    try:
        subprocess.run(["colmap", "-h"], capture_output=True, check=True)
        dependencies["colmap"] = True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
        
    # Check Meshroom (this check might not work for all installations)
    try:
        meshroom_paths = [
            "meshroom",  # If in PATH
            "Meshroom",  # Alternate capitalization
            os.path.join(os.path.expanduser("~"), "Meshroom", "meshroom"),  # Common install location
        ]
        
        for path in meshroom_paths:
            try:
                subprocess.run([path, "-h"], capture_output=True, check=True)
                dependencies["meshroom"] = True
                break
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
    except:
        pass
        
    # Check CUDA
    try:
        # Try to check for CUDA using nvidia-smi
        result = subprocess.run(["nvidia-smi"], capture_output=True, check=True)
        dependencies["cuda"] = True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
        
    return dependencies

def extract_frames(video_path, output_dir, frame_rate=1, quality="HIGH"):
    """Extract frames from a video using FFmpeg"""
    try:
        frames_dir = os.path.join(output_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        # Define quality settings
        if quality == 'HIGH':
            scale = ""
        elif quality == 'MEDIUM':
            scale = "scale=iw/2:ih/2"
        else:  # LOW
            scale = "scale=iw/4:ih/4"
            
        # Prepare FFmpeg command
        ffmpeg_cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"select=not(mod(n\\,{frame_rate})){', ' + scale if scale else ''}",
            "-vsync", "0",
            "-q:v", "1",
            os.path.join(frames_dir, "frame_%04d.png")
        ]
        
        # Execute FFmpeg
        subprocess.run(ffmpeg_cmd, check=True)
        
        # Generate timestamps file using FFmpeg
        timestamp_file = os.path.join(output_dir, "timestamps.csv")
        ffmpeg_timestamp_cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"select=not(mod(n\\,{frame_rate})),showinfo",
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
        
        return True, frames_dir
    except Exception as e:
        return False, str(e)

def extract_gps_metadata_from_video(video_path, output_dir):
    """Extract GPS metadata from a video file using ExifTool"""
    try:
        metadata_file = os.path.join(output_dir, "gps_metadata.json")
        
        # Extract metadata using ExifTool
        exiftool_cmd = [
            "exiftool", "-json", "-g", video_path
        ]
        
        result = subprocess.run(exiftool_cmd, capture_output=True, check=True, text=True)
        
        # Save the metadata to file
        with open(metadata_file, 'w') as f:
            f.write(result.stdout)
            
        return True, metadata_file
    except Exception as e:
        return False, str(e)

def analyze_video(video_path):
    """Get information about a video file"""
    try:
        # Use FFprobe to get video information
        ffprobe_cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        
        result = subprocess.run(ffprobe_cmd, capture_output=True, check=True, text=True)
        video_info = json.loads(result.stdout)
        
        # Check for GPS stream or metadata
        has_gps = False
        
        # Try to detect GPS metadata using ExifTool
        try:
            exiftool_cmd = [
                "exiftool", "-json", "-g", "-a", video_path
            ]
            
            result = subprocess.run(exiftool_cmd, capture_output=True, check=True, text=True)
            exif_data = json.loads(result.stdout)
            
            # Check for GPS metadata
            for entry in exif_data:
                if "GPS" in entry:
                    has_gps = True
                    break
        except:
            pass
        
        # Extract video details
        video_details = {
            "has_gps": has_gps,
            "duration": None,
            "width": None,
            "height": None,
            "fps": None,
            "codec": None
        }
        
        for stream in video_info.get("streams", []):
            if stream.get("codec_type") == "video":
                video_details["width"] = stream.get("width")
                video_details["height"] = stream.get("height")
                
                # Get FPS
                if "avg_frame_rate" in stream:
                    fps_parts = stream["avg_frame_rate"].split('/')
                    if len(fps_parts) == 2 and int(fps_parts[1]) != 0:
                        video_details["fps"] = round(int(fps_parts[0]) / int(fps_parts[1]), 2)
                
                video_details["codec"] = stream.get("codec_name")
                break
        
        if "format" in video_info:
            video_details["duration"] = float(video_info["format"].get("duration", 0))
        
        return video_details
    except Exception as e:
        print(f"Error analyzing video: {str(e)}")
        return None
