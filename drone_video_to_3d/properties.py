import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty, IntProperty

class DroneVideo3DSettings(bpy.types.PropertyGroup):
    video_path: StringProperty(
        name="Video File",
        description="Path to the drone video file",
        default="",
        subtype='FILE_PATH'
    )
    
    output_path: StringProperty(
        name="Output Directory",
        description="Path to save extracted frames and output files",
        default="",
        subtype='DIR_PATH'
    )
    
    use_gps_metadata: BoolProperty(
        name="Use GPS Metadata",
        description="Use GPS metadata from the video for georeference",
        default=True
    )
    
    frame_extraction_quality: EnumProperty(
        name="Frame Quality",
        description="Quality of extracted frames",
        items=[
            ('HIGH', "High", "Extract frames at original resolution"),
            ('MEDIUM', "Medium", "Extract frames at 50% resolution"),
            ('LOW', "Low", "Extract frames at 25% resolution")
        ],
        default='HIGH'
    )
    
    frame_extraction_rate: IntProperty(
        name="Frame Rate",
        description="Extract 1 frame every N frames",
        default=1,
        min=1,
        max=100
    )
    
    use_cuda: BoolProperty(
        name="Use CUDA Acceleration",
        description="Use GPU acceleration for processing",
        default=True
    )
    
    photogrammetry_pipeline: EnumProperty(
        name="Photogrammetry Pipeline",
        description="Choose which photogrammetry software to use",
        items=[
            ('COLMAP', "COLMAP", "Use COLMAP for 3D reconstruction"),
            ('MESHROOM', "Meshroom", "Use Meshroom (AliceVision) for 3D reconstruction")
        ],
        default='COLMAP'
    )
    
    # Additional GPS-related properties
    gps_fix_method: EnumProperty(
        name="GPS Fix Method",
        description="Method to fix or adjust GPS data",
        items=[
            ('NONE', "None", "Use raw GPS data without adjustment"),
            ('SMOOTH', "Smooth", "Apply smoothing to GPS trajectory"),
            ('MANUAL', "Manual", "Allow manual adjustment of GPS points")
        ],
        default='NONE'
    )
    
    export_format: EnumProperty(
        name="Export Format",
        description="Format for the final 3D model",
        items=[
            ('OBJ', "OBJ", "Wavefront OBJ format"),
            ('PLY', "PLY", "Stanford PLY format"),
            ('GLB', "GLB", "Binary glTF format")
        ],
        default='OBJ'
    )
    
    include_textures: BoolProperty(
        name="Include Textures",
        description="Include textures in the exported model",
        default=True
    )
    
    include_geo_metadata: BoolProperty(
        name="Include GeoMetadata",
        description="Include geographic metadata in the exported model",
        default=True
    )

def register():
    bpy.utils.register_class(DroneVideo3DSettings)
    bpy.types.Scene.drone_video_3d = bpy.props.PointerProperty(type=DroneVideo3DSettings)

def unregister():
    del bpy.types.Scene.drone_video_3d
    bpy.utils.unregister_class(DroneVideo3DSettings)
