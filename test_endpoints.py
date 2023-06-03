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

@pytest.fixture
def base_url():
    return "http://127.0.0.1:1337"

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

def test_upload_to_debrid_missing_magnet(base_url):
    url = f"{base_url}/upload_to_debrid"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
    data = {"magnet": ""}
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400
    assert response.json()["error"] == "Missing or invalid magnet parameter."

def test_upload_to_debrid_valid_magnet(base_url):
    url = f"{base_url}/upload_to_debrid"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
    data = {"magnet": "magnet:?xt=urn:btih:somemagnetlink"}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code not in [200, 500]:
        print(f"Response data: {response.json()}")

    assert response.status_code in [200, 500], f"Expected status code 200 or 500, but got {response.status_code}"

    if response.status_code == 200:
        assert 'error' not in response.json(), f"Expected no 'error' in response, but got {response.json()}"
    else: 
        assert 'error' in response.json() and response.json()['error'] == 'All attempts failed during the process_magnet phase. DM unicorns pls.', f"Expected specific error message in response, but got {response.json()}"

def test_restart_magnet_valid_id(base_url):
    url = f"{base_url}/restart_magnet"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
    data = {"magnet_id": "191291302"}
    response = requests.post(url, json=data, headers=headers)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    assert 'error' not in response.json(), f"Expected no 'error' in response, but got {response.json()}"

def test_restart_magnet_missing_id(base_url):
    url = f"{base_url}/restart_magnet"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
    data = {}
    response = requests.post(url, json=data, headers=headers)

    assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
    assert 'error' in response.json() and response.json()['error'] == 'Missing or invalid magnet_id parameter.', f"Expected specific error message in response, but got {response.json()}"

def test_restart_magnet_invalid_id(base_url):
    url = f"{base_url}/restart_magnet"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
    data = {"magnet_id": "000000000"}
    response = requests.post(url, json=data, headers=headers)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    assert 'status' in response.json() and response.json()['status'] == 'success', f"Expected 'status' to be 'success', but got {response.json()}"
    assert 'data' in response.json() and response.json()['data'] == 'Magnet is processing or completed', f"Expected specific data message in response, but got {response.json()}"

# def test_get_emby_library_items(base_url, debug_level):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
#     data = {"emby_apikey": "354da7ea720d405c9171f82344c76e69"}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 200
#     assert response.json()['status'] == 'success'
#     assert isinstance(response.json()['data'], list), "Data returned is not a list"
#     if response.json()['data']:
#         assert 'id' in response.json()['data'][0], "Returned item does not contain 'id'"
#         assert 'name' in response.json()['data'][0], "Returned item does not contain 'name'"
#         assert 'type' in response.json()['data'][0], "Returned item does not contain 'type'"

# def test_get_emby_library_items_missing_apikey(base_url):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
#     data = {}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 400
#     assert response.json()['error'] == 'Missing or invalid emby_apikey parameter.'

# def test_get_emby_library_items_invalid_apikey(base_url):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
#     data = {"emby_apikey": "invalidapikey"}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 401
#     assert response.json()['error'] == 'Invalid Emby API key.'

# def test_get_emby_library_items_no_users(base_url):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
#     data = {"emby_apikey": "apikey_with_no_users"}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 404
#     assert response.json()['error'] == 'No users found.'

# def test_get_emby_library_items_no_library_items(base_url):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}
#     data = {"emby_apikey": "apikey_with_no_library_items"}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 404
#     assert response.json()['error'] == 'No library items found.'
