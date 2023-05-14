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
from typing import Any, Dict, Iterable, List, Union
from alldebrid import AllDebrid, APIError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception, retry_if_result
import requests

from constants import TRANSMISSION_CHECK, TRANSMISSION_HOST, TRANSMISSION_PORT

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

def fetch_torrent_metadata(magnet_uri: str) -> Dict[str, Any]:
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
            "peer-limit": 200,
            "bandwidthPriority": 1
        }
    }

    response = make_request(session, data).json()
    torrent_id = response.get('arguments', {}).get('torrent-added', {}).get('id')
    if not torrent_id:
        raise Exception("Failed to add torrent")

    # Wait for metadata to be fetched
    # start_time = time.time()
    # while time.time() - start_time < 60:  # timeout after 60 seconds
    #     data = {
    #         "method": "torrent-get",
    #         "arguments": {
    #             "ids": [torrent_id],
    #             "fields": ["metadataPercentComplete"]
    #         }
    #     }
    #     response = make_request(session, data).json()
    #     if response.get('arguments', {}).get('torrents', [{}])[0].get('metadataPercentComplete') == 1:
    #         break
    #     time.sleep(0.2)  # Reduced sleep time
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

EXCLUDED_EXTENSIONS = ['.rar', '.iso', '.zip', '.7z', '.gz', '.bz2', '.xz']

def is_none(result):
    return result is None
def is_error(exception):
    return isinstance(exception, (ValueError, APIError))

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry_error_callback=is_error, retry=retry_if_result(is_none))
def check_file_extensions(uri: Union[str, List[str]]):
    if not uri.startswith('magnet:'):
        try:
            magnet_uri = ad._download_and_upload_single_file(uri)
        except (ValueError, APIError) as exc:
            print(f"Error downloading and uploading file to AllDebrid: {exc} (check_file_extensions)")
            return False
    else:
        magnet_uri = uri

    try:
        res =  ad.check_magnet_instant(magnets=uri)
    except (APIError, ValueError) as exc:
        logging.info(f"Error checking magnet instant: {exc}")
        return False
    
    if res['data']['magnets'][0]['instant']:
        files = res['data']['magnets'][0]['files']
        logging.info("files: ", files)
        for n in files:
            if any(n['n'].endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                logging.info(f"file extension found: {n['n']}")
                logging.info("extensions found: ", any(n['n'].endswith(ext) for ext in EXCLUDED_EXTENSIONS))
                return True
        return False
    else:
        if TRANSMISSION_CHECK:
            resp = fetch_torrent_metadata(uri)
            for file in resp['files']:
                if any(file['name'].endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                    logging.info(f"file extension found: {file['name']}")
                    logging.info("extensions found: ", any(file['name'].endswith(ext) for ext in EXCLUDED_EXTENSIONS))
                    return True
                return False

# Without rar files
# r = check_file_extensions("magnet:?xt=urn:btih:5428AB2CAF31194F5F8129546FFAED76E40F943B&dn=Casablanca%201942%20REMASTERED%201080p%20BluRay%20REMUX%20AVC%20DTS%20HD%20MA%201%200%20FGT&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Fretracker.hotplug.ru%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.birkenwald.de%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&tr=http%3A%2F%2Ftracker.bt4g.com%3A2095%2Fannounce&tr=udp%3A%2F%2Fmovies.zsw.ca%3A6969%2Fannounce&tr=udp%3A%2F%2Fretracker01-msk-virt.corbina.net%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.leech.ie%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.altrosky.nl%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.bitsearch.to%3A1337%2Fannounce&tr=http%3A%2F%2Ftracker.mywaifu.best%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.srv00.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fthouvenin.cloud%3A6969%2Fannounce&tr=udp%3A%2F%2Faarsen.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fsanincode.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fuploads.gamecoast.net%3A6969%2Fannounce&tr=udp%3A%2F%2Fmail.artixlinux.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.joybomb.tw%3A6969%2Fannounce&tr=https%3A%2F%2Ftracker.tamersunion.org%3A443%2Fannounce&tr=udp%3A%2F%2Fstatic.54.161.216.95.clients.your-server.de%3A6969%2Fannounce&tr=udp%3A%2F%2Fcpe-104-34-3-152.socal.res.rr.com%3A6969%2Fannounce&tr=https%3A%2F%2Ft1.hloli.org%3A443%2Fannounce")
# With rar files
# r = check_file_extensions("magnet:?xt=urn:btih:B44A83FDC2CAC26F1C5E2A028340DB7382E2F401&dn=WALL.E.2008.COMPLETE.UHD.BLURAY-AViATOR&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fretracker.hotplug.ru%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.birkenwald.de%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&tr=http%3A%2F%2Ftracker.bt4g.com%3A2095%2Fannounce&tr=udp%3A%2F%2Ftracker.leech.ie%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.altrosky.nl%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.bitsearch.to%3A1337%2Fannounce&tr=http%3A%2F%2Ftracker.mywaifu.best%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.srv00.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fthouvenin.cloud%3A6969%2Fannounce&tr=udp%3A%2F%2Fastrr.ru%3A6969%2Fannounce&tr=udp%3A%2F%2Faarsen.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fepider.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fsanincode.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fmoonburrow.club%3A6969%2Fannounce&tr=udp%3A%2F%2Fuploads.gamecoast.net%3A6969%2Fannounce&tr=udp%3A%2F%2Fmail.artixlinux.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fv1046920.hosted-by-vdsina.ru%3A6969%2Fannounce&tr=udp%3A%2F%2Fstatic.54.161.216.95.clients.your-server.de%3A6969%2Fannounce&tr=udp%3A%2F%2Fcpe-104-34-3-152.socal.res.rr.com%3A6969%2Fannounce&tr=http%3A%2F%2Fvps-dd0a0715.vps.ovh.net%3A6969%2Fannounce&tr=https%3A%2F%2Ft1.hloli.org%3A443%2Fannounce")
# Cached with rar files
# r = check_file_extensions("magnet:?xt=urn:btih:0E6C69E3D30700980B46174515B5BC8984EEC12F&dn=Spider%20Man%202002&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.open-internet.nl%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=http%3A%2F%2Ftracker3.itzmx.com%3A6961%2Fannounce&tr=http%3A%2F%2Ftracker1.itzmx.com%3A8080%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.si%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fbt.xxx-tracker.com%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Fthetracker.org%3A80%2Fannounce&tr=udp%3A%2F%2Fdenis.stalker.upeer.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%3A80%2Fannounce&tr=http%3A%2F%2Fopen.acgnxtracker.com%3A80%2Fannounce")
# Unknown
# r = check_file_extensions("magnet:?xt=urn:btih:CCDA83FCB67C93DA8443C3D336E80FBEE92EBD59&dn=The.Rise.Of.The.Beast.2022.720p.AMZN.WEBRip.800MB.x264-GalaxyRG&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.birkenwald.de%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fopentor.org%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.dler.org%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2970%2Fannounce&tr=https%3A%2F%2Ftracker.foreverpirates.co%3A443%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=http%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fcoppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.zer0day.to%3A1337%2Fannounce")
for filename in os.listdir("results/"):
    if filename.endswith(".json"):
        with open("results/" + filename, "r") as f:
            data = json.load(f)
            for item in data:
                links = item["links"]
                for link in links:
                    r = check_file_extensions(link)
                    # print(r)
                    if r == True:
                        print(link)
                        print("True")
                        print()
                        break