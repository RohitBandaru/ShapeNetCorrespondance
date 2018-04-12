import pandas as pd
import json
# http://web.purplefrog.com/~thoth/blender/python-cookbook/import-python.html
'''import bpy
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
'''
csv_input = pd.read_csv('metadata2.csv')

def render_category(category_name, views, number_of_models):
	# get ids
	ids = csv_input[csv_input["category"] == category_name]["fullId"]
	number_of_models = min(number_of_models, ids.shape[0])

	for i,id in enumerate(ids):
		if(i >= number_of_models):
			break
		print("rendering " + id)
		#render_model("models/"+id+".obj", views, "./images")

with open('category_counts.json', 'r') as file:
	data = json.load(file)
	for row in data:
		count = data[row]
		if(count>50):
			render_category(row, 6, 50)


