import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty

class ImpostorBaker(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    #bl_idname = __name__
    
    bl_idname = __package__

    filepath: StringProperty(
        name='File path',
        subtype='FILE_PATH',
    )

    #---------------Bake Textures---------------#
    bake_normal_map: BoolProperty(
        name="Bake normal map",
        default=True,
    )
    bake_OBN_map: BoolProperty(
        name="Bake object space bent normal map",
        default=True,
    )
    bake_TBN_map: BoolProperty(
        name="Bake tangent space bent normal map",
        default=True,
    )
    bake_depth_map: BoolProperty(
        name="Bake depth map",
        default=True,
    )
    bake_mask_map: BoolProperty(
        name="Bake mask map",
        default=True,
    )

    #---------------Margin for Textures---------------#
    suffix_margin: StringProperty(
        name="Margin suffix",
        subtype='FILE_NAME',
        default="margin",
        #[‘FILE_PATH’, ‘DIR_PATH’, ‘FILE_NAME’, ‘BYTE_STRING’, ‘PASSWORD’, ‘NONE’]
    )
    margin_base_color_map: BoolProperty(
        name="Margin for BaseColor",
        default=True,
    )
    margin_OBN_map: BoolProperty(
        name="Margin for object space bent normal map",
        default=True,
    )
    margin_TBN_map: BoolProperty(
        name="Margin for tangent space bent normal map",
        default=True,
    )
    margin_depth_map: BoolProperty(
        name="Margin for depth map",
        default=True,
    )

    #---------------Margin for Textures---------------#
    suffix_Base_color: StringProperty(
        name="BaseColor suffix",
        subtype='FILE_NAME',
        default="D",
    )
    suffix_normal: StringProperty(
        name="Normal suffix",
        subtype='FILE_NAME',
        default="N",
    )
    suffix_OBN: StringProperty(
        name="Object space bent normal map suffix",
        subtype='FILE_NAME',
        default="OBN",
    )
    suffix_TBN: StringProperty(
        name="Tangent space bent normal map suffix",
        subtype='FILE_NAME',
        default="TBN",
    )
    suffix_mask: StringProperty(
        name="Mask suffix",
        subtype='FILE_NAME',
        default="M",
    )
    suffix_depth: StringProperty(
        name="Depth suffix",
        subtype='FILE_NAME',
        default="depth",
    )
    # number: IntProperty(
    #     name="Example Number",
    #     default=4,
    # )

    def draw(self, context):
        layout = self.layout
        layout.label(text='set the File Path where the Textures gets saved to (empty means it is the same folder the .blend file is saved in.)')
        layout.prop(self, "filepath")
        layout.label(text="select which of the following textures should be baked:")
        layout.prop(self, "bake_normal_map")
        layout.prop(self, "bake_OBN_map")
        layout.prop(self, "bake_TBN_map")
        layout.prop(self, "bake_depth_map")
        layout.prop(self, "bake_mask_map")

        layout.label(text="select the textures for which margin textures should be created:")
        layout.prop(self, "suffix_margin")
        layout.prop(self, "margin_base_color_map")
        layout.prop(self, "margin_OBN_map")
        layout.prop(self, "margin_TBN_map")
        layout.prop(self, "margin_depth_map")
        
        layout.label(text="Define which suffixes should be used for the textures:")
        layout.prop(self, "suffix_Base_color")
        layout.prop(self, "suffix_normal")
        layout.prop(self, "suffix_OBN")
        layout.prop(self, "suffix_TBN")
        layout.prop(self, "suffix_mask")
        layout.prop(self, "suffix_depth")
        
        #layout.prop(self, "number")

class OBJECT_OT_addon_prefs_example(Operator):
    """Display example preferences"""
    bl_idname = "object.addon_prefs_example"
    bl_label = "Add-on Preferences Example"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        info = ("Path: %s, Number: %d, Boolean %r" %
                (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}
