# pylint: disable=C0114,C0116,C0301,W0718,C0103
import json
from torrentio import scrape
from orionoid import search
from filters import score_title
from alldebrid import check_instant_availability

title = "tt0944947"
scraped_releases = []

# Call the first method and append its output to the list
scraped_releases += scrape(title, "(.*)")

# Call the second method and append its output to the list
scraped_releases += search(title, "S01")

scraped_releases = sorted(scraped_releases, key=lambda r: r['size'], reverse=True)

# Do something with the combined list of scraped releases
with open('extended.json', 'w', encoding='utf-8') as file:
    json.dump(scraped_releases[:5], file, indent=4, ensure_ascii=False)

# # res = search(title, "(.*)")
# with open('orionoid.json', 'r', encoding='utf-8') as file:
#     res = json.load(file)
# sorted_data = sorted(res, key=lambda k: score_title(k["title"]), reverse=True)
# for r in sorted_data:
#     title = r["title"]
#     size = r["size"]
#     seeds = r["seeds"]
#     quality = r["quality"]
#     magnet = r["links"][0]
#     # print(f"Title: {title}\nSize: {size}\nSeeds: {seeds}\nQuality: {quality}\nMagnet: {magnet}\n")
#     print(f"Score: {score_title(title)} ({title})")
#     cached = check_instant_availability(magnet)
#     print(f"Cached: {cached['data']['magnets'][0]['instant']}")
