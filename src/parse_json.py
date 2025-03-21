import json

path_to_file = "data/json/0007_small_img.json"

with open(path_to_file, "r") as in_file_obj:
    text = in_file_obj.read()
    # convert the text into a dictionary
    data = json.loads(text)

machine_info = data['machine_info']['cpu']
for test in range(len(data['benchmarks'])):
    print(data['benchmarks'][test]['group'])
    print(data['benchmarks'][test]['stats'])
    print(data['benchmarks'][test]['extra_info']['compression_ratio'] if 'compression_ratio' in data['benchmarks'][test]['extra_info'] else None)
