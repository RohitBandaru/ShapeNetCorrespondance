import pandas as pd

csv_input = pd.read_csv('metadata.csv')
out = pd.DataFrame()

out['category'] = csv_input['category'].fillna('NaN').apply(lambda x: str.split(x, ',')[0])
out['fullId'] = csv_input['fullId'].apply(lambda x: str.split(x, '.')[1])

out['aligned.dims'] = csv_input['aligned.dims'].apply(lambda x: "" if (min(list(map(float, str.split(x, '\,')))) == 0) else x ) 
out = out[csv_input['aligned.dims'] != ""]
out = out.drop(['aligned.dims'],1)

out.to_csv('metadata2.csv', index=False)


import csv
import json
import collections

def is3D(model):
	dims = list(map(float, str.split(model['aligned.dims'], '\,') ))
	for dim in dims:
		if dim == 0.0:
			return False
	return True
with open('metadata.csv', 'r') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	header = next(reader)
	nocatnames = []
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
	'''
	with open('category_counts.json', 'w') as file:
		json.dump(category_counts, file, indent=2)

