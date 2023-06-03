# import os

# import requests

# debug = os.getenv('DEBUG', 0)
# test = os.getenv('TEST', 0)

# if debug is None and test is None:
#     print("Both DEBUG and TEST environment variables need to be set or used when running this.")
#     exit(1)

# try:
#     debug = int(debug)
# except ValueError:
#     print("DEBUG and TEST environment variables need to be integers.")
#     exit(1)

# if not 0 <= debug <= 4:
#     print("DEBUG needs to be an integer between 1-4")
#     exit(1)

# if debug == 1:
#     print("Debug level: Low verbosity")
# elif debug == 2:
#     print("Debug level: Medium verbosity")
# elif debug == 3:
#     print("Debug level: High verbosity")
# elif debug == 4:
#     print("Debug level: Maximum verbosity")

# def check_ping_endpoint(debug):
#     """
#     Function to check if the server is running and print debug information.

#     :param debug: Debug verbosity level.
#     """
#     # Call /ping endpoint
#     url = "http://127.0.0.1:1337/ping"
#     response = requests.get(url)

#     if debug >= 3:
#         print(f"Debug: Response code: {response.status_code}")
#         print(f"Debug: Response body: {response.json()}")
#     elif debug >= 2:
#         print(f"Debug: Response code: {response.status_code}")
#     elif debug >= 1:
#         print(f"Debug: Response code: {response.status_code}")
#     else:
#         pass

#     # Check if the server is running
#     if response.status_code == 200 and response.json() == {'success': 'pong'}:
#         print("Server is running")
#     else:
#         print("Server is not running or response is not as expected")

# def check_restart_magnet(debug):
#     """
#     Function to make a POST request to the /restart_magnet endpoint and print debug information.

#     :param debug: Debug verbosity level.
#     """
#     url = "http://127.0.0.1:1337/restart_magnet"
#     data = {"magnet_id": "191291302"}
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
#     response = requests.post(url, json=data, headers=headers)

#     if debug >= 2:
#         print(f"Made POST request to {url} with data {data}")
#     if debug >= 3:
#         print(f"Response status code: {response.status_code}")
#     if debug >= 4:
#         print(f"Response content: {response.json()}")
#     else:
#         pass

#     if response.status_code == 200 and response.json()['status'] == 'success':
#         print("Restarted magnet successfully")
#     else:
#         print("Failed to restart magnet")

# def check_get_magnet_states(debug):
#     """
#     Function to make a GET request to the /get_magnet_states endpoint and print debug information.

#     :param debug: Debug verbosity level.
#     """
#     url = "http://127.0.0.1:1337/get_magnet_states"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
#     response = requests.get(url, headers=headers)

#     if debug >= 2:
#         print(f"Made GET request to {url}")
#     if debug >= 3:
#         print(f"Response status code: {response.status_code}")
#     if debug >= 4:
#         print(f"Status code: {response.status_code}")
#         print(f"Response content: {response.json()}")
#     if debug >= 1:
#         print(f"Response content: {response.json()}")
#     else:
#         pass

#     if response.status_code == 200 and response.json()['status'] == 'success':
#         print("Got magnet status successfully")
#     else:
#         print("Failed to get magnet status")

# def get_emby_library_items(debug):
#     """
#     Function to make a GET request to the /get_emby_library_items endpoint and print debug information.

#     :param debug: Debug verbosity level.
#     """
#     url = "http://127.0.0.1:1337/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
#     data = {"emby_apikey": "354da7ea720d405c9171f82344c76e69"}
#     response = requests.get(url, headers=headers, json=data)

#     if debug >= 2:
#         print(f"Made GET request to {url}")
#     if debug >= 3:
#         print(f"Response status code: {response.status_code}")
#     if debug >= 4:
#         print(f"Status code: {response.status_code}")
#         print(f"Response content: {response.json()}")
#     if debug >= 1:
#         print(f"Response content: {response.json()}")
#     else:
#         pass

#     if response.status_code == 200 and response.json()['status'] == 'success':
#         print("Got emby library items successfully")
#     else:
#         print("Failed to get emby library items")

# def test_search_id(debug):
#     """
#     Function to make a GET request to the /search_id endpoint and print debug information.

#     :param debug: Debug verbosity level.
#     """
#     imdb_id = "tt2861424"
#     url = f"http://127.0.0.1:1337/search_id"
#     params = {"imdb_id": imdb_id}
#     data = {
#         "season": 1,
#         "qualities_sets": [["hd1080", "hd720"], ["hd4k"]],
#         "max_results": 50,
#         "sort_order": "best",
#         "min_seeds": 1,
#         "filter_uncached": False,
#         "sort_by_quality": True
#     }
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
#     response = requests.post(url, headers=headers, params=params, json=data)

#     if debug >= 2:
#         print(f"Made POST request to {url}")
#     if debug >= 3:
#         print(f"Response status code: {response.status_code}")
#     if debug >= 4:
#         print(f"Status code: {response.status_code}")
#         print(f"Response content: {response.json()}")
#     if debug >= 1:
#         print(f"Response content: {response.json()}")
#     else:
#         pass

#     if response.status_code == 200 and response.json()['status'] == 'success':
#         print("Got search results successfully")
#     else:
#         print("Failed to get search results")

# def test_upload_to_debrid():
#     """
#     Function to make a POST request to the /upload_to_debrid endpoint and print debug information.

#     :param debug: Debug verbosity level.
#     """
#     url = "http://127.0.0.1:1337/upload_to_debrid"
#     # TODO: Write this function

# if test == "PING" or test == "1":
#     check_ping_endpoint(debug)
#     exit(0)
# elif test == "RESTART_MAGNET" or test == "2":
#     check_restart_magnet(debug)
#     exit(0)
# elif test == "GET_MAGNET_STATUS" or test == "3":
#     check_get_magnet_states(debug)
#     exit(0)
# elif test == "GET_EMBY_LIBRARY_ITEMS" or test == "4":
#     get_emby_library_items(debug)
#     exit(0)
# elif test == "SEARCH_ID" or test == "5":
#     test_search_id(debug)
#     exit(0)
# elif test == "UPLOAD_TO_DEBRID" or test == "6":
#     test_upload_to_debrid()
#     exit(0)
# elif test == "ALL" or test == "7":
#     print("Testing check_ping_endpoint")
#     check_ping_endpoint(debug)
#     print("Testing check_restart_magnet")
#     check_restart_magnet(debug)
#     print("Testing check_get_magnet_status")
#     check_get_magnet_states(debug)
#     print("Testing get_emby_library_items")
#     get_emby_library_items(debug)
#     print("Testing test_search_id")
#     test_search_id(debug)
#     print("Testing test_upload_to_debrid")
#     test_upload_to_debrid()
#     exit(0)
# else:
#     print("Test not implemented")
#     exit(1)

import os
import pytest
import requests

@pytest.fixture
def debug_level():
    debug = os.getenv('DEBUG', 0)
    try:
        debug = int(debug)
    except ValueError:
        pytest.fail("DEBUG environment variable needs to be an integer.")
    if not 0 <= debug <= 4:
        pytest.fail("DEBUG needs to be an integer between 1-4")
    return debug

def test_check_ping_endpoint(debug_level):
    url = "http://127.0.0.1:1337/ping"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json() == {'success': 'pong'}

def test_check_restart_magnet(debug_level):
    url = "http://127.0.0.1:1337/restart_magnet"
    data = {"magnet_id": "191291302"}
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

def test_check_get_magnet_states(debug_level):
    url = "http://127.0.0.1:1337/get_magnet_states"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

def test_get_emby_library_items(debug_level):
    url = "http://127.0.0.1:1337/emby_library_items"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
    data = {"emby_apikey": "354da7ea720d405c9171f82344c76e69"}
    response = requests.get(url, headers=headers, json=data)
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

def test_search_id(debug_level):
    imdb_id = "tt2861424"
    url = f"http://127.0.0.1:1337/search_id"
    params = {"imdb_id": imdb_id}
    data = {
        "season": 1,
        "qualities_sets": [["hd1080", "hd720"], ["hd4k"]],
        "max_results": 50,
        "sort_order": "best",
        "min_seeds": 1,
        "filter_uncached": False,
        "sort_by_quality": True
    }
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
    response = requests.post(url, headers=headers, params=params, json=data)
    assert response.status_code == 200
    assert response.json()['status'] == 'success'