import html
import inspect
import json
import os
import re
from typing import Dict
import unicodedata
import requests
from bs4 import BeautifulSoup
# import xml.etree.ElementTree as ET
from defusedxml import ElementTree as ET
import time
from constants import X_PLEX_TOKEN

from orionoid import search_best_qualities
from uploader import process_magnet

def remove_special_characters(text):
    try:
        text = text.replace("·", "-")
        # text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\uA0-\uD7FF\uE000-\uFFFD]', '', text)
        text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch == '-')
    except Exception as exc:
        print(f"Error occured while doing text processing on title: {text}, {exc}.")
        return text
    return text

def fetch_watchlist(url):
    headers = {"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache, no-store, must-revalidate"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # raise an exception if the HTTP status code is 4xx or 5xx
    except requests.RequestException as e:
        print(f"Error occurred while fetching watchlist: {e}")
        return None
    content = response.content.decode('utf-8', 'ignore')
    soup = BeautifulSoup(content, "lxml")
    videos = soup.find_all("video")
    watchlist = {}
    for video in videos:
        try:
            title = video.get("title")  # using get() method to avoid KeyError
            if title is not None and isinstance(title, str):
                title = remove_special_characters(title)
            else:
                print(f"Warning: Unexpected title '{title}' in video: {video}")
            watchlist[video["ratingkey"]] = {
                "title": title,
                "year": video.get("year", "N/A"),
                "type": video.get("type", "N/A"),
            }
        except Exception as e:
            print(f"Error occurred while processing video: {e}")
    return watchlist

def print_with_filename():
    current_frame = inspect.currentframe()
    file_path = inspect.getfile(current_frame)
    file_name = os.path.basename(file_path)
    return file_name

def get_library_ids():
    # url = f"http://88.99.242.111:32400/library/sections?X-Plex-Token={X_PLEX_TOKEN}"
    url = f"http://metadata.provider.plex.tv/library/sections?X-Plex-Token={X_PLEX_TOKEN}"
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
        # url = f"http://88.99.242.111:32400/library/sections/{library_id}/refresh?X-Plex-Token={X_PLEX_TOKEN}"
        url = f"http://metadata.provider.plex.tv/library/sections/{library_id}/refresh?X-Plex-Token={X_PLEX_TOKEN}"
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
        'X-Plex-Token': f"{X_PLEX_TOKEN}"
    }
    response = requests.put(url, params=params)
    response.raise_for_status()
    print(response.content)
    print(response.status_code)

def check_availability_and_remove_from_watchlist(item_title: str) -> bool:
    library_ids: Dict[str, str] = get_library_ids()
    for library_name, library_id in library_ids.items():
        refresh_library(library_name)
        url: str = f"http://metadata.provider.plex.tv/metadata/sections/{library_id}/all?X-Plex-Token={X_PLEX_TOKEN}"
        try:
            response: requests.Response = requests.get(url, timeout=10)
            response.raise_for_status()  # raise an exception for 4xx and 5xx HTTP status codes
        except requests.RequestException as e:
            print(f"Error occurred while fetching library data: {e}")
            continue  # skip to the next library
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            print(f"Error occurred while parsing XML: {e}")
            continue  # skip to the next library
        for video in root.iter('Video'):
            if video.get('title') == item_title:
                print(f"Item {item_title} found in {library_name} library.")
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
            if not data[0].get('has_excluded_extension', False):  # Exclude if has_excluded_extension is true
                items.append(data[0])

    for item in items:
        title = item["title"]
        link = item["links"][0]
        quality = item["quality"]
        has_excluded_extension = item["has_excluded_extension"]
        print(f"Downloading {title} from {link} in {quality} quality. (DEBUG: has_excluded_extension: {has_excluded_extension})")

        process_magnet(link)

    while True:
        if check_availability_and_remove_from_watchlist(title):
            print(f"Item {title} has been removed from the watchlist.")
            break
        else:
            print(f"Item {title} could not be found in any library, retrying in 2 seconds...")
            time.sleep(2)

    print("Finished downloading all items.")
    end_time = time.perf_counter()
    rounded_end_time = round(end_time - start_time, 2)
    print(f"Finished in {rounded_end_time} seconds. (Module {print_with_filename()})")

url = f"https://metadata.provider.plex.tv/library/sections/watchlist/all?&includeFields=title%2Ctype%2Cyear%2CratingKey&includeElements=Guid&sort=watchlistedAt%3Adesc&X-Plex-Token=GAyx53DTk4nMLyr9Mts_"
monitor_watchlist(url)


