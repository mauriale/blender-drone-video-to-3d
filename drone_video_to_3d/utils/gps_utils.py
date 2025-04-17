import pyproj
import json
import csv
import os
import numpy as np

def extract_gps_metadata(exiftool_output):
    """Extract GPS metadata from ExifTool JSON output"""
    try:
        metadata = json.loads(exiftool_output)
        gps_data = {}
        
        for entry in metadata:
            # Extract GPS information if available
            if "GPS" in entry:
                gps = entry["GPS"]
                latitude = gps.get("GPSLatitude")
                longitude = gps.get("GPSLongitude")
                altitude = gps.get("GPSAltitude")
                
                if latitude and longitude:
                    # Extract frame info if available (will depend on how ExifTool processes video)
                    frame_name = f"frame_{int(entry.get('FrameNumber', 0)):04d}.png"
                    
                    gps_data[frame_name] = {
                        "gps": {
                            "latitude": latitude,
                            "longitude": longitude,
                            "altitude": altitude if altitude else 0.0,
                            # Other fields would be populated if available in the metadata
                            "speed": gps.get("GPSSpeed", 0.0),
                            "roll": 0.0,  # Would be extracted if available
                            "pitch": 0.0,  # Would be extracted if available
                            "yaw": 0.0,    # Would be extracted if available
                        },
                        "camera": {
                            "focal_length": entry.get("FocalLength", 24.0),
                            "aperture": entry.get("Aperture", 2.8),
                            "sensor_width": entry.get("SensorWidth", 13.2)
                        }
                    }
        
        return gps_data
    except Exception as e:
        print(f"Error extracting GPS metadata: {str(e)}")
        return {}

def convert_to_cartesian(lat, lon, alt):
    """Convert GPS coordinates to cartesian coordinates"""
    try:
        # Create transformer from WGS84 to ECEF (Earth-Centered, Earth-Fixed)
        transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:4978")
        
        # Transform coordinates
        x, y, z = transformer.transform(lat, lon, alt)
        return (x, y, z)
    except Exception as e:
        print(f"Error converting coordinates: {str(e)}")
        return (0.0, 0.0, 0.0)

def generate_gps_poses_csv(gps_data, output_file):
    """Generate a CSV file with GPS poses for photogrammetry software"""
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["frame", "x", "y", "z", "roll", "pitch", "yaw"])
            
            for frame_name, data in gps_data.items():
                gps = data["gps"]
                lat = gps["latitude"]
                lon = gps["longitude"]
                alt = gps["altitude"]
                
                # Convert to cartesian coordinates
                x, y, z = convert_to_cartesian(lat, lon, alt)
                
                # Write to CSV
                writer.writerow([
                    frame_name,
                    x,
                    y,
                    z,
                    gps["roll"],
                    gps["pitch"],
                    gps["yaw"]
                ])
                
        return True
    except Exception as e:
        print(f"Error generating GPS poses CSV: {str(e)}")
        return False

def generate_meshroom_sensor_data(gps_data, output_file):
    """Generate a sensor_data.xml file for Meshroom/AliceVision"""
    try:
        with open(output_file, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<SensorData>\n')
            
            for i, (frame_name, data) in enumerate(gps_data.items()):
                gps = data["gps"]
                camera = data["camera"]
                
                f.write(f'  <View sensorId="0" poseId="{i}">\n')
                f.write(f'    <Img image="{frame_name}"/>\n')
                f.write(f'    <metadata key="GPS">{gps["latitude"]},{gps["longitude"]},{gps["altitude"]}</metadata>\n')
                f.write(f'    <metadata key="Orientation">{gps["roll"]},{gps["pitch"]},{gps["yaw"]}</metadata>\n')
                f.write(f'    <metadata key="FocalLength">{camera["focal_length"]}</metadata>\n')
                f.write(f'    <metadata key="Aperture">{camera["aperture"]}</metadata>\n')
                f.write(f'    <metadata key="SensorWidth">{camera["sensor_width"]}</metadata>\n')
                f.write('  </View>\n')
                
            f.write('</SensorData>')
            
        return True
    except Exception as e:
        print(f"Error generating Meshroom sensor data: {str(e)}")
        return False

def smooth_gps_trajectory(gps_data, window_size=5):
    """Apply smoothing to GPS trajectory to reduce noise"""
    try:
        frame_names = sorted(list(gps_data.keys()))
        if len(frame_names) < window_size:
            return gps_data  # Not enough points to smooth
            
        # Extract coordinates to arrays
        lats = []
        lons = []
        alts = []
        
        for name in frame_names:
            lats.append(gps_data[name]["gps"]["latitude"])
            lons.append(gps_data[name]["gps"]["longitude"])
            alts.append(gps_data[name]["gps"]["altitude"])
            
        # Convert to numpy arrays
        lats = np.array(lats)
        lons = np.array(lons)
        alts = np.array(alts)
        
        # Apply moving average smoothing
        kernel = np.ones(window_size) / window_size
        
        # Handle edge effects by padding
        lats_padded = np.pad(lats, (window_size//2, window_size//2), mode='edge')
        lons_padded = np.pad(lons, (window_size//2, window_size//2), mode='edge')
        alts_padded = np.pad(alts, (window_size//2, window_size//2), mode='edge')
        
        # Apply convolution for smoothing
        lats_smooth = np.convolve(lats_padded, kernel, mode='valid')
        lons_smooth = np.convolve(lons_padded, kernel, mode='valid')
        alts_smooth = np.convolve(alts_padded, kernel, mode='valid')
        
        # Update GPS data with smoothed values
        smoothed_data = gps_data.copy()
        for i, name in enumerate(frame_names):
            smoothed_data[name]["gps"]["latitude"] = float(lats_smooth[i])
            smoothed_data[name]["gps"]["longitude"] = float(lons_smooth[i])
            smoothed_data[name]["gps"]["altitude"] = float(alts_smooth[i])
            
        return smoothed_data
    except Exception as e:
        print(f"Error smoothing GPS trajectory: {str(e)}")
        return gps_data
