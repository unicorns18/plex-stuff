"""
Wrapper for Emby API.
"""
# pylint: disable=C0301
import json
import re
import warnings
import requests
from exceptions import EmbyError

warnings.filterwarnings("ignore", message="Unverified HTTPS request")


def is_safe_url(url):
    """
    This function checks whether a given URL is safe based on its domain.

    :param url: The URL to be checked.
    :return: True if the domain of the URL is in the trusted list, False otherwise.  # noqa: E501
    """
    trusted_domains = ["88.99.242.111"]
    pattern = r"^https?://([^/:]+)"
    match = re.match(pattern, url)
    return bool(match and match.group(1) in trusted_domains)


def validate_emby_apikey(apikey):
    """
    This function validates an Emby API key by sending a GET request to the Emby server.  # noqa: E501

    :param apikey: The Emby API key to be validated.
    :return: True if the API key is valid (i.e., the server returns a 200 status code), False otherwise.  # noqa: E501
    """
    url = f"https://88.99.242.111/unicorns/emby/Users?api_key={apikey}"
    response = requests.get(url, verify=False, timeout=30)
    return response.status_code == 200


def get_library_ids(api_key):
    """
    This function retrieves the IDs of all libraries in the Emby server using a given API key.  # noqa: E501

    :param api_key: The API key to be used for the request.
    :return: A list of library IDs if the server returns a 200 status code, an empty list otherwise.  # noqa: E501
    """
    response = requests.get(
        "https://88.99.242.111/unicorns/emby/Items",
        params={"api_key": api_key},
        verify=False,
        timeout=30,
    )

    if response.status_code != 200:
        print("Failed to get libraries.")
        return []
    libraries = json.loads(response.text)
    print(libraries)
    return [library["Id"] for library in libraries["Items"]]


def get_user_ids(api_key):
    """
    This function retrieves the IDs of all users in the Emby server using a given API key.  # noqa: E501

    :param api_key: The API key to be used for the request.
    :return: A list of user IDs if the server returns a 200 status code. Raises an EmbyError if no users are found or if the API key is invalid.
    """
    response = requests.get(
        "https://88.99.242.111/unicorns/emby/Users",
        headers={"X-MediaBrowser-Token": api_key},
        verify=False,
        timeout=30,
    )

    if response.status_code != 200:
        print("Failed to get users.")
        raise EmbyError("Invalid Emby API key.")

    users = json.loads(response.text)
    user_ids = [user["Id"] for user in users]
    if not user_ids:
        raise EmbyError("No users found.")
    return user_ids


def get_libraries(api_key, user_id):
    """
    This function retrieves the libraries of a specific user in the Emby server using a given API key.

    :param api_key: The API key to be used for the request.
    :param user_id: The ID of the user whose libraries are to be retrieved.
    :return: The libraries if the server returns a 200 status code. Raises an EmbyError if no library items are found or if the API key is invalid. # noqa: E501
    """
    url = f"https://88.99.242.111/unicorns/emby/Users/{user_id}/Items"
    if not is_safe_url(url):
        raise ValueError("Invalid URL.")

    headers = {
        "X-MediaBrowser-Token": api_key,
        "Accept": "application/json",
    }
    params = {
        "Recursive": "true",
        "IncludeItemTypes": "Movie,Series",
        "Fields": "BasicSyncInfo",
    }
    response = requests.get(
        url, headers=headers, params=params, verify=False, timeout=30
    )  # noqa: E501

    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        raise EmbyError("Invalid Emby API key.")

    libraries = response.json()
    if not libraries["Items"]:
        raise EmbyError("No library items found.")
    return libraries


def refresh_library(api_key, library_id):
    """
    This function refreshes a specific library in the Emby server using a given API key. # noqa: E501

    :param api_key: The API key to be used for the request.
    :param library_id: The ID of the library to be refreshed.
    """
    headers = {
        "X-Emby-Client": "Emby Web",
        "X-Emby-Device-Name": "Google Chrome Windows",
        "X-Emby-Device-Id": "1d2debae-cfe6-4f0c-8e35-444d4ec53246",
        "X-Emby-Client-Version": "4.7.11.0",
        "X-Emby-Token": api_key,
        "X-Emby-Language": "en-us",
    }

    response = requests.post(
        f"https://88.99.242.111/unicorns/emby/Items/{library_id}/Refresh?Recursive=true&ImageRefreshMode=Default&MetadataRefreshMode=Default&ReplaceAllImages=false&ReplaceAllMetadata=false",  # noqa: E501
        headers=headers,
        verify=False,
        timeout=30,
    )
    print(response.status_code)

    if response.status_code == 204:
        print(f"Successfully refreshed library {library_id}.")
    else:
        print(f"Failed to refresh library {library_id}.")


def refresh_all_libraries(api_key):
    """
    This function refreshes all libraries in the Emby server using a given API key. # noqa: E501

    :param api_key: The API key to be used for the request.
    """
    library_ids = get_library_ids(api_key)
    for library_id in library_ids:
        refresh_library(api_key, library_id)
