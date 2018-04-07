import bpy
import os

context = bpy.context

models_path = "models/"
render_path = "images/"

models = ["53323c27be8885e1cca277dcc2bd3e15.obj"]

#create a scene
scene = bpy.data.scenes.new("Scene")
camera_data = bpy.data.cameras.new("Camera")

camera = bpy.data.objects.new("Camera", camera_data)
camera.location = (-2.0, 3.0, 3.0)
camera.rotation_euler = (422.0, 0.0, 149)
scene.objects.link(camera)

# do the same for lights etc
scene.update()

for model_path in models:
    scene.camera = camera
    path = os.path.join(models_path, model_path)
    # make a new scene with cam and lights linked
    context.screen.scene = scene
    bpy.ops.scene.new(type='LINK_OBJECTS')
    context.scene.name = model_path
    cams = [c for c in context.scene.objects if c.type == 'CAMERA']
    #import model
    bpy.ops.import_scene.obj(filepath=path, axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl")
    for c in cams:
        context.scene.camera = c                                    
        print("Render ", model_path, context.scene.name, c.name)
        context.scene.render.filepath = "somepathmadeupfrommodelname"
        bpy.ops.render.render(write_still=True)