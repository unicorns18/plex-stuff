# pylint: disable=C0301
"""
This module provides functionality to process magnet links using the AllDebrid API.
It checks if the magnet is instant, uploads it, and saves and deletes uptobox.com torrent links.
"""
import concurrent.futures
import json
import os
import re
import time
from typing import Any, Dict, Iterable, List, Union
from alldebrid import AllDebrid, APIError

DEFAULT_API_KEY = "tXQQw2JPx8iKEyeeOoJE"
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

def check_file_extensions(uri: Union[str, List[str]]):
    EXCLUDED_EXTENSIONS = ['.rar', '.iso', '.zip', '.7z', '.gz', '.bz2', '.xz']

    # Check if uri is a magnet link or a regular URL
    if not uri.startswith('magnet:'):
        # If it's a regular URL, download and upload the file to get a magnet link
        magnet_uri = ad._download_and_upload_single_file(uri)
    else:
        # If it's already a magnet link, use it as is
        magnet_uri = uri

    res = ad.check_magnet_instant(magnets=magnet_uri)

    if res['status'] != 'success':
        print(f"Error checking magnet: {res} (check_file_extensions)")
        return False

    try:
        magnets = res['data']['magnets']
        if not magnets:
            print("No magnets found")
            return False

        # If 'instant' is False, return
        if not magnets[0].get('instant', False):
            return False

        magnet_files = magnets[0]['files']
    except KeyError as e:
        print(f"Key {e} not found in the dictionary. Response: {res} (check_file_extensions)")
        return False

    return any(item['n'].endswith(ext) for item in magnet_files if item is not None for ext in EXCLUDED_EXTENSIONS) and any(item['n'].endswith('.mkv') for item in magnet_files if item is not None)
