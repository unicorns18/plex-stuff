import inspect
import json
import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time

from orionoid import search_best_qualities
from uploader import process_magnet

def fetch_watchlist(url):
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content, "xml")
    directories = soup.find_all("Video")
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

def get_library_ids():
    url = f"http://88.99.242.111:32400/library/sections?X-Plex-Token=GAyx53DTk4nMLyr9Mts_"
    response = requests.get(url)
    root = ET.fromstring(response.content)

    library_ids = {}
    for child in root:
        library_ids[child.attrib['title']] = child.attrib['key']

    return library_ids

def refresh_library(library_name):
    library_ids = get_library_ids()
    library_id = library_ids.get(library_name)
    if library_id:
        url = f"http://88.99.242.111:32400/library/sections/{library_id}/refresh?X-Plex-Token=GAyx53DTk4nMLyr9Mts_"
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Successfully refreshed {library_name} library!")
        else:
            print(f"Failed to refresh {library_name} library.")
    else:
        print(f"No library found with name {library_name}.")

def remove_from_watchlist(item_rating_key):
    url = f"http://metadata.provider.plex.tv/actions/removeFromWatchlist"
    params = {
        'ratingKey': item_rating_key,
        'X-Plex-Token': "GAyx53DTk4nMLyr9Mts_"
    }
    response = requests.put(url, params=params)
    response.raise_for_status()
    print(response.content)
    print(response.status_code)

def check_availability_and_remove_from_watchlist(item_title):
    library_ids = get_library_ids()
    for library_name, library_id in library_ids.items():
        refresh_library(library_name)
        url = f"http://88.99.242.111:32400/library/sections/{library_id}/all?X-Plex-Token=GAyx53DTk4nMLyr9Mts_"
        response = requests.get(url)
        root = ET.fromstring(response.content)
        for video in root.iter('Video'):
            if video.get('title') == item_title:
                print(f"Item {item_title} found in {library_name} library.")
                # Assuming we have a function remove_from_watchlist to remove the item
                remove_from_watchlist(item_title)
                return True
    print(f"Item {item_title} not found in any library.")
    return False

def monitor_watchlist(url):
    previous_watchlist = {}
    previous_watchlist = fetch_watchlist(url)

    while True:
        time.sleep(2)
        current_watchlist = fetch_watchlist(url)
        print(f"Current watchlist: {current_watchlist}")

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
    TITLE = current_watchlist[first_item_key]["title"]
    TYPE = current_watchlist[first_item_key]["type"]
    print(f"Title: {TITLE}")
    print(f"Type: {TYPE}")
    exit(0)
    QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
    FILENAME_PREFIX = "result"
    search_best_qualities(title=TITLE, title_type=TYPE, qualities_sets=QUALITIES_SETS, filename_prefix=FILENAME_PREFIX)

    items = []
    for filename in os.listdir("results/"):
        with open(os.path.join("results/", filename), "r") as f:
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

url = "https://metadata.provider.plex.tv/library/sections/watchlist/all?&includeFields=title%2Ctype%2Cyear%2CratingKey&includeElements=Guid&sort=watchlistedAt%3Adesc&X-Plex-Token=sxkzRsW9JtHSUy-Dne6s"
monitor_watchlist(url)
