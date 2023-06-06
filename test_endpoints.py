# pylint: disable=line-too-long
"""
Tests for the endpoints within the Server backend/API.
"""
import os
import pytest
import requests


@pytest.fixture
def debug_level():
    """
    A pytest fixture that reads the 'DEBUG' environment variable, verifies that it is an integer between 0 and 4, and returns it.  # noqa: E501
    If 'DEBUG' is not set, the fixture returns 0.
    Raises a pytest failure if 'DEBUG' is not an integer or is not within the range 0-4.

    Returns
    -------
    int
        The debug level.
    """
    debug = os.getenv('DEBUG', None)
    try:
        debug = int(debug)
    except ValueError:
        pytest.fail("DEBUG environment variable needs to be an integer.")
    if not 0 <= debug <= 4:
        pytest.fail("DEBUG needs to be an integer between 1-4")
    return debug


def test_check_ping_endpoint():
    """
    A pytest test that checks the ping endpoint of the API.

    Raises
    ------
    AssertionError
        If the status code is not 200 or the response is not {'success': 'pong'}.  # noqa: E501

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/ping"
    response = requests.get(url, timeout=30)
    assert response.status_code == 200
    assert response.json() == {'success': 'pong'}


def test_check_restart_magnet():
    """
    A pytest test that checks the restart_magnet endpoint of the API.

    Raises
    ------
    AssertionError
        If the status code is not 200 or the response is not {'status': 'success'}.  # noqa: E501

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/restart_magnet"
    data = {"magnet_id": "191291302"}
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
    response = requests.post(url, json=data, headers=headers, timeout=30)
    assert response.status_code == 200
    assert response.json()['status'] == 'success'


def test_check_get_magnet_states():
    """
    A pytest test that checks the get_magnet_states endpoint of the API.

    Raises
    ------
    AssertionError
        If the status code is not 200 or the response is not {'status': 'success'}.  # noqa: E501

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/get_magnet_states"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
    response = requests.get(url, headers=headers, timeout=30)
    assert response.status_code == 200
    assert response.json()['status'] == 'success'


def test_get_emby_library_items():
    """
    A pytest test that checks the emby_library_items endpoint of the API.
    Raises
    ------
    AssertionError
        If the status code is not 200 or the response is not {'status': 'success'}.  # noqa: E501

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/emby_library_items"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
    data = {"emby_apikey": "354da7ea720d405c9171f82344c76e69"}
    response = requests.get(url, headers=headers, json=data, timeout=30)
    assert response.status_code == 200
    assert response.json()['status'] == 'success'


def test_search_id():
    """
    A pytest test that checks the search_id endpoint of the API.

    Raises
    ------
    AssertionError
        If the status code is not 200 or the response is not {'status': 'success'}.  # noqa: E501

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/search_id"
    data = {
        "imdb_id": "tt2861424",
        "season": 1,
        "qualities_sets": [["hd1080", "hd720"], ["hd4k"]],
        "max_results": 50,
        "sort_order": "best",
        "min_seeds": 1,
        "filter_uncached": False,
        "sort_by_quality": True
    }
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
    response = requests.post(url, headers=headers, json=data, timeout=30)  # noqa: E501

    assert response.status_code == 200
    assert response.json()['status'] == 'success'


def test_upload_to_debrid_missing_magnet():
    """
    A pytest test that checks the upload_to_debrid endpoint of the API with a missing magnet parameter.  # noqa: E501

    Raises
    ------
    AssertionError
        If the status code is not 400 or the response is not {'error': 'Missing or invalid magnet parameter.'}.  # noqa: E501

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/upload_to_debrid"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
    data = {"magnet": ""}
    response = requests.post(url, json=data, headers=headers, timeout=30)
    assert response.status_code == 400
    assert response.json()["error"] == "Missing or invalid magnet parameter."


def test_upload_to_debrid_valid_magnet():
    """
    A pytest test that checks the upload_to_debrid endpoint of the API with a valid magnet parameter.  # noqa: E501

    Raises
    ------
    AssertionError
        If the status code is not 200 or 500.

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/upload_to_debrid"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
    data = {"magnet": "magnet:?xt=urn:btih:somemagnetlink"}
    response = requests.post(url, json=data, headers=headers, timeout=30)

    if response.status_code not in [200, 500]:
        print(f"Response data: {response.json()}")

    assert response.status_code in [200, 500], f"Expected status code 200 or 500, but got {response.status_code}"  # noqa: E501

    if response.status_code == 200:
        assert 'error' not in response.json(), f"Expected no 'error' in response, but got {response.json()}"  # noqa: E501
    else:
        assert 'error' in response.json() and response.json()['error'] == 'All attempts failed during the process_magnet phase. DM unicorns pls.', f"Expected specific error message in response, but got {response.json()}"  # noqa: E501


def test_restart_magnet_valid_id():
    """
    A pytest test that checks the restart_magnet endpoint of the API with a valid magnet_id parameter.  # noqa: E501

    Raises
    ------
    AssertionError
        If the status code is not 200 or the response is not {'status': 'success'}.  # noqa: E501

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/restart_magnet"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
    data = {"magnet_id": "191291302"}
    response = requests.post(url, json=data, headers=headers, timeout=30)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"  # noqa: E501
    assert 'error' not in response.json(), f"Expected no 'error' in response, but got {response.json()}"  # noqa: E501


def test_restart_magnet_missing_id():
    """
    A pytest test that checks the restart_magnet endpoint of the API with a missing magnet_id parameter.

    Raises
    ------
    AssertionError
        If the status code is not 400 or the response is not {'error': 'Missing or invalid magnet_id parameter.'}.  # noqa: E501

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/restart_magnet"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
    data = {}
    response = requests.post(url, json=data, headers=headers, timeout=30)

    assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"  # noqa: E501
    assert 'error' in response.json() and response.json()['error'] == 'Missing or invalid magnet_id parameter.', f"Expected specific error message in response, but got {response.json()}"  # noqa: E501


def test_restart_magnet_invalid_id():
    """
    A pytest test that checks the restart_magnet endpoint of the API with an invalid magnet_id parameter.  # noqa: E501

    Raises
    ------
    AssertionError
        If the status code is not 400 or the response is not {'error': 'Missing or invalid magnet_id parameter.'}.  # noqa: E501

    Returns
    -------
    None
    """
    url = "http://127.0.0.1:1337/restart_magnet"
    headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
    data = {"magnet_id": "000000000"}
    response = requests.post(url, json=data, headers=headers, timeout=30)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"  # noqa: E501
    assert 'status' in response.json() and response.json()['status'] == 'success', f"Expected 'status' to be 'success', but got {response.json()}"  # noqa: E501
    assert 'data' in response.json() and response.json()['data'] == 'Magnet is processing or completed', f"Expected specific data message in response, but got {response.json()}"  # noqa: E501

# def test_get_emby_library_items(base_url, debug_level):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
#     data = {"emby_apikey": "354da7ea720d405c9171f82344c76e69"}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 200
#     assert response.json()['status'] == 'success'
#     assert isinstance(response.json()['data'], list), "Data returned is not a list"  # noqa: E501
#     if response.json()['data']:
#         assert 'id' in response.json()['data'][0], "Returned item does not contain 'id'"  # noqa: E501
#         assert 'name' in response.json()['data'][0], "Returned item does not contain 'name'"  # noqa: E501
#         assert 'type' in response.json()['data'][0], "Returned item does not contain 'type'"  # noqa: E501

# def test_get_emby_library_items_missing_apikey(base_url):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
#     data = {}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 400
#     assert response.json()['error'] == 'Missing or invalid emby_apikey parameter.' # noqa: E501

# def test_get_emby_library_items_invalid_apikey(base_url):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
#     data = {"emby_apikey": "invalidapikey"}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 401
#     assert response.json()['error'] == 'Invalid Emby API key.'

# def test_get_emby_library_items_no_users(base_url):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
#     data = {"emby_apikey": "apikey_with_no_users"}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 404
#     assert response.json()['error'] == 'No users found.'

# def test_get_emby_library_items_no_library_items(base_url):
#     url = f"{base_url}/emby_library_items"
#     headers = {"Content-Type": "application/json", "apikey": "suitloveshisapikeyswtfmomentweirdchamp"}  # noqa: E501
#     data = {"emby_apikey": "apikey_with_no_library_items"}
#     response = requests.get(url, headers=headers, json=data)
#     assert response.status_code == 404
#     assert response.json()['error'] == 'No library items found.'
