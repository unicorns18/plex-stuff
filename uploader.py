#pylint: disable=C0301
"""
This module provides functionality to process magnet links using the AllDebrid API.
It checks if the magnet is instant, uploads it, and saves and deletes uptobox.com torrent links.
"""
import concurrent.futures
import time
from typing import Any, Dict, Iterable, List
from alldebrid import APIError, AllDebrid

DEFAULT_API_KEY = "tXQQw2JPx8iKEyeeOoJE"
ad = AllDebrid(apikey=DEFAULT_API_KEY)

def process_magnet(magnet: str) -> None:
    """
    Process a magnet link, check if it's instant, upload it, and save and delete uptobox.com torrent links.

    :param magnet: The magnet link to process.
    """

    def save_and_delete_link(link: str) -> None:
        """
        Save and then delete a link using the ad module.

        :param link: The link to save and delete.
        """
        res_saved_links: Dict[str, Any] = ad.save_new_link(link=link)
        print(res_saved_links)
        res_deleted_link: Dict[str, Any] = ad.delete_saved_link(links=link)
        print(res_deleted_link)

    def filter_uptobox_links_generator(magnet_links: List[Dict[str, str]]) -> Iterable[str]:
        """
        Filter uptobox.com links from a list of magnet links.

        :param magnet_links: A list of magnet link dictionaries.
        :return: A generator yielding uptobox.com links.
        """
        for link in magnet_links:
            if 'uptobox.com' in link['link']:
                yield link['link']

    start_time = time.perf_counter()

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
            torrent_links: Iterable[str] = filter_uptobox_links_generator(res_status['data']['magnets']['links'])
        except (ValueError, APIError) as exc:
            print(f"Error uploading magnet or getting status: {exc}")
            return

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(save_and_delete_link, link) for link in torrent_links}
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

if __name__ == "__main__":
    MAGNET = "magnet:?xt=urn:btih:260AC3B389BE23D137BB13724DC6A5B43637FE1E&dn=Breaking.Bad.S01.2160p.WEBRip.DTS-HD.MA5.1.x264-TrollUHD&tr=http%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&tr=udp%3A%2F%2F47.ip-51-68-199.eu%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2780%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2730%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2920%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.dler.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce"
    process_magnet(MAGNET)
