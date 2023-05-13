from uploader import process_magnet
import json

# results = []
# for filename in os.listdir("postprocessing_results"):
#     if filename.endswith(".json"):
#         with open(os.path.join("postprocessing_results", filename), 'r') as f:
#             data = json.load(f)
            
#             for item in data:
#                 if 'cached' in item and 'links' in item and item['cached'] == True:
#                     results.append(item['links'][0])
#                     break

with open('results.json', 'r') as f:
    results = json.load(f)

for link in results:
    try:
        process_magnet(link)
    except:
        pass
