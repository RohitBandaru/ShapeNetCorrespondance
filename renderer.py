# http://web.purplefrog.com/~thoth/blender/python-cookbook/import-python.html
import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir )
    #print(sys.path)

import blender_view_render

# this next part forces a reload in case you edit the source after you first start the blender session
import importlib
importlib.reload(blender_view_render)

# this is optional and allows you to call the functions without specifying the package name
from blender_view_render import *

render_model("models/cube.obj", 3, "./images")
