import hashlib
import requests

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '})

token = "NZTOF3K2RK2MZC5O3ZQYP5NEOL5OB2VGEXQVMLRWM3DEYVOKXRLA"

def check_instant_availability(magnet: str) -> bool:
    # Calculate the SHA1 hash of 'magnet'
    hash = hashlib.sha1(magnet.encode('utf-8')).hexdigest()
    URL = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash}"
    URL += f"?auth_token={token}"
    print(URL)
    res = session.get(URL, timeout=60)
    if res.status_code == 401:
        raise ValueError("Bad token (expired, invalid)")
    elif res.status_code == 403:
        raise ValueError("Permission denied (account locked, not premium)")
    
    res.raise_for_status()
    return res.json()

print(check_instant_availability("magnet:?xt=urn:btih:CB98398FEB9A7FD6C3C20C79FD3170DD3F0E0F60&dn=Incredibles.2.2018.4K.HDR.2160p.BDRip%20Ita%20Eng%20x265-NAHOM.torrent&tr=udp://tracker.coppersurfer.tk:6969/announce&tr=udp://tracker.opentrackr.org:1337/announce&tr=udp://tracker.leechers-paradise.org:6969/announce&tr=udp://9.rarbg.com:2710/announce&tr=udp://9.rarbg.to:2710/announce&tr=udp://9.rarbg.me:2710/announce&tr=udp://glotorrents.pw:6969/announce&tr=udp://tracker.openbittorrent.com:80/announce&tr=udp://tracker.torrent.eu.org:451/announce&tr=udp://exodus.desync.com:6969/announce&tr=udp://exodus.desync.com:6969"))
