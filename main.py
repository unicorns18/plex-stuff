# from orionoid import search_best_qualities
import json
import os
from orionoid import search_best_qualities
from uploader import process_magnet

with open('mdblist.json', 'r') as file:
    data = json.load(file)

directory = 'postprocessing_results/'
# QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
# FILENAME_PREFIX = "result"

# for title, imdb_id in data.items():
#     print("Searching for title: {}".format(title))
#     search_best_qualities(title=imdb_id, title_type="movie", qualities_sets=QUALITIES_SETS, filename_prefix=FILENAME_PREFIX)
#     print("Done for title: {}".format(title))

print("Done for all titles, uploading to AllDebrid now...")
magnets = {}
for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
            if len(data) > 0 and data[0].get('has_excluded_extension', False) is False:
                first_link = data[0]['links'][0]
                magnets[filename] = first_link

for title, magnet in magnets.items():
    print("Uploading for title: {}".format(title))
    process_magnet(magnet=magnet)
    print("Done for title: {}".format(title))

