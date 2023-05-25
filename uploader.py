# pylint: disable=C0301
"""
This module provides functionality to process magnet links using the AllDebrid API.
It checks if the magnet is instant, uploads it, and saves and deletes uptobox.com torrent links.
"""
import concurrent.futures
import json
import logging
import os
import re
import time
from typing import Any, Dict, Iterable, List, Tuple, Union
from alldebrid import AllDebrid, APIError
from flask import jsonify
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_result
import requests

from constants import DEFAULT_API_KEY, EXCLUDED_EXTENSIONS, TRANSMISSION_CHECK, TRANSMISSION_HOST, TRANSMISSION_PORT

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ad = AllDebrid(apikey=DEFAULT_API_KEY)

# def process_magnet(magnet: str):
#     """
#     Process a magnet link, check if it's instant, upload it, and save uptobox.com torrent links.

#     :param magnet: The magnet link to process.
#     """

#     def save_link(link: str) -> None:
#         """
#         Save a link using the ad module.

#         :param link: The link to save.
#         """
#         if not link or not isinstance(link, str):
#             print(f"Invalid link: {link}")
#             return

#         try:
#             res_saved_links: Dict[str, Any] = ad.save_new_link(link=link)
#             if res_saved_links['status'] == 'success':
#                 print(f"Saved link: {link}")
#             else:
#                 print(f"Error saving link: {link}")
#                 raise ValueError(f"Error saving link: {link}")
#         except APIError as exc:
#             print(f"Error saving link: {link}: {exc}")
#         except ValueError as exc:
#             print(f"Error saving link: {link}: {exc}")
#         except Exception as exc:
#             print(f"Error saving link: {link}: {exc}")

#     def filter_uptobox_links(magnet_links: List[Dict[str, str]]) -> Iterable[str]:
#         """
#         Filter uptobox.com links from a list of magnet links.

#         :param magnet_links: A list of magnet link dictionaries.
#         :return: A generator yielding uptobox.com links.
#         """
#         if not isinstance(magnet_links, list):
#             raise ValueError("The magnet_links argument must be a list.")

#         for link in magnet_links:
#             if not isinstance(link, dict):
#                 raise ValueError(
#                     "Each item in magnet_links must be a dictionary.")
#             elif 'link' not in link:
#                 raise ValueError(
#                     "Each dictionary in magnet_links must contain a 'link' key.")
#             elif not isinstance(link['link'], str):
#                 raise ValueError(
#                     "The 'link' value in the dictionaries in magnet_links must be a string.")
#             elif 'uptobox.com' in link['link']:
#                 yield link['link']

#     start_time = time.perf_counter()

#     # Check if the provided magnet is in the URL format
#     if magnet.startswith('http'):
#         try:
#             magnet = ad.download_file_then_upload_to_alldebrid(magnet)
#             print(f"Magnet: {magnet}")
#         except (ValueError, APIError) as exc:
#             print(f"Error downloading and uploading file to AllDebrid: {exc}")
#             return

#     try:
#         res: Dict[str, Any] = ad.check_magnet_instant(magnet)
#         instant: bool = res['data']['magnets'][0]['instant']
#     except (ValueError, APIError) as exc:
#         print(f"Error checking magnet instant: {exc}")
#         return

#     if instant:
#         try:
#             res_upload: Dict[str, Any] = ad.upload_magnets(magnet)
#             upload_id: str = res_upload['data']['magnets'][0]['id']
#             res_status: Dict[str, Any] = ad.get_magnet_status(upload_id)
#             torrent_links: Iterable[str] = filter_uptobox_links(
#                 res_status['data']['magnets']['links'])
#         except (ValueError, APIError) as exc:
#             print(f"Error uploading magnet or getting status: {exc}")
#             return

#         try:
#             with concurrent.futures.ThreadPoolExecutor() as executor:
#                 futures = {executor.submit(save_link, link)
#                            for link in torrent_links}
#                 for _ in concurrent.futures.as_completed(futures):
#                     pass
#         except (ValueError, APIError) as exc:
#             print(f"Error processing torrent links: {exc}")
#             return
#     else:
#         try:
#             res_upload = ad.upload_magnets(magnet)
#         except (ValueError, APIError) as exc:
#             print(f"Error uploading magnet: {exc}")
#             return

#     end_time = time.perf_counter()
#     print(f"Time elapsed: {end_time - start_time:0.4f} seconds")
def process_magnet(magnet: str):
    """
    Process a magnet link, check if it's instant, upload it, and save uptobox.com torrent links.

    :param magnet: The magnet link to process.
    """
    success_response = jsonify({'success': 'Successfully uploaded to debrid.'})
    error_response = jsonify({'error': 'Something went wrong during the process_magnet phase. DM unicorns pls.'})

    def save_link(link: str) -> None:
        """
        Save a link using the ad module.

        :param link: The link to save.
        """
        if not link or not isinstance(link, str):
            print(f"Invalid link: {link}")
            raise ValueError(f"Invalid link: {link}")

        try:
            res_saved_links: Dict[str, Any] = ad.save_new_link(link=link)
            if res_saved_links['status'] == 'success':
                print(f"Saved link: {link}")
            else:
                print(f"Error saving link: {link}")
                raise ValueError(f"Error saving link: {link}")
        except APIError as exc:
            print(f"Error saving link: {link}: {exc}")
            raise
        except ValueError as exc:
            print(f"Error saving link: {link}: {exc}")
            raise
        except Exception as exc:
            print(f"Error saving link: {link}: {exc}")
            raise

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
                raise ValueError("Each item in magnet_links must be a dictionary.")
            elif 'link' not in link:
                raise ValueError("Each dictionary in magnet_links must contain a 'link' key.")
            elif not isinstance(link['link'], str):
                raise ValueError("The 'link' value in the dictionaries in magnet_links must be a string.")
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
            return error_response, 500

    try:
        res: Dict[str, Any] = ad.check_magnet_instant(magnet)
        instant: bool = res['data']['magnets'][0]['instant']
    except (ValueError, APIError) as exc:
        print(f"Error checking magnet instant: {exc}")
        return error_response, 500

    if instant:
        try:
            res_upload: Dict[str, Any] = ad.upload_magnets(magnet)
            upload_id: str = res_upload['data']['magnets'][0]['id']
            res_status: Dict[str, Any] = ad.get_magnet_status(upload_id)
            torrent_links: Iterable[str] = filter_uptobox_links(res_status['data']['magnets']['links'])
        except (ValueError, APIError) as exc:
            print(f"Error uploading magnet or getting status: {exc}")
            return error_response, 500

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(save_link, link) for link in torrent_links}
                for _ in concurrent.futures.as_completed(futures):
                    pass
        except (ValueError, APIError) as exc:
            print(f"Error processing torrent links: {exc}")
            return error_response, 500
    else:
        try:
            res_upload = ad.upload_magnets(magnet)
        except (ValueError, APIError) as exc:
            print(f"Error uploading magnet: {exc}")
            return error_response, 500

    end_time = time.perf_counter()
    print(f"Time elapsed: {end_time - start_time:0.4f} seconds")

    return success_response, 200


def debrid_persistence_checks(title: str):
    response = ad.saved_links()

    if response['status'] == 'success':
        links = response['data']['links']
        filtered_links = [link for link in links if title.lower() in link['filename'].lower()]
        return {'status': 'success', 'data': {'links': filtered_links}}
    else:
        return {'status': 'error', 'message': 'Failed to retrieve saved links.'}

def extract_title_from_magnets_dn(magnet: str) -> str:
    """
    Extracts the title from the magnet's display name.

    :param magnet: The magnet link.
    :return: The title.
    """
    title = ""
    # Patterns for different variations of the title
    patterns = [
        r"&dn=([^&]+)",                           # Pattern 1: Extract text after '&dn=' until the next '&'
        r"%5B([^%]+)%5D",                         # Pattern 2: Extract text between '%5B' and '%5D'
        r"(\[[^\]]+\])",                          # Pattern 3: Extract text between '[' and ']'
        r"(?:www\.[^.]+\.[^.]+\.[^.]+\/)([^\/]+)"  # Pattern 4: Extract text after the third '.' and before '/'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, magnet)
        if match:
            title = match.group(1)
            break
    
    # Remove unwanted characters like '%20' or '%5B'
    title = re.sub(r"%\w{2}", " ", title)
    
    return title.strip()

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

def fetch_torrent_metadata(magnet_uri: Union[str, List[str]], timeout: int = 60) -> Dict[str, Any]:
    """
    Get metadata of a torrent from its magnet URI.

    Args:
        magnet_uri: The magnet URI of the torrent
        timeout: The number of seconds to wait for metadata to be obtained

    Returns:
        metadata: A dictionary containing the torrent's metadata

    Raises:
        Exception: If torrent addition fails or if metadata cannot be obtained within the timeout period
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

    try:
        response = make_request(session, data).json()
        torrent_id = response['arguments']['torrent-added']['id']
    except (KeyError, ValueError):
        raise Exception("Failed to add torrent")

    try:
        start_time = time.time()
        while True:
            if time.time() - start_time >= timeout:
                raise Exception("Failed to get metadata within timeout period")

            data = {
                "method": "torrent-get",
                "arguments": {
                    "ids": [torrent_id],
                    "fields": ["name", "hashString", "totalSize", "files"]
                }
            }

            response = make_request(session, data).json()
            torrent_info = response['arguments']['torrents'][0]
            if torrent_info['metadataPercentComplete'] == 1:
                break

    except (KeyError, ValueError):
        raise Exception("Failed to get metadata")

    # Get the torrent info
    metadata = {
        'name': torrent_info.get('name'),
        'total_size': torrent_info.get('totalSize'),
        'hash': torrent_info.get('hashString'),
        'files': [{'name': f['name'], 'size': f['length']} for f in torrent_info.get('files', [])]
    }

    # Remove the torrent
    data = {
        "method": "torrent-remove",
        "arguments": {
            "ids": [torrent_id],
            "delete-local-data": True
        }
    }
    make_request(session, data)

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
