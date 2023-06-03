import json
import re
import requests
import warnings

import urllib3

from constants import EMBY_API_KEY
from exceptions import EmbyError

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def is_safe_url(url):
    trusted_domains = ['88.99.242.111']
    pattern = r'^https?://([^/:]+)'
    match = re.match(pattern, url)
    if match:
        domain = match.group(1)
        if domain in trusted_domains:
            return True
    return False

def validate_emby_apikey(apikey):
    url = f"https://88.99.242.111/unicorns/emby/Users?api_key={apikey}"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return True
    else:
        return False

def get_library_ids(api_key):
    response = requests.get("https://88.99.242.111/unicorns/emby/Items", params={"api_key": api_key}, verify=False)

    if response.status_code == 200:
        libraries = json.loads(response.text)
        print(libraries)
        return [library["Id"] for library in libraries["Items"]]
    else:
        print("Failed to get libraries.")
        return []

def get_user_ids(api_key):
    response = requests.get("https://88.99.242.111/unicorns/emby/Users", headers={"X-MediaBrowser-Token": api_key}, verify=False)

    if response.status_code == 200:
        users = json.loads(response.text)
        user_ids = [user["Id"] for user in users]
        if not user_ids:
            raise EmbyError('No users found.')
        return user_ids
    else:
        print("Failed to get users.")
        raise EmbyError('Invalid Emby API key.')


# def get_libraries(api_key, user_id):
#     url = f"https://88.99.242.111/unicorns/emby/Users/{user_id}/Items"
#     headers = {
#         "X-MediaBrowser-Token": api_key,
#         "Accept": "application/json",
#     }
#     params = {
#         "Recursive": "true",
#         "IncludeItemTypes": "Movie,Series",
#         "Fields": "BasicSyncInfo",
#     }
#     response = requests.get(url, headers=headers, params=params, verify=False)

#     if response.status_code == 200:
#         libraries = response.json()
#         if not libraries['Items']:
#             raise EmbyError('No library items found.')
#         return libraries
#     else:
#         print(f"Error {response.status_code}: {response.text}")
#         raise EmbyError('Invalid Emby API key.')
def get_libraries(api_key, user_id):
    url = f"https://88.99.242.111/unicorns/emby/Users/{user_id}/Items"
    if not is_safe_url(url):
        raise ValueError('Invalid URL.')

    headers = {
        "X-MediaBrowser-Token": api_key,
        "Accept": "application/json",
    }
    params = {
        "Recursive": "true",
        "IncludeItemTypes": "Movie,Series",
        "Fields": "BasicSyncInfo",
    }
    response = requests.get(url, headers=headers, params=params, verify=False)

    if response.status_code == 200:
        libraries = response.json()
        if not libraries['Items']:
            raise EmbyError('No library items found.')
        return libraries
    else:
        print(f"Error {response.status_code}: {response.text}")
        raise EmbyError('Invalid Emby API key.')
    
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
        verify=False
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

# if __name__ == "__main__":
#     user_ids = get_user_ids(EMBY_API_KEY)
#     if user_ids:
#         libraries = get_libraries(EMBY_API_KEY, user_ids[0])
#         if libraries:
#             for item in libraries["Items"]:
#                 print(f"{item['Id']}: {item['Name']} ({item['Type']})")
#     else:
#         print("No users found.")