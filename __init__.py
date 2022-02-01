bl_info = {
    "name": "Texture Bakery",
    "author": "Timmith Dysinski",
    "version": (1, 0, 3),
    "blender": (2, 93, 0),
    "location": "Properties > Scene > Texture Bakery",
    "description": "Helps shortcut the rigorous process of baking textures with some helpful UI",
    "warning": "",
    "doc_url": "",
    "category": "System",
}


import bpy
from bpy.types import Operator


def setup():
    # Variable Setup
    nodeGroup = bpy.data.node_groups['NodeGroup.001']

    rgb_maker = nodeGroup.nodes['rgb-maker']
    rt_rgb = nodeGroup.nodes['Image Texture.001']
    rgb_png = bpy.data.images.get('rt-rgb')

    alpha_maker = nodeGroup.nodes['alpha-maker']
    rt_alpha = nodeGroup.nodes['Image Texture.004']
    alpha_png = bpy.data.images.get('rt-alpha')

    substring = '-final-texture.png'
    for i in bpy.data.images.keys():
        if substring in i:
            final_texture_filename = i
    result_filepath = bpy.data.images[final_texture_filename].filepath_from_user()
    
    final_preview = nodeGroup.nodes['Node'].outputs[0]
    output = nodeGroup.nodes['Group Output'].inputs[0]

    # Function Setup
    link = nodeGroup.links.new
    
    # Ensure that the UV Maps is set to 'export'
    bpy.data.meshes['Cube'].uv_layers.active_index = 0
    bpy.data.meshes['Cube'].uv_layers['export'].active_render = True
    bpy.data.meshes['Cube'].uv_layers['artist'].active_render = False

    # Ensure that 'surface' is the selected object in the scene
    for obj in bpy.data.objects:
        obj.select_set(False)
    bpy.data.objects['surface'].select_set(True)
    
    # Ensure that Active Material Index is set to 'base'
    bpy.data.objects['surface'].active_material_index = 0
    
    return nodeGroup, output, rgb_maker, rt_rgb, rgb_png, alpha_maker, rt_alpha, alpha_png, result_filepath, final_preview, link


def rgb_bake(link, rgb_maker, output, nodeGroup, rt_rgb, rgb_png):
    link(rgb_maker.outputs[0],output)
    nodeGroup.nodes.active.select = False
    nodeGroup.nodes.active = rt_rgb
    nodeGroup.nodes.active.select = True

    # all images (from PSD) post export and post clean (defringer), 
    # set the alphaMode to NONE before rgb bake 
    substring = '-clean'
    for i in bpy.data.images.keys():
        if substring in i:
            bpy.data.images[i].alpha_mode = 'NONE'
            print(i+"'s alpha_mode switched to NONE")

    print("rt-rgb Setup Complete, starting Bake...")
    BAKE(nodeGroup)
    rgb_png.save()

    # and set back to STRAIGHT for alpha bake
    for i in bpy.data.images.keys():
        if substring in i:
            bpy.data.images[i].alpha_mode = 'STRAIGHT'
            print(i+"'s alpha_mode switched back to STRAIGHT")

    print("'rt-rgb.png' Saved.")
    link(rt_rgb.outputs[0],output)
    print("")
    return


def alpha_bake(link, alpha_maker, output, nodeGroup, rt_alpha, alpha_png):
    link(alpha_maker.outputs[0],output)
    nodeGroup.nodes.active.select = False
    nodeGroup.nodes.active = rt_alpha
    nodeGroup.nodes.active.select = True
    print("rt-alpha Setup Complete, starting Bake...")
    BAKE(nodeGroup)
    alpha_png.save()
    print("'rt-alpha.png' Saved.")
    link(rt_alpha.outputs[0],output)
    print("")
    return

# DEPRECATED!!
def final_texture_render(output, result_filepath, final_preview, link):
    print("Reloading before Render...")
    bpy.data.images['rt-alpha'].reload()
    bpy.data.images['rt-rgb'].reload()
    print("Rendering...")
    bpy.ops.render.render()
    print("Render Complete.")
    bpy.data.images['Render Result'].save_render(result_filepath)
    print("'island-basic-final-texture.png' Saved.")
    bpy.data.images['island-basic-final-texture.png'].reload()
    link(final_preview, output)
    print("")
    return


def BAKE(nodeGroup):
    bpy.ops.object.bake(type='DIFFUSE')
    print("{}'s Bake Complete...".format(nodeGroup.nodes.active.name))
    return

# DEPRECATED!!
def full_bake():
    print("")
    print("-----------------------------------------------------------")
    print("Starting Full Bake Process:")
    print("")
    
    # Initial Setup
    nodeGroup, output, rgb_maker, rt_rgb, rgb_png, alpha_maker, rt_alpha, alpha_png, result_filepath, final_preview, link = setup()
    
    # Setup the bake and save the output, rt-rgb
    rgb_bake(link, rgb_maker, output, nodeGroup, rt_rgb, rgb_png)

    # Setup the bake and save the output, rt-alpha
    alpha_bake(link, alpha_maker, output, nodeGroup, rt_alpha, alpha_png)

    # Reload results, render and save final texture
    final_texture_render(output, result_filepath, final_preview, link)
    
    print("Full Bake Process Complete!")
    print("-----------------------------------------------------------")
    print("")
    return


class TextureBakeryUI(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Texture Bakery"
    bl_idname = "horizon.texture_bakery"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # row = layout.row()
        # row.scale_y = 2.0
        # row.operator("texture_bakery.full_bake")
        row = layout.row()
        row.operator("texture_bakery.rgb_bake")
        row.operator("texture_bakery.alpha_bake")
        # row = layout.row()
        # row.operator("texture_bakery.final_texture_render")

class FullBake(Operator):
    bl_idname = "texture_bakery.full_bake"
    bl_label = "Full Texture Bake"
    bl_options = {'REGISTER'}

    def execute(self, context):
        full_bake()
        return {'FINISHED'}


class rgbBake(Operator):
    bl_idname = "texture_bakery.rgb_bake"
    bl_label = "rt-rgb Bake (only)"
    bl_options = {'REGISTER'}

    def execute(self, context):
        nodeGroup, output, rgb_maker, rt_rgb, rgb_png, alpha_maker, rt_alpha, alpha_png, result_filepath, final_preview, link = setup()
        rgb_bake(link, rgb_maker, output, nodeGroup, rt_rgb, rgb_png)
        return {'FINISHED'}


class alphaBake(Operator):
    bl_idname = "texture_bakery.alpha_bake"
    bl_label = "rt-alpha Bake (only)"
    bl_options = {'REGISTER'}

    def execute(self, context):
        nodeGroup, output, rgb_maker, rt_rgb, rgb_png, alpha_maker, rt_alpha, alpha_png, result_filepath, final_preview, link = setup()
        alpha_bake(link, alpha_maker, output, nodeGroup, rt_alpha, alpha_png)
        return {'FINISHED'}


class FinalTextureRender(Operator):
    bl_idname = "texture_bakery.final_texture_render"
    bl_label = "Final Texture Render (only)"
    bl_options = {'REGISTER'}

    def execute(self, context):
        nodeGroup, output, rgb_maker, rt_rgb, rgb_png, alpha_maker, rt_alpha, alpha_png, result_filepath, final_preview, link = setup()
        final_texture_render(output, result_filepath, final_preview, link)
        return {'FINISHED'}


# Store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(TextureBakeryUI)
    # bpy.utils.register_class(FullBake)
    bpy.utils.register_class(rgbBake)
    bpy.utils.register_class(alphaBake)
    # bpy.utils.register_class(FinalTextureRender)

    # Handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(FullBake.bl_idname, 'B', 'PRESS', oskey=True, shift=True)

    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(TextureBakeryUI)
    # bpy.utils.unregister_class(FullBake)
    bpy.utils.unregister_class(rgbBake)
    bpy.utils.unregister_class(alphaBake)
    # bpy.utils.unregister_class(FinalTextureRender)

    # Handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
