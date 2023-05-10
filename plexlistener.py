import inspect
import json
import os
import requests
from bs4 import BeautifulSoup
import time

from orionoid import search_best_qualities
from uploader import process_magnet

def fetch_watchlist(url):
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content, "xml")
    directories = soup.find_all("Directory")
    watchlist = {}
    for directory in directories:
        watchlist[directory["ratingKey"]] = {
            "title": directory["title"],
            "year": directory["year"],
            "type": directory["type"],
        }
    return watchlist

def print_with_filename():
    current_frame = inspect.currentframe()
    file_path = inspect.getfile(current_frame)
    file_name = os.path.basename(file_path)
    return file_name

def monitor_watchlist(url):
    previous_watchlist = fetch_watchlist(url)

    while True:
        time.sleep(2)
        current_watchlist = fetch_watchlist(url)

        previous_keys = set(previous_watchlist.keys())
        current_keys = set(current_watchlist.keys())

        if current_watchlist == previous_watchlist:
            print("No changes in the watchlist.")
        else:
            new_items = current_keys - previous_keys
            for item in new_items:
                print(f"New item added: {current_watchlist[item]}")

            removed_items = previous_keys - current_keys
            for item in removed_items:
                print(f"Item removed: {previous_watchlist[item]}")

            previous_watchlist = current_watchlist

            if len(current_watchlist) > 0:
                print("An item has been detected in the watchlist. Exiting the loop.")
                break

    start_time = time.perf_counter()
    first_item_key = list(current_watchlist.keys())[0]
    QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
    FILENAME_PREFIX = "result"
    TITLE = current_watchlist[first_item_key]["title"]
    TYPE = current_watchlist[first_item_key]["type"]
    print(f"Title: {TITLE}")
    print(f"Type: {TYPE}")
    exit(0)
    search_best_qualities(title=TITLE, title_type=TYPE, qualities_sets=QUALITIES_SETS, filename_prefix=FILENAME_PREFIX)

    items = []
    for filename in os.listdir("postprocessing_results/"):
        with open(os.path.join("postprocessing_results/", filename), "r") as f:
            data = json.load(f)
            items.append(data[0])

    for item in items:
        title = item["title"]
        link = item["links"][0]
        quality = item["quality"]
        print(f"Downloading {title} from {link} in {quality} quality.")

        process_magnet(link)

    end_time = time.perf_counter()
    rounded_end_time = round(end_time - start_time, 2)
    print(f"Finished in {rounded_end_time} seconds. (Module {print_with_filename()})")

url = "https://metadata.provider.plex.tv/library/sections/watchlist/all?&includeFields=title%2Ctype%2Cyear%2CratingKey&includeElements=Guid&sort=watchlistedAt%3Adesc&&X-Plex-Token=GAyx53DTk4nMLyr9Mts_"
monitor_watchlist(url)
