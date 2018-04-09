# https://github.com/panmari/stanford-shapenet-renderer

# A simple script that uses blender to render views of a 
# single object by rotation the camera around it.
# Also produces depth map at the same time.
#
# Example:
# blender --background --python mytest.py -- --views 10 /path/to/my.obj
#

import argparse, sys, os
import bpy
import numpy as np

def render_model(obj_path, views, output_folder):
    depth_scale = 0.20

    # Set up rendering of depth map:
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # Add passes for additionally dumping albed and normals.
    bpy.context.scene.render.layers["RenderLayer"].use_pass_normal = True
    bpy.context.scene.render.layers["RenderLayer"].use_pass_color = True

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    rl = tree.nodes.new('CompositorNodeRLayers')

    map = tree.nodes.new(type="CompositorNodeMapValue")
    # Size is chosen kind of arbitrarily, 
    # try out until you're satisfied with resulting depth map.
    map.offset = [-.5]
    map.size = [depth_scale]
    map.use_min = True
    map.min = [0]
    map.use_max = True
    map.max = [255]

    links.new(rl.outputs['Depth'], map.inputs[0])

    invert = tree.nodes.new(type="CompositorNodeInvert")
    links.new(map.outputs[0], invert.inputs[1])

    # create a file output node and set the path
    depthFileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    depthFileOutput.label = 'Depth Output'
    links.new(invert.outputs[0], depthFileOutput.inputs[0])

    scale_normal = tree.nodes.new(type="CompositorNodeMixRGB")
    scale_normal.blend_type = 'MULTIPLY'
    # scale_normal.use_alpha = True
    scale_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
    links.new(rl.outputs['Normal'], scale_normal.inputs[1])

    bias_normal = tree.nodes.new(type="CompositorNodeMixRGB")
    bias_normal.blend_type = 'ADD'
    # bias_normal.use_alpha = True
    bias_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
    links.new(scale_normal.outputs[0], bias_normal.inputs[1])

    normalFileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    normalFileOutput.label = 'Normal Output'
    links.new(bias_normal.outputs[0], normalFileOutput.inputs[0])

    # Delete default cube
    bpy.data.objects['Cube'].select = True
    bpy.ops.object.delete()

    bpy.ops.import_scene.obj(filepath=obj_path)
    for object in bpy.context.scene.objects:
        if object.name in ['Camera', 'Lamp']:
            continue
        bpy.context.scene.objects.active = object

        # normalize object dimensions
        x, y, z = bpy.context.active_object.dimensions
        maxDim = max(x,y,z)
        scale = 2/maxDim
        bpy.ops.transform.resize(value=(scale,scale,scale))
        bpy.ops.object.transform_apply(scale=True)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.context.object.modifiers["EdgeSplit"].split_angle = 1.32645
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")

        # center object
        bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN")


    # Make light just directional, disable shadows.
    lamp = bpy.data.lamps['Lamp']
    lamp.type = 'SUN'
    lamp.shadow_method = 'NOSHADOW'
    # Possibly disable specular shading:
    lamp.use_specular = False

    # Add another light source so stuff facing away from light is not completely dark
    bpy.context.scene.world.light_settings.use_environment_light = True
    bpy.context.scene.world.light_settings.environment_energy = 0.3
    bpy.context.scene.world.light_settings.environment_color = 'PLAIN'

    bpy.ops.object.lamp_add(type='SUN')
    lamp2 = bpy.data.lamps['Sun']
    lamp2.shadow_method = 'NOSHADOW'
    lamp2.use_specular = False
    lamp2.energy = 0.015
    bpy.data.objects['Sun'].rotation_euler = bpy.data.objects['Lamp'].rotation_euler
    bpy.data.objects['Sun'].rotation_euler[0] += 180

    def random_point_on_sphere(r=5):
        import random
        import math
        rand = random.uniform(0, 1)
        theta = rand*math.pi*2
        phi = math.acos(rand*2-1)

        x = r*math.cos(theta)*math.sin(phi)
        y = r*math.sin(theta)*math.sin(phi)
        z = r*math.cos(phi)

        return (x,y,z)

    scene = bpy.context.scene
    scene.render.resolution_x = 600
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.alpha_mode = 'TRANSPARENT'
    cam = scene.objects['Camera']
    cam_constraint = cam.constraints.new(type='TRACK_TO')
    cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    cam_constraint.up_axis = 'UP_Y'

    # point camera to origin
    b_camera = cam
    origin = (0, 0, 0)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = origin
    b_camera.parent = b_empty  # setup parenting
    scn = bpy.context.scene
    scn.objects.link(b_empty)
    scn.objects.active = b_empty
    cam_constraint.target = b_empty

    model_identifier = os.path.split(os.path.split(obj_path)[0])[1]
    fp = os.path.join(output_folder, model_identifier, model_identifier)
    scene.render.image_settings.file_format = 'PNG'  # set output format to .png

    for output_node in [depthFileOutput, normalFileOutput]:
        output_node.base_path = ''

    for i in range(0, views):
        cam.location = (0,0,-5)#random_point_on_sphere()
        x,y,z = cam.location
        print("cam location %i, %i, %i" % (x,y,z))
        
        scene.render.filepath = fp + '{0:03d}'.format(int(i))
        depthFileOutput.file_slots[0].path = scene.render.filepath + "_depth"
        normalFileOutput.file_slots[0].path = scene.render.filepath + "_normal"
        bpy.ops.render.render(write_still=True)  # render still

cube = "models/cube.obj"
spaceship = "models/b22e56fdf18e2eb8968b65a7871de463.obj"
shell = "models/b28ae0a9ed0d3bfb28561f010f20bc5.obj"
cone = "models/b29c96cafb6b21a5df77683b81f29c56.obj"
if __name__ == "__main__":
    pass
    #render_model(cube, 3, "./images")
