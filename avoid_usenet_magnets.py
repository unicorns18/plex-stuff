import os
import json
import shutil
import threading
from typing import List, Optional, Tuple
import warnings
import libtorrent as lt
import time
import concurrent.futures
from alldebrid import AllDebrid

DEFAULT_API_KEY = "tXQQw2JPx8iKEyeeOoJE"
ad = AllDebrid(apikey=DEFAULT_API_KEY)

warnings.simplefilter('ignore', category=DeprecationWarning)
lock = threading.Lock()

def check_rar_files_in_torrent(magnet_link, save_path='/storage/torrent_files/', timeout=120):
    params = {
        "save_path": save_path,
        "storage_mode": lt.storage_mode_t.storage_mode_sparse,
    }
    
    rar_files = []
    start_time = time.time()

    # Initialize the session
    session = lt.session()

    try:
        res = ad.check_magnet_instant(magnet_link)
        
        if res['data']['magnets'][0]['instant'] == True:
            for file in res['data']['magnets'][0]['files']:
                if 'e' in file:  # this is a directory
                    for subfile in file['e']:
                        _, ext = os.path.splitext(subfile['n'])
                        print(f"File: {subfile['n']} Size: {subfile['s']}")
                        if ext.lower() in ['.rar', '.iso', '.zip', '.7z', '.gz', '.bz2', '.xz']:
                            rar_files.append(subfile['n'])
                else:
                    _, ext = os.path.splitext(file['n'])
                    print(f"File: {file['n']} Size: {file['s']}")
                    if ext.lower() in ['.rar', '.iso', '.zip', '.7z', '.gz', '.bz2', '.xz']:
                        rar_files.append(file['n'])
            return rar_files
        else:
            print("Not instant. Proceeding with torrent-based method.")
    except Exception as e:
        print(f"Failed to check magnet link instantly: {e}")
        print("Proceeding with torrent-based method.")

    try:
        handle = lt.add_magnet_uri(session, magnet_link, params)
    except Exception as e:
        print(f"Failed to add magnet link: {e}")
        return rar_files

    try:
        # Pause the download and set file priorities to 0
        handle.pause()
        while not handle.has_metadata():
            time.sleep(1)
            if time.time() - start_time > timeout:
                print("Timeout while waiting for metadata")
                return rar_files
        handle.prioritize_files([0]*len(handle.get_torrent_info().files()))

        print("downloading metadata...")
        while (not handle.has_metadata()):
            time.sleep(1)
            if time.time() - start_time > timeout:
                print("Timeout while waiting for metadata")
                return rar_files
        print("got metadata, starting torrent download...")

        torinfo = handle.get_torrent_info()

        # Lock access to the save_path directory
        with lock:
            # If the torrent already exists in the save_path, delete it
            torrent_name = torinfo.name()
            file_path = os.path.join(params["save_path"], torrent_name)
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

        for file in torinfo.files():
            # print(f"File: {file.path} Size: {file.size}")
            _, ext = os.path.splitext(file.path)
            if ext.lower() in ['.rar', '.iso', '.zip', '.7z', '.gz', '.bz2', '.xz']:
                rar_files.append(file.path)

        # Attempt to remove the torrent
        session.remove_torrent(handle, lt.session.delete_files)

        # Check if the torrent still exists in the session
        if handle in session.get_torrents():
            print("Failed to remove torrent using libtorrent, using shutil method")

            # Delete the files manually
            with lock:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Clean up the session
        del session

    return rar_files

def process_file(filepath: str) -> Optional[Tuple[str, str, List[str]]]:
    with open(filepath, 'r') as f:
        data = json.load(f)
        if 'links' in data[0] and data[0]['links']:
            magnet = data[0]['links'][0]
            rar_files = check_rar_files_in_torrent(magnet)
            if rar_files:  # If any unwanted files were found, return the filename, magnet, and rar_files
                return (filepath, magnet, rar_files)
    return None

num_workers = os.cpu_count()
directory = 'results/'
json_files = [f for f in os.listdir(directory) if f.endswith(".json")]
total_files = len(json_files)

unwanted_files = []
with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, num_workers)) as executor:
    futures = {executor.submit(process_file, directory + filename): filename for filename in json_files}
    for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
        filename = futures[future]
        try:
            result = future.result()
            if result is not None:  # If unwanted files were found, add to the list
                unwanted_files.append(result)
                filename, magnet, rar_files = result
            print(f"Processed {i} out of {total_files} files. Currently on file: {filename}")
        except Exception as exc:
            print('%r generated an exception: %s' % (filename, exc))

with open('unwanted_files.txt', 'w') as f:
    for filename, magnet, rar_files in unwanted_files:
        f.write(f"Filename: {filename}, Magnet: {magnet}, RAR files: {rar_files}\n")
