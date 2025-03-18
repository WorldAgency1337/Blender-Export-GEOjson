bl_info = {
    "name": "Export Selected Objects to GeoJSON",
    "author": "r.moskovkin",
    "version": (1, 4),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Export",
    "description": "Exports selected objects' origins to a GeoJSON file with Glass properties",
    "category": "Import-Export",
}

import bpy
import json
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

def get_glass_material_data(material):
    """Извлекает параметры стеклянного материала"""
    if material and material.node_tree:
        for node in material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                return {
                    "color_RGB": {
                        "Red": int(node.inputs['Base Color'].default_value[0] * 255),
                        "Green": int(node.inputs['Base Color'].default_value[1] * 255),
                        "Blue": int(node.inputs['Base Color'].default_value[2] * 255)
                    },
                    "transparency": round(node.inputs['Alpha'].default_value, 2),
                    "refraction": round(node.inputs['IOR'].default_value, 2),
                    "roughness": round(node.inputs['Roughness'].default_value, 2),
                    "metallicity": round(node.inputs['Metallic'].default_value, 2)
                }
    return None

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
                "type": "ObjectFeature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [obj.location.x, obj.location.y]  # Убираем Z-координату
                }
            }

            # Проверяем, есть ли "стеклянные" материалы
            glass_materials = {}
            if obj.type == 'MESH' and obj.data.materials:
                for mat in obj.data.materials:
                    if "Glass" in mat.name:  # Проверка по имени материала
                        material_data = get_glass_material_data(mat)
                        if material_data:
                            glass_materials[mat.name] = material_data
            
            # Добавляем "Glasses", если нашли стеклянные материалы
            if glass_materials:
                feature["Glasses"] = [glass_materials]

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
    bl_category = 'Export'  # Важно! Здесь указываем основную вкладку

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
