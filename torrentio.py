# pylint: disable=C0114,C0301
import json
import re
import requests
from exceptions import IMDBIdNotFoundError
from filters import clean_title

DEFAULT_OPTS = "https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/manifest.json"  # noqa: E501
session = requests.Session()

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
        response = session.get(url, timeout=60)
        response = json.loads(response.content)
        return response
    except Exception:  # pylint: disable=W0703
        return None

def search(query: str, type_: str) -> str:
    """
    Searches for the IMDB ID of the movie or show

    Parameters
    ----------
    query: str
        Name of the movie or show
    type_: str
        Type of the video ('movie' or 'show')

    Returns
    -------
    str
        IMDB ID of the movie or show
    """
    url = f"https://v3-cinemeta.strem.io/catalog/{type_}/top/search={query}.json"
    meta = get(url)
    return meta["metas"][0]["imdb_id"]

def extract_info(result):
    """
    Extracts the necessary information from the search result

    Parameters
    ----------
    result: dict
        Search result

    Returns
    -------
    dict
        Dictionary with title, size, links, seeds, and source
    """
    title = clean_title(result["title"].split("\n")[0].replace(" ", "."))
    size_text = re.search(r"(?<=💾 )([0-9]+.?[0-9]+)(?= GB| MB)", result["title"]).group()
    size = float(size_text) / 1000 if "MB" in result["title"] else float(size_text)
    links = ["magnet:?xt=urn:btih:" + result["infoHash"] + "&dn=&tr="]
    seeds = int(re.search(r"(?<=👤 )([0-9]+)", result["title"]).group() or 0)
    source = re.search(r"(?<=⚙️ )(.*)(?=\n|$)", result["title"]).group() or "unknown"
    return {"title": title, "size": size, "links": links, "seeds": seeds, "source": source}

def scrape(query: str, altquery: str):
    """
    Scrape the torrent from torrentio.

    Parameters
    ----------
    query: str
        Name of the movie or tv series.
    altquery: str
        Name of the movie or tv series.

    Returns
    -------
    list
        List of scraped torrents.
    """
    scraped_releases = []

    if altquery == "(.*)":
        altquery = query

    type_ = "show" if re.search(r"(S[0-9]|complete|S\?[0-9])", altquery, re.IGNORECASE) else "movie"

    opts = DEFAULT_OPTS.split("/")[-2] if DEFAULT_OPTS.endswith("manifest.json") else ""

    if re.search(r"(tt[0-9]+)", altquery, re.IGNORECASE):
        query = re.search(r"(tt[0-9]+)", altquery, re.IGNORECASE).group()
    else:
        try:
            query = search(query, type_)
        except IMDBIdNotFoundError:
            try:
                type_ = "show" if type_ == "movie" else "movie"
                query = search(query, type_)
            except IMDBIdNotFoundError:
                print("[torrentio] error: could not find IMDB ID")
                return []

    url = f"https://torrentio.strem.fun/{opts}/{'' if len(opts) == 0 else '/'}stream/{type_}/{query}.json"
    response = get(url)

    if "streams" not in response:
        print(f"[torrentio] error: {response if response is not None else 'unknown error'}")
        return []

    for result in response["streams"]:
        scraped_releases.append(extract_info(result))

    return scraped_releases
