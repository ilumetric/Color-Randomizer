bl_info = {
    'name': 'Color Randomizer',
    "author": "Max Derksen",
    'version': (1, 3, 0),
    'blender': (4, 2, 0),
    'location': 'VIEW 3D > Header',
    'category': 'Object',
}
import bpy
from bpy.types import Operator, PropertyGroup, AddonPreferences
from bpy.props import IntProperty, PointerProperty
import rna_keymap_ui


def set_name(self, context, obj):
    name = obj.name
    props = obj.random_color_

    if props.color_idx == 0:
        props.color_idx += 1
    else:
        count = props.color_idx - 1
        prefix = "CR" + str(count) + "_"
        lenP = len(prefix)
        name = name[lenP:]

    obj.name = "CR" + str(props.color_idx) + "_" + name

    props.color_idx += 1


def del_prefix(self, context, obj):
    name = obj.name
    props = obj.random_color_

    count = props.color_idx - 1
    prefix = "CR" + str(count) + "_"
    lenP = len(prefix)
    obj.name = name[lenP:]

    props.color_idx = 0


class CR_OT_set_color(Operator):
    bl_idname = "cr.set_color"
    bl_label = "Object Color"
    bl_description = "Relative Plus One"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        return objs != []

    def execute(self, context):
        objects = context.selected_objects
        for obj in objects:
            props = obj.random_color_
            if len(obj.name) >= 54 and props.color_idx == 0:
                self.report({'WARNING'}, f'The object name "{obj.name}" is too long! You need to reduce the name to at least 53 characters.')
                continue

            set_name(self, context, obj)
        return {'FINISHED'}


class CR_OT_del_prefix(Operator):
    bl_idname = "cr.del_prefix"
    bl_label = "Delete Prefixes"
    bl_description = "Delete Prefix in Object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        return any(obj.random_color_.color_idx != 0 for obj in objs)

    def execute(self, context):
        objects = context.selected_objects
        for obj in objects:
            props = obj.random_color_
            if props.color_idx != 0:
                del_prefix(self, context, obj)
        return {'FINISHED'}


def button_in_header(self, context):
    layout = self.layout
    row = layout.row(align = True)
    row.scale_x = 1.3
    row.operator("cr.set_color", text="",  icon='COLOR')
    row.scale_x = 1.0
    row.operator("cr.del_prefix", text="",  icon='X') 


class CR_store(PropertyGroup):
    color_idx: IntProperty(default=0, max=999)


class CR_transform_preferences(AddonPreferences):
    bl_idname =  __name__

    def draw(self, context):
        layout = self.layout
  
        box = layout.box()
        col = box.column()
        col.label(text="Keymap")
        
        kc = context.window_manager.keyconfigs.user
        km = kc.keymaps['3D View']
        keymap_items = km.keymap_items

        kmi = keymap_items['cr.set_color']
        kmi.show_expanded = False
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

        kmi = keymap_items['cr.del_prefix']
        kmi.show_expanded = False
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

        col.label(text="*Some hotkeys may not work because of the use of other addons!!!")

        """ box = layout.box()
        col = box.column(align=True)
        col.label(text="Links")
        row = col.row()
        row.operator("wm.url_open", text="Blender Market").url = "https://blendermarket.com/creators/derksen"
        row.operator("wm.url_open", text="Gumroad").url = "https://gumroad.com/derksen"
        row.operator("wm.url_open", text="Artstation").url = "https://www.artstation.com/derksen" """


cr_keymaps = []  

classes = [
    CR_OT_set_color,
    CR_OT_del_prefix,
    CR_store,
    CR_transform_preferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.random_color_ = PointerProperty(type=CR_store)

    bpy.types.VIEW3D_HT_header.append(button_in_header)

    wm = bpy.context.window_manager
    key_conf = wm.keyconfigs.addon

    if not key_conf:
        return
    
    km = key_conf.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new("cr.set_color", type = "C",value="PRESS", ctrl=True, alt=True, shift=True)
    kmi.active = False
    cr_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("cr.del_prefix", type = "X",value="PRESS", ctrl=True, alt=True, shift=True)
    kmi.active = False
    cr_keymaps.append((km, kmi))


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.random_color_

    bpy.types.VIEW3D_HT_header.remove(button_in_header)

    for km, kmi in cr_keymaps:
        km.keymap_items.remove(kmi)

    cr_keymaps.clear()