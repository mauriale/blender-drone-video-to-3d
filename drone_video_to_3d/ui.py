import bpy
from bpy.types import Panel

class DRONEVIDEO3D_PT_main_panel(Panel):
    bl_label = "Drone Video to 3D"
    bl_idname = "DRONEVIDEO3D_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Drone Video to 3D"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.drone_video_3d
        
        # Video input section
        box = layout.box()
        box.label(text="Video Input")
        box.prop(settings, "video_path")
        box.prop(settings, "output_path")
        
        # Processing options section
        box = layout.box()
        box.label(text="Processing Options")
        box.prop(settings, "use_gps_metadata")
        box.prop(settings, "frame_extraction_quality")
        box.prop(settings, "frame_extraction_rate")
        box.prop(settings, "use_cuda")
        box.prop(settings, "photogrammetry_pipeline")
        
        # Operation buttons
        layout.separator()
        col = layout.column(align=True)
        col.operator("dronevideo3d.extract_frames", text="Extract Frames")
        col.operator("dronevideo3d.extract_gps", text="Extract GPS Metadata")
        col.operator("dronevideo3d.run_photogrammetry", text="Run Photogrammetry")
        layout.separator()
        layout.operator("dronevideo3d.import_model", text="Import 3D Model")

class DRONEVIDEO3D_PT_georeferencing_panel(Panel):
    bl_label = "Georeferencing"
    bl_idname = "DRONEVIDEO3D_PT_georeferencing_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Drone Video to 3D"
    bl_parent_id = "DRONEVIDEO3D_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.drone_video_3d
        
        layout.prop(settings, "gps_fix_method")
        layout.label(text="GPS Data Visualization")
        layout.operator("dronevideo3d.visualize_gps", text="Show GPS Path on Map")
        layout.operator("dronevideo3d.adjust_gps", text="Manually Adjust GPS Poses")
        layout.separator()
        layout.operator("dronevideo3d.export_georeferenced", text="Export Georeferenced Model")

class DRONEVIDEO3D_PT_export_panel(Panel):
    bl_label = "Export Options"
    bl_idname = "DRONEVIDEO3D_PT_export_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Drone Video to 3D"
    bl_parent_id = "DRONEVIDEO3D_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.drone_video_3d
        
        layout.prop(settings, "export_format")
        layout.prop(settings, "include_textures")
        layout.prop(settings, "include_geo_metadata")
        layout.separator()
        layout.operator("dronevideo3d.export_model", text="Export 3D Model")

def register():
    bpy.utils.register_class(DRONEVIDEO3D_PT_main_panel)
    bpy.utils.register_class(DRONEVIDEO3D_PT_georeferencing_panel)
    bpy.utils.register_class(DRONEVIDEO3D_PT_export_panel)

def unregister():
    bpy.utils.unregister_class(DRONEVIDEO3D_PT_export_panel)
    bpy.utils.unregister_class(DRONEVIDEO3D_PT_georeferencing_panel)
    bpy.utils.unregister_class(DRONEVIDEO3D_PT_main_panel)
