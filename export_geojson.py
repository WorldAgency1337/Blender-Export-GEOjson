bl_info = {
    "name": "Export Selected Objects to GeoJSON",
    "author": "r.moskovkin",
    "version": (1, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Export GeoJSON",
    "description": "Exports selected objects' origins to a GeoJSON file",
    "category": "Import-Export",
}

import bpy
import json
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

class ExportGeoJSONOperator(bpy.types.Operator, ExportHelper):
    """Export selected objects as GeoJSON"""
    bl_idname = "export.geojson"
    bl_label = "Export GeoJSON"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".geojson"
    filter_glob: StringProperty(default="*.geojson", options={'HIDDEN'})

    def execute(self, context):
        objects = bpy.context.selected_objects
        geojson_data = {
            "type": "FeatureCollection",
            "features": []
        }

        for obj in objects:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [obj.location.x, obj.location.y, obj.location.z]
                },
                "properties": {
                    "name": obj.name,
                    "type": obj.type
                }
            }
            geojson_data["features"].append(feature)

        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=4)

        self.report({'INFO'}, "GeoJSON exported successfully!")
        return {'FINISHED'}

class ExportGeoJSONPanel(bpy.types.Panel):
    """Creates a Panel in the Sidebar"""
    bl_label = "Export GeoJSON"
    bl_idname = "VIEW3D_PT_export_geojson"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Export GeoJSON'

    def draw(self, context):
        layout = self.layout
        layout.operator("export.geojson", text="Export to GeoJSON")

# Регистрация
classes = [ExportGeoJSONOperator, ExportGeoJSONPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
