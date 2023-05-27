import json
import requests
import warnings

from constants import EMBY_API_KEY

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def get_library_ids(api_key):
    response = requests.get("https://88.99.242.111/unicorns/emby/Items", params={"api_key": api_key})

    if response.status_code == 200:
        libraries = json.loads(response.text)
        return [library["Id"] for library in libraries["Items"]]
    else:
        print("Failed to get libraries.")
        return []

def refresh_library(api_key, library_id):
    headers = {
        "X-Emby-Client": "Emby Web",
        "X-Emby-Device-Name": "Google Chrome Windows",
        "X-Emby-Device-Id": "1d2debae-cfe6-4f0c-8e35-444d4ec53246",
        "X-Emby-Client-Version": "4.7.11.0",
        "X-Emby-Token": api_key,
        "X-Emby-Language": "en-us"
    }

    response = requests.post(
        f"https://88.99.242.111/unicorns/emby/Items/{library_id}/Refresh?Recursive=true&ImageRefreshMode=Default&MetadataRefreshMode=Default&ReplaceAllImages=false&ReplaceAllMetadata=false",
        headers=headers,
    )
    print(response.status_code)

    if response.status_code == 204:
        print(f"Successfully refreshed library {library_id}.")
    else:
        print(f"Failed to refresh library {library_id}.")

def refresh_all_libraries(api_key):
    library_ids = get_library_ids(api_key)
    for library_id in library_ids:
        refresh_library(api_key, library_id)

refresh_all_libraries(EMBY_API_KEY)
