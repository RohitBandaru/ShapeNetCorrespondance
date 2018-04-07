import csv
import json
import collections
import renderer

def is3D(model):
	dims = list(map(float, str.split(model['aligned.dims'], '\,') ))
	for dim in dims:
		if dim == 0.0:
			return False
	return True

print("hi")
with open('metadata.csv', 'r') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	header = next(reader)
	#print(header)
	'''nocatnames = []
	category_ids = {}
	category_counts = collections.OrderedDict()
	for model in reader:
		# skip 2D models, 70 in total
		if not is3D(model):
			continue

		id = model['fullId'][4:]
		categories = str.split(model['category'], ',')

		primary_category = categories[0]
		if(primary_category==""):
			primary_category = "ETC"

		if primary_category in category_ids:
			category_ids[primary_category].append(id)
		else:
			category_ids[primary_category] = [id]

	cat_lengths = [ (len(v),k) for k,v in category_ids.items() ]
	cat_lengths.sort(reverse=True) # natively sort tuples by first element

	for cat_size, cat in cat_lengths:
		category_counts[cat] = cat_size
'''
	#print(category_counts)
	'''with open('category_counts.json', 'w') as file:
		json.dump(category_counts, file, indent=2)

	'''
	'''import numpy as np
	import matplotlib.pyplot as plt
	plt.hist(cat_sizes,bins='auto')
	plt.show()
	print(cat_sizes)
	'''



	#filtered_cats = dict((key,value) for key, value in category_ids.items() if len(value)>100)
	#print(filtered_cats)

def render(ids, output_path):
	pass