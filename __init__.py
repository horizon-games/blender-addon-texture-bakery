bl_info = {
    "name": "Texture Bakery",
    "author": "Timmith Dysinski",
    "version": (1, 0, 1),
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
    output = nodeGroup.nodes['Group Output']

    color = nodeGroup.nodes['rgb-maker']
    rt_rgb = nodeGroup.nodes['Image Texture.001']
    rgb_img = bpy.data.images.get('rt-rgb')

    alpha = nodeGroup.nodes['alpha-maker']
    rt_alpha = nodeGroup.nodes['Image Texture.004']
    alpha_img = bpy.data.images.get('rt-alpha')

    result_filepath = bpy.data.images['island-basic-final-texture.png'].filepath_from_user()

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
    
    return nodeGroup, output, color, rt_rgb, rgb_img, alpha, rt_alpha, alpha_img, result_filepath, link


def rgb_bake(link, color, output, nodeGroup, rt_rgb, rgb_img):
    link(color.outputs[0],output.inputs[0])
    nodeGroup.nodes.active.select = False
    nodeGroup.nodes.active = rt_rgb
    nodeGroup.nodes.active.select = True
    print("rt-rgb Setup Complete, starting Bake...")
    BAKE(nodeGroup)
    rgb_img.save()
    print("rt-rgb Image Saved.")
    print("")
    return
    
    
def alpha_bake(link, alpha, output, nodeGroup, rt_alpha, alpha_img):
    link(alpha.outputs[0],output.inputs[0])
    nodeGroup.nodes.active.select = False
    nodeGroup.nodes.active = rt_alpha
    nodeGroup.nodes.active.select = True
    print("rt-alpha Setup Complete, starting Bake...")
    BAKE(nodeGroup)
    alpha_img.save()
    print("rt-alpha Image Saved.")
    print("")
    
    
def final_texture_render(result_filepath):
    print("Reloading before Render...")
    bpy.data.images['rt-alpha'].reload()
    bpy.data.images['rt-rgb'].reload()
    print("Rendering...")
    bpy.ops.render.render()
    bpy.data.images['Render Result'].save_render(result_filepath)
    print("Render Saved.")
    bpy.data.images['island-basic-final-texture.png'].reload()


def BAKE(nodeGroup):
    bpy.ops.object.bake(type='DIFFUSE')
    print("{}'s Bake Complete...".format(nodeGroup.nodes.active.name))
    return


def full_bake():
    
    nodeGroup, output, color, rt_rgb, rgb_img, alpha, rt_alpha, alpha_img, result_filepath, link = setup()
    
    print("")
    print("-----------------------------------------------------------")
    print("Starting Full Bake Process:")
    print("")
    
    # Setup the bake and save the output, rt-rgb
    rgb_bake(link, color, output, nodeGroup, rt_rgb, rgb_img)

    # Setup the bake and save the output, rt-alpha
    alpha_bake(link, alpha, output, nodeGroup, rt_alpha, alpha_img)

    # Reload results, render and save final texture
    final_texture_render(result_filepath)
    
    print("")
    print("Full Bake Process Complete!")
    print("-----------------------------------------------------------")
    print("")


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
        row = layout.row()
        row.scale_y = 2.0
        row.operator("texture_bakery.full_bake")



class TextureBakery(Operator):
    """Texture Bakery"""
    bl_idname = "texture_bakery.full_bake"
    bl_label = "Full Texture Bake"
    bl_options = {'REGISTER'}

    def execute(self, context):
        full_bake()
        return {'FINISHED'}

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(TextureBakeryUI)
    bpy.utils.register_class(TextureBakery)

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')

    kmi = km.keymap_items.new(TextureBakery.bl_idname, 'B', 'PRESS', oskey=True, shift=True)
    # kmi.properties.total = 4

    addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(TextureBakeryUI)
    bpy.utils.unregister_class(TextureBakery)

    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
