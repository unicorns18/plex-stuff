# pylint: disable=C0301
"""
This module provides functionality to process magnet links using the AllDebrid API.
It checks if the magnet is instant, uploads it, and saves and deletes uptobox.com torrent links.
"""
import concurrent.futures
import json
import logging
import os
import time
from typing import Any, Dict, Iterable, List, Tuple, Union
from alldebrid import AllDebrid, APIError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_result
import requests

from constants import DEFAULT_API_KEY, EXCLUDED_EXTENSIONS, TRANSMISSION_CHECK, TRANSMISSION_HOST, TRANSMISSION_PORT

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ad = AllDebrid(apikey=DEFAULT_API_KEY)

def process_magnet(magnet: str) -> None:
    """
    Process a magnet link, check if it's instant, upload it, and save uptobox.com torrent links.

    :param magnet: The magnet link to process.
    """

    def save_link(link: str) -> None:
        """
        Save a link using the ad module.

        :param link: The link to save.
        """
        if not link or not isinstance(link, str):
            print(f"Invalid link: {link}")
            return

        try:
            res_saved_links: Dict[str, Any] = ad.save_new_link(link=link)
            if res_saved_links['status'] == 'success':
                print(f"Saved link: {link}")
            else:
                print(f"Error saving link: {link}")
        except APIError as exc:
            print(f"Error saving link: {link}: {exc}")
        except ValueError as exc:
            print(f"Error saving link: {link}: {exc}")
        except Exception as exc:
            print(f"Error saving link: {link}: {exc}")

    def filter_uptobox_links(magnet_links: List[Dict[str, str]]) -> Iterable[str]:
        """
        Filter uptobox.com links from a list of magnet links.

        :param magnet_links: A list of magnet link dictionaries.
        :return: A generator yielding uptobox.com links.
        """
        if not isinstance(magnet_links, list):
            raise ValueError("The magnet_links argument must be a list.")

        for link in magnet_links:
            if not isinstance(link, dict):
                raise ValueError(
                    "Each item in magnet_links must be a dictionary.")
            elif 'link' not in link:
                raise ValueError(
                    "Each dictionary in magnet_links must contain a 'link' key.")
            elif not isinstance(link['link'], str):
                raise ValueError(
                    "The 'link' value in the dictionaries in magnet_links must be a string.")
            elif 'uptobox.com' in link['link']:
                yield link['link']

    start_time = time.perf_counter()

    # Check if the provided magnet is in the URL format
    if magnet.startswith('http'):
        try:
            magnet = ad.download_file_then_upload_to_alldebrid(magnet)
            print(f"Magnet: {magnet}")
        except (ValueError, APIError) as exc:
            print(f"Error downloading and uploading file to AllDebrid: {exc}")
            return

    try:
        res: Dict[str, Any] = ad.check_magnet_instant(magnet)
        instant: bool = res['data']['magnets'][0]['instant']
    except (ValueError, APIError) as exc:
        print(f"Error checking magnet instant: {exc}")
        return

    if instant:
        try:
            res_upload: Dict[str, Any] = ad.upload_magnets(magnet)
            upload_id: str = res_upload['data']['magnets'][0]['id']
            res_status: Dict[str, Any] = ad.get_magnet_status(upload_id)
            torrent_links: Iterable[str] = filter_uptobox_links(
                res_status['data']['magnets']['links'])
        except (ValueError, APIError) as exc:
            print(f"Error uploading magnet or getting status: {exc}")
            return

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(save_link, link)
                           for link in torrent_links}
                for _ in concurrent.futures.as_completed(futures):
                    pass
        except (ValueError, APIError) as exc:
            print(f"Error processing torrent links: {exc}")
            return
    else:
        try:
            res_upload = ad.upload_magnets(magnet)
        except (ValueError, APIError) as exc:
            print(f"Error uploading magnet: {exc}")
            return

    end_time = time.perf_counter()
    print(f"Time elapsed: {end_time - start_time:0.4f} seconds")

def make_request(session: requests.Session, data: Dict[str, Any], retries: int = 3):
    """
    Make a POST request to the Transmission RPC server.
    
    Args:
        session: requests.Session object
        data: Dictionary containing the JSON data to be sent in the request body
        retries: Number of times to retry the request in case of failure
    
    Returns:
        response: Response object

    Raises:
        Exception: If request fails after specified number of retries
    """
    for _ in range(retries):
        try:
            response = session.post(f'http://{TRANSMISSION_HOST}:{TRANSMISSION_PORT}/transmission/rpc', json=data)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            if e.response.status_code == 409:
                # Update the session ID from the server's response
                session.headers.update({'X-Transmission-Session-Id': e.response.headers['X-Transmission-Session-Id']})
            else:
                print(f"Request failed: {e}, retrying...")
                time.sleep(0.2)
    raise Exception("Request failed after multiple retries")

def fetch_torrent_metadata(magnet_uri: Union[str, List[str]]) -> Dict[str, Any]:
    """
    Get metadata of a torrent from its magnet URI.
    
    Args:
        magnet_uri: The magnet URI of the torrent

    Returns:
        metadata: A dictionary containing the torrent's metadata

    Raises:
        Exception: If torrent addition fails
    """
    session = requests.Session()

    # Add the torrent (unpaused)
    data = {
        "method": "torrent-add",
        "arguments": {
            "filename": magnet_uri,
            "paused": False,
            "peer-limit": 10000,
            "bandwidthPriority": 1
        }
    }

    response = make_request(session, data).json()
    torrent_id = response.get('arguments', {}).get('torrent-added', {}).get('id')
    if not torrent_id:
        raise Exception("Failed to add torrent")

    start_time = time.time()
    while True:
        if time.time() - start_time >= 60:  # timeout after 60 seconds
            break

        data = {
            "method": "torrent-get",
            "arguments": {
                "ids": [torrent_id],
                "fields": ["metadataPercentComplete"]
            }
        }

        response = make_request(session, data).json()
        metadata_percent_complete = response.get('arguments', {}).get('torrents', [{}])[0].get('metadataPercentComplete')
        if metadata_percent_complete == 1:
            break

        time.sleep(0.2)

    # Pause the torrent
    data = {
        "method": "torrent-stop",
        "arguments": {
            "ids": [torrent_id]
        }
    }
    make_request(session, data)
    time.sleep(0.2)  # Ensure the torrent is paused before removal

    # Get the torrent info
    data = {
        "method": "torrent-get",
        "arguments": {
            "ids": [torrent_id],
            "fields": ["name", "hashString", "totalSize", "files"]
        }
    }
    response = make_request(session, data).json()
    torrent_info = response.get('arguments', {}).get('torrents', [{}])[0]

    # Remove the torrent
    data = {
        "method": "torrent-remove",
        "arguments": {
            "ids": [torrent_id],
            "delete-local-data": True
        }
    }
    make_request(session, data)
    metadata = {
        'name': torrent_info.get('name'),
        'total_size': torrent_info.get('totalSize'),
        'hash': torrent_info.get('hashString'),
        'files': [{'name': f['name'], 'size': f['length']} for f in torrent_info.get('files', [])]
    }

    return metadata

def is_none(result):
    return result is None
def is_error(exception):
    return isinstance(exception, (ValueError, APIError))

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry_error_callback=is_error, retry=retry_if_result(is_none))
def check_file_extensions(uri: Union[str, List[str]]) -> Tuple[bool, Union[str, None]]:
    
    # If the given URI is a string and doesn't start with 'magnet:', download and upload the file to AllDebrid
    if isinstance(uri, str) and not uri.startswith('magnet:'):
        try:
            magnet_uri = ad._download_and_upload_single_file(uri)
        except (ValueError, APIError) as exc:
            return False, f"Error downloading and uploading file to AllDebrid: {exc} (check_file_extensions)"
    else:
        magnet_uri = uri

    # Check if the magnet link is instant using AllDebrid's API
    try:
        res = ad.check_magnet_instant(magnets=uri)
    except (APIError, ValueError) as exc:
        return False, f"Error checking magnet instant: {exc}"

    # If the magnet link is instant, check the files in the magnet link for excluded extensions
    if res['data']['magnets'][0]['instant']:
        files = res['data']['magnets'][0]['files']
        excluded_files = [n['n'] for n in files for ext in EXCLUDED_EXTENSIONS if n['n'].endswith(ext)]
        if excluded_files:
            return True, f"File extension found: {excluded_files}. Extensions found: {EXCLUDED_EXTENSIONS}."
        else:
            return False, "No excluded extensions found in magnet files. (AllDebrid)"
    
    # If the magnet link is not instant and TRANSMISSION_CHECK is enabled, check the torrent metadata for excluded extensions
    elif TRANSMISSION_CHECK:
        resp = fetch_torrent_metadata(uri)
        excluded_files = [file['name'] for file in resp['files'] for ext in EXCLUDED_EXTENSIONS if file['name'].endswith(ext)]
        if excluded_files:
            return True, f"File extension found: {excluded_files}. Extensions found: {EXCLUDED_EXTENSIONS}."
        else:
            return False, "No excluded extensions found in torrent metadata. (Transmission)"
    
    # If the magnet link is not instant and TRANSMISSION_CHECK is not enabled, return a message indicating that the check is not enabled
    else:
        return False, "Transmission check is not enabled."



# def check_file_extensions(uri: Union[str, List[str]]) -> Tuple[bool, Union[str, None]]:
#     reason = "No file extensions checked yet."

#     if isinstance(uri, str) and not uri.startswith('magnet:'):
#         try:
#             magnet_uri = ad._download_and_upload_single_file(uri)
#         except (ValueError, APIError) as exc:
#             reason = f"Error downloading and uploading file to AllDebrid: {exc} (check_file_extensions)"
#             return False, reason
#     else:
#         magnet_uri = uri

#     try:
#         res =  ad.check_magnet_instant(magnets=uri)
#     except (APIError, ValueError) as exc:
#         reason = f"Error checking magnet instant: {exc}"
#         return False, reason

#     if res['data']['magnets'][0]['instant']:
#         files = res['data']['magnets'][0]['files']
#         for n in files:
#             for ext in EXCLUDED_EXTENSIONS:
#                 if n['n'].endswith(ext):
#                     reason = f"File extension found: {n['n']}. Extensions found: {ext}."
#                     return True, reason
#         reason = "No excluded extensions found in magnet files. (AllDebrid)"
#         return False, reason
#     else:
#         if TRANSMISSION_CHECK:
#             resp = fetch_torrent_metadata(uri)
#             for file in resp['files']:
#                 for ext in EXCLUDED_EXTENSIONS:
#                     if file['name'].endswith(ext):
#                         print(f"File extension found: {file['name']}. Extensions found: {ext}.")
#                         reason = f"File extension found: {file['name']}. Extensions found: {ext}."
#                         return True, reason
#             reason = "No excluded extensions found in torrent metadata. (Transmission)"
#             return False, reason
#         else:
#             reason = "Transmission check is not enabled."
#             return False, reason

# magnets = []
# for filename in os.listdir("results/"):
#     if filename.endswith(".json"):
#         with open("results/" + filename, "r") as f:
#             data = json.load(f)
#             for item in data:
#                 links = item["links"]
#                 for link in links:
#                     print(check_file_extensions(link))
