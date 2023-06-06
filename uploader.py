# pylint: disable=C0301
"""
This module provides functionality to process magnet links using the AllDebrid API.  # noqa: E501
It checks if the magnet is instant, uploads it, and saves and deletes uptobox.com torrent links.  # noqa: E501
"""
import concurrent.futures
import logging
import re
import time
from typing import Any, Dict, List, Tuple, Union
from urllib.parse import unquote, urlparse
from alldebrid import AllDebrid, APIError
from flask import jsonify
import requests

from constants import (
    DEFAULT_API_KEY,
    EXCLUDED_EXTENSIONS,
    TRANSMISSION_CHECK,
    TRANSMISSION_HOST,
    TRANSMISSION_PORT,
)
from exceptions import MetadataError, TorrentAddError, TransmissionError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ad = AllDebrid(apikey=DEFAULT_API_KEY)


def filter_uptobox_links(magnet_links: List[Dict[str, str]]) -> List[str]:
    """
    Filter uptobox.com links from a list of magnet links.

    :param magnet_links: A list of magnet link dictionaries.
    :return: A list of uptobox.com links.
    """
    if not isinstance(magnet_links, list):
        raise ValueError("The magnet_links argument must be a list.")

    uptobox_links = []

    for link in magnet_links:
        if not isinstance(link, dict):
            raise ValueError("Each item in magnet_links must be a dictionary.")
        if "link" not in link:
            raise ValueError(
                "Each dictionary in magnet_links must contain a 'link' key."
            )
        if not isinstance(link["link"], str):
            raise ValueError(
                "The 'link' value in the dictionaries in magnet_links must be a string."
            )
        if "uptobox.com" in link["link"]:
            uptobox_links.append(link["link"])

    return uptobox_links


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
        if res_saved_links["status"] == "success":
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


def get_magnet_from_url(magnet):
    """
    If the magnet is a URL, it downloads and uploads the file to AllDebrid.

    :param magnet: The magnet link to process.
    :return: The processed magnet link.
    """
    if magnet.startswith("http"):
        try:
            magnet = ad.download_file_then_upload_to_alldebrid(magnet)
            print(f"Magnet: {magnet}")
        except (ValueError, APIError) as exc:
            print(f"Error downloading and uploading file to AllDebrid: {exc}")
            return None
    return magnet


def check_magnet_instant(magnet: str) -> bool:
    """
    Checks if the magnet link is instant.

    :param magnet: The magnet link to process.
    :return: A boolean indicating if the magnet link is instant.
    """
    try:
        res: Dict[str, Any] = ad.check_magnet_instant(magnet)
        if (
            "data" in res
            and "magnets" in res["data"]
            and len(res["data"]["magnets"]) > 0
            and "instant" in res["data"]["magnets"][0]
        ):
            return res["data"]["magnets"][0]["instant"]
    except (ValueError, APIError) as exc:
        print(f"Error checking magnet instant: {exc}")
    return None


def upload_magnet_and_get_links(magnet: str) -> List[str]:
    """
    Uploads the magnet link and returns the torrent links.

    :param magnet: The magnet link to process.
    :return: A list of torrent links.
    """
    try:
        res_upload: Dict[str, Any] = ad.upload_magnets(magnet)
        upload_id: str = res_upload["data"]["magnets"][0]["id"]
        res_status: Dict[str, Any] = ad.get_magnet_status(upload_id)
        return filter_uptobox_links(res_status["data"]["magnets"]["links"])
    except (ValueError, APIError) as exc:
        print(f"Error uploading magnet or getting status: {exc}")
        return None


def process_magnet(magnet: str):
    """
    Process a magnet link, check if it's instant, upload it, and save uptobox.com torrent links.

    :param magnet: The magnet link to process.
    """
    success_response = jsonify({"success": "Successfully uploaded to debrid."})
    error_response = jsonify(
        {
            "error": "Something went wrong during the process_magnet phase. DM unicorns pls."
        }
    )

    start_time = time.perf_counter()

    magnet = get_magnet_from_url(magnet)
    if magnet is None:
        return error_response, 500

    instant = check_magnet_instant(magnet)
    if instant is None:
        return error_response, 500

    torrent_links = upload_magnet_and_get_links(magnet)
    if torrent_links is None:
        return error_response, 500

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(save_link, link) for link in torrent_links}
            for _ in concurrent.futures.as_completed(futures):
                pass
    except (ValueError, APIError) as exc:
        print(f"Error processing torrent links: {exc}")
        return error_response, 500

    end_time = time.perf_counter()
    print(f"Time elapsed: {end_time - start_time:0.4f} seconds")

    return success_response, 200


def debrid_persistence_checks(title: str):
    """
    This method checks the persistence of debrid links. It goes through saved links and filters
    out the ones relevant to the provided title. It assigns a confidence score to each relevant
    link based on the number of words from the title found in the link's filename.

    Parameters
    ----------
    title : str
        The title to check for in the filenames of the saved links.

    Returns
    -------
    dict
        If the status of the response is "success", it returns a dictionary with a "status"
        key set to "success" and a "data" key containing a list of filtered links. Each link
        in the list is a dictionary with a "confidence" key added, indicating how many words
        from the title were found in the filename.

        If the status of the response is not "success", it returns a dictionary with a "status"
        key set to "error" and a "message" key set to "Failed to retrieve saved links."
    """
    response = ad.saved_links()

    if response["status"] == "success":
        links = response["data"]["links"]

        filtered_links = []
        for link in links:
            filename = link["filename"].lower()
            confidence = 0
            title_words = title.lower().split(" ")

            for word in title_words:
                if word in filename:
                    confidence += (
                        10  # Increment confidence by 10 for each matching word
                    )

            # Only add links to the filtered list if confidence is greater than 0
            if confidence > 0:
                link["confidence"] = confidence  # Add a confidence score to the link
                filtered_links.append(link)

        return {"status": "success", "data": {"links": filtered_links}}

    return {
        "status": "error",
        "message": "Failed to retrieve saved links.",
    }


def extract_title_from_magnets_dn(magnet: str) -> str:
    """
    Extracts the title from the magnet's display name.

    :param magnet: The magnet link.
    :return: The title.
    """
    title = ""
    # Patterns for different variations of the title
    patterns = [
        r"&dn=([^&]+)",  # Pattern 1: Extract text after '&dn=' until the next '&'  # noqa: E501
        r"%5B([^%]+)%5D",  # Pattern 2: Extract text between '%5B' and '%5D'
        r"(\[[^\]]+\])",  # Pattern 3: Extract text between '[' and ']'
        r"(?:www\.[^.]+\.[^.]+\.[^.]+\/)([^\/]+)",  # Pattern 4: Extract text after the third '.' and before '/'  # noqa: E501
    ]

    for pattern in patterns:
        match = re.search(pattern, magnet)
        if match:
            title = match.group(1)
            break

    # Decode the URL-encoded string
    title = unquote(title)

    # Replace unwanted characters like dots or minuses with space
    title = re.sub(r"\.|-|_", " ", title)

    return title.strip()


def make_request(
    session: requests.Session, data: Dict[str, Any], retries: int = 3
):  # noqa: E501
    """
    Make a POST request to the Transmission RPC server.

    Args:
        session: requests.Session object
        data: Dictionary containing the JSON data to be sent in the request body  # noqa: E501
        retries: Number of times to retry the request in case of failure

    Returns:
        response: Response object

    Raises:
        Exception: If request fails after specified number of retries
    """
    for _ in range(retries):
        try:
            response = session.post(
                f"http://{TRANSMISSION_HOST}:{TRANSMISSION_PORT}/transmission/rpc",  # noqa: E501
                json=data,
            )
            response.raise_for_status()
            return response
        except requests.HTTPError as exc:
            if exc.response.status_code == 409:
                # Update the session ID from the server's response
                session.headers.update(
                    {
                        "X-Transmission-Session-Id": exc.response.headers[
                            "X-Transmission-Session-Id"
                        ]
                    }
                )
            else:
                print(f"Request failed: {exc}, retrying...")
                time.sleep(0.2)
    raise TransmissionError("Request failed after multiple retries")


def fetch_torrent_metadata(
    magnet_uri: Union[str, List[str]], timeout: int = 60
) -> Dict[str, Any]:
    """
    Get metadata of a torrent from its magnet URI.

    Args:
        magnet_uri: The magnet URI of the torrent
        timeout: The number of seconds to wait for metadata to be obtained

    Returns:
        metadata: A dictionary containing the torrent's metadata

    Raises:
        Exception: If torrent addition fails or if metadata cannot be obtained within the timeout period  # noqa: E501
    """
    session = requests.Session()

    # Add the torrent (unpaused)
    data = {
        "method": "torrent-add",
        "arguments": {
            "filename": magnet_uri,
            "paused": False,
            "peer-limit": 10000,
            "bandwidthPriority": 1,
        },
    }

    try:
        response = make_request(session, data).json()
        torrent_id = response["arguments"]["torrent-added"]["id"]
    except (KeyError, ValueError) as exc:
        raise TorrentAddError("Failed to add torrent") from exc

    try:
        start_time = time.time()
        while True:
            if time.time() - start_time >= timeout:
                raise MetadataError(
                    "Failed to get metadata within timeout period"
                )  # noqa: E501

            data = {
                "method": "torrent-get",
                "arguments": {
                    "ids": [torrent_id],
                    "fields": ["name", "hashString", "totalSize", "files"],
                },
            }

            response = make_request(session, data).json()
            torrent_info = response["arguments"]["torrents"][0]
            if torrent_info["metadataPercentComplete"] == 1:
                break
    except (KeyError, ValueError) as exc:
        raise MetadataError("Failed to get metadata") from exc

    # Get the torrent info
    metadata = {
        "name": torrent_info.get("name"),
        "total_size": torrent_info.get("totalSize"),
        "hash": torrent_info.get("hashString"),
        "files": [
            {"name": f["name"], "size": f["length"]}
            for f in torrent_info.get("files", [])
        ],
    }

    # Remove the torrent
    data = {
        "method": "torrent-remove",
        "arguments": {"ids": [torrent_id], "delete-local-data": True},
    }
    make_request(session, data)

    return metadata


def is_none(result):
    """
    Returns True if the result is None, False otherwise.
    """
    return result is None


def is_error(exception):
    """
    Returns True if the exception is an instance of ValueError or APIError, False otherwise.  # noqa: E501
    """
    return isinstance(exception, (ValueError, APIError))


def get_magnet_instant_data(magnet_uri):
    """
    Calls a method from `ad` to check the magnet link instantaneously.

    Parameters
    ----------
    magnet_uri: str
        Magnet URI link.

    Returns
    -------
    dict, str
        Response dictionary from the `ad.check_magnet_instant` method, and error message if any.
    """
    try:
        return ad.check_magnet_instant(magnets=magnet_uri)
    except (APIError, ValueError) as exc:
        return False, f"Error checking magnet instant: {exc}"

def fetch_excluded_files_from_magnet_data(magnet_data):
    """
    Fetches files from magnet data that have extensions included in the EXCLUDED_EXTENSIONS list.

    Parameters
    ----------
    magnet_data: dict
        Response dictionary from the `ad.check_magnet_instant` method.

    Returns
    -------
    list
        List of files that have extensions included in the EXCLUDED_EXTENSIONS list.
    """
    files = magnet_data["data"]["magnets"][0]["files"]
    return [
        n["n"]
        for n in files
        for ext in EXCLUDED_EXTENSIONS
        if n["n"].endswith(ext)
    ]

def fetch_excluded_files_from_torrent_data(torrent_data):
    """
    Fetches files from torrent metadata that have extensions included in the EXCLUDED_EXTENSIONS list.

    Parameters
    ----------
    torrent_data: dict
        Response dictionary from the `fetch_torrent_metadata` method.

    Returns
    -------
    list
        List of files that have extensions included in the EXCLUDED_EXTENSIONS list.
    """
    return [
        file["name"]
        for file in torrent_data["files"]
        for ext in EXCLUDED_EXTENSIONS
        if file["name"].endswith(ext)
    ]

def generate_result_with_excluded_files(excluded_files, source):
    """
    Generates the result message based on whether excluded files were found or not.

    Parameters
    ----------
    excluded_files: list
        List of files that have extensions included in the EXCLUDED_EXTENSIONS list.
    source: str
        String that indicates the source from which the files were fetched.

    Returns
    -------
    tuple
        Tuple containing a boolean value indicating whether excluded files were found or not,
        and a string message.
    """
    if excluded_files:
        return (
            True,
            f"File extension found: {excluded_files}. "
            f"Extensions found: {EXCLUDED_EXTENSIONS}.",
        )
    return (
        False,
        f"No excluded extensions found in {source} files.",
    )

def check_magnet_uri(uri: str):
    """
    Checks magnet uri type, and if it is a valid URI.

    Parameters
    ----------
    uri: str
        Input URI

    Returns
    -------
    str
        Valid magnet URI

    Raises
    ------
    ValueError
        If the URI is not valid or not a magnet link
    """

    parsed = urlparse(uri)
    magnet_pattern = r'magnet:\?xt=urn:[a-z0-9]+:[a-z0-9]{32,40}&dn=.*&tr=.*'
    match = re.fullmatch(magnet_pattern, uri)

    if all([parsed.scheme, parsed.netloc, parsed.path]) and match:
        return uri
    raise ValueError("The provided URI is not a valid magnet URI.")

def check_file_extensions(uri: Union[str, List[str]]) -> Tuple[bool, Union[str, None]]:
    """
    Checks the provided URI for file extensions that are included in the EXCLUDED_EXTENSIONS list.

    Parameters
    ----------
    uri: Union[str, List[str]]
        URI(s) to check.

    Returns
    -------
    Tuple[bool, Union[str, None]]
        Tuple containing a boolean value indicating whether excluded files were found or not,
        and a string message.
    """
    result = (False, "Transmission check is not enabled.")

    magnet_uri = check_magnet_uri(uri)

    res, error_message = get_magnet_instant_data(magnet_uri)

    if error_message:
        result = res, error_message
    elif res["data"]["magnets"][0]["instant"]:
        excluded_files = fetch_excluded_files_from_magnet_data(res)
        result = generate_result_with_excluded_files(excluded_files, "magnet")
    elif TRANSMISSION_CHECK:
        resp = fetch_torrent_metadata(uri)
        excluded_files = fetch_excluded_files_from_torrent_data(resp)
        result = generate_result_with_excluded_files(excluded_files, "torrent metadata")

    return result
