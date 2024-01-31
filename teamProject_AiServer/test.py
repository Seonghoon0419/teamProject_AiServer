import sys
import json



polygon_data_file ="point.json"

with open(polygon_data_file, 'r') as json_file:
        polygon_data = json.load(json_file)

print(polygon_data)