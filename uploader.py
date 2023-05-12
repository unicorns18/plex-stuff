#pylint: disable=C0301
"""
This module provides functionality to process magnet links using the AllDebrid API.
It checks if the magnet is instant, uploads it, and saves and deletes uptobox.com torrent links.
"""
import concurrent.futures
import time
from typing import Any, Dict, Iterable, List
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
            torrent_links: Iterable[str] = filter_uptobox_links(res_status['data']['magnets']['links'])
        except (ValueError, APIError) as exc:
            print(f"Error uploading magnet or getting status: {exc}")
            return

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(save_link, link) for link in torrent_links}
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

# res = ad.download_file_then_upload_to_alldebrid("https://yourbittorrent2.com/down/12537781.torrent")
# process_magnet("magnet:?xt=urn:btih:cf8d0ec615e705741e446887726fe80374613f2a&dn=Incredibles.2.2018.2160p.BluRay.x265.10bit.SDR.TrueHD.7.1.Atmos-SWTYBLZ&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2800&tr=udp%3A%2F%2F9.rarbg.to%3A2860")
