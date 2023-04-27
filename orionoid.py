#pylint: disable=C0114,C0301
import json
import time
import regex
import requests
from exceptions import MatchNotFoundError
from filters import clean_title

TOKEN = "ZZBAYPMQTXGGVHPKZJO5Y4SQJO3NA3XE7WBJLN67DOA3TLLQ3A7VMP532XSIDGKRPNQPCHNEV5HUGTD4UEU5IE6FBP4N7VV3ZZBKM6LZRUZ2WM7KKDKIYFJLV6C26JHA"
CLIENT_ID = "GVFTUUBKFCK67DC8AR9EF2QHCP8GDCME"
API_HOST = "https://api.orionoid.com"

default_opts = [
    ["sortvalue","best"],
    ["streamtype","torrent"],
    ["limitcount","20"],
    ["filename","true"]
]

session = requests.Session()

def get_token(code: str = "") -> str:
    """
    Gets orion token.

    Parameters
    ----------
    code: str
        Code from authentication URL.

    Returns
    -------
    str
        User Token.

    """
    while True:
        try:
            response = session.get(url="https://api.orionoid.com?keyapp=TESTTESTTESTTESTTESTTESTTESTTEST&mode=user&action=authenticate").json()
            
            print("Please visit the following link to authenticate your account:")
            print(response["data"]["direct"], response["data"]["code"])
            print("After you have authenticated your account, please copy the code from the URL and paste it here:")
            code = input("Code: ")
            print("Please wait...")
            interval = 5
            time.sleep(interval)
            break
        except Exception: # pylint: disable=W0703
            print("Error: Please check your internet connection.")
            time.sleep(5)
            continue

    while True:
        try:
            response = session.get(url=f"https://api.orionoid.com?keyapp=TESTTESTTESTTESTTESTTESTTESTTEST&mode=user&action=authenticate&code={code}").json()
            interval = 5
            if response["result"]["type"] == "userauthapprove":
                return response["data"]["token"]
            elif response["result"]["type"] == "userauthinreject":
                print("Error: User rejected access for your app.")
                break
            elif response["result"]["type"] == "userauthexpired":
                print("Error: Authentication process expired. Please restart the process.")
                break
            else:
                time.sleep(interval) # sleep for the interval returned by the request
                continue
        except requests.exceptions.ConnectionError:
            print("Error: Please check your internet connection.")
            time.sleep(5)
            continue

def get(url: str) -> None:
    """
    Sends a GET request to URL.

    Parameters
    ----------
    url: str
        URL for GET request.

    Returns
    -------
    None
    """
    try:
        response = session.get(url,timeout=60)
        response = json.loads(response.content)
        return response
    except Exception: # pylint: disable=W0703
        return None

def search(query: str, altquery: str) -> dict:
    """
    Searches orion.

    Parameters
    ----------
    query: str
        Query to search.
    altquery: str
        Alternate Query to search.

    Returns
    -------
    dict
        Scraped Releases.
    """
    if altquery == "(.*)":
        altquery = query

    type_ = ("show" if regex.search(r'(S[0-9]|complete|S\?[0-9])',altquery,regex.I) else "movie")
    opts = []

    for opt in default_opts:
        opts += ['='.join(opt)]
    opts = '&'.join(opts)

    if type_ == "show":
        season_number = (regex.search(r'(?<=S)([0-9]+)',altquery,regex.I).group() if regex.search(r'(?<=S)([0-9]+)',altquery,regex.I) else None)
        episode_number = (regex.search(r'(?<=E)([0-9]+)',altquery,regex.I).group() if regex.search(r'(?<=E)([0-9]+)',altquery,regex.I) else None)
        if season_number is None or int(season_number) == 0:
            season_number = 1
        opts += '&numberseason=' + str(int(season_number))
        if not episode_number is None and int(episode_number) != 0:
            opts += '&numberepisode=' + str(int(episode_number))
    scraped_releases = []
    
    if regex.search(r'(tt[0-9]+)', altquery, regex.I):
        query = regex.search(r'(tt[0-9]+)', altquery, regex.I).group()
    
    if regex.search(r'(tt[0-9]+)', query, regex.I):
        url = 'https://api.orionoid.com?token='+TOKEN+'&mode=stream&action=retrieve&type='+type_+'&idimdb='+query[2:] + '&' + opts
    else:
        url = 'https://api.orionoid.com?token='+TOKEN+'&mode=stream&action=retrieve&type='+type_+'&query='+query + '&' + opts

    response = get(url)
    if response['result']['status'] != 'success':
        print("Error: Did not receive a successful response from the server.")
        return None
    
    if "data" not in response or ("data" in response and "streams" not in response["data"]):
        print("data not found in response")
        return None
    print("data found in response, streams found in data, continuing...")

    match = "None"

    try:
        if "data" in response:
            if "movie" in response["data"]:
                match = response["data"]["movie"]["meta"]["title"] + ' ' + str(response["data"]["movie"]["meta"]["year"])
            elif "show" in response["data"]:
                match = response["data"]["show"]["meta"]["title"] + ' ' + str(response["data"]["show"]["meta"]["year"])
            print("Match: '" + query + "' to " + type_ + " '" + match + "' - found " + str(response["data"]["count"]["total"]) + " releases (total), retrieved " + str(response["data"]["count"]["retrieved"]))
    except MatchNotFoundError:
        print("Error: Could not find match.")

    for res in response["data"]["streams"]:
        title = clean_title(res['file']['name'].split('\n')[0].replace(' ','.'))
        size = (float(res["file"]["size"]) / 1000000000 if "size" in res["file"] else 0)
        links = res["links"]
        seeds = res["stream"]["seeds"] if "stream" in res and "seeds" in res["stream"] else 0
        source = res["stream"]["source"] if "stream" in res and "source" in res["stream"] else ""
        quality = res["video"]["quality"] if "video" in res and "quality" in res["video"] else ""
        scraped_releases.append({
            "title": title,
            "size": size,
            "links": links,
            "seeds": seeds,
            "source": source,
            "quality": quality
        })
    return scraped_releases
