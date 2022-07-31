# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "ImpostorBaker",
    "author" : "Malte Szellas",
    "description" : "",
    "version": (2, 0, 1),
    "blender" : (3, 1, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
from . import ui
from . import operators



def bake_and_create_impostor(self, context):
    self.layout.operator('object.bakeandcreateimpostor')

def register():
    bpy.types.VIEW3D_MT_object.append(bake_and_create_impostor)
    bpy.utils.register_class(ui.OBJECT_OT_addon_prefs_example)
    bpy.utils.register_class(ui.ImpostorBaker)
    bpy.utils.register_class(operators.BakeAndCreateImpostorOperator)

def unregister():
    bpy.types.VIEW3D_MT_object.remove(bake_and_create_impostor)
    bpy.utils.unregister_class(ui.OBJECT_OT_addon_prefs_example)
    bpy.utils.unregister_class(ui.ImpostorBaker)
    bpy.utils.unregister_class(operators.BakeAndCreateImpostorOperator)