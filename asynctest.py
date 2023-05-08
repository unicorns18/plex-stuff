from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import json
import random
import re
import time
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode
from alldebrid import AllDebrid

from requests import session
import requests
import ijson
from filters import clean_title
from tmdb import MEDIA_TYPE_MOVIE, MEDIA_TYPE_TV, is_movie_or_tv_show

session = requests.Session()
TOKEN = "ZZBAYPMQTXGGVHPKZJO5Y4SQJO3NA3XE7WBJLN67DOA3TLLQ3A7VMP532XSIDGKRPNQPCHNEV5HUGTD4UEU5IE6FBP4N7VV3ZZBKM6LZRUZ2WM7KKDKIYFJLV6C26JHA"
API_HOST = "https://api.orionoid.com"
DEFAULT_API_KEY = "tXQQw2JPx8iKEyeeOoJE"
TMDB_API_KEY = "cea9c08287d26a002386e865744fafc8"
BASE_URL = "https://api.themoviedb.org/3"
ad = AllDebrid(apikey=DEFAULT_API_KEY)

def normalize_queries(query: str, altquery: str) -> Tuple[str, str]:
    """
    Normalize the Queries.

    Parameters
    ----------
    query: str
        Query for Orion Search Engine.
    altquery: str
        Alternative Query for Orion Search Engine.

    Returns
    -------
    tuple
        Normalized Queries.
    """
    if altquery == "(.*)":
        altquery = query
    return query, altquery

def determine_type(altquery: str) -> str:
    """
    Determine the Type of Query.

    Parameters
    ----------
    altquery: str
        Alternative Query for Orion Search Engine.

    Returns
    -------
    str
        Type of Query.
    """
    return "show" if re.search(r'(S[0-9]|complete|S\?[0-9])', altquery, re.I) else "movie"

def build_opts(default_opts) -> str:
    """
    Build the Options for Query.

    Parameters
    ----------
    default_opts: list
        Default Options for Orion Search Engine.

    Returns
    -------
    list
        Options for Query.
    """
    return '&'.join(['='.join(opt) for opt in default_opts])

def extract_season_episode(altquery: str, type_: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract the Season and Episode from the Query.

    Parameters
    ----------
    altquery: str
        Alternative Query for Orion Search Engine.
    type_: str
        Type of Query.

    Returns
    -------
    tuple
        Season and Episode.
    """
    if type_ == "show":
        season_number = re.search(r'(?<=S)([0-9]+)', altquery, re.I)
        episode_number = re.search(r'(?<=E)([0-9]+)', altquery, re.I)
        return (season_number.group() if season_number else None, episode_number.group() if episode_number else None)
    return None, None

def add_season_episode(opts: str, season_number: Optional[str], episode_number: Optional[str]) -> str:
    """
    Add Season and Episode to Options.

    Parameters
    ----------
    opts: list
        Options for Query.
    season_number: int
        Season Number.
    episode_number: int
        Episode Number.

    Returns
    -------
    list
        Options for Query.
    """
    if season_number is not None and int(season_number) != 0:
        # opts += '&numberseason=' + str(int(season_number))
        opts += f"&numberseason={int(season_number)}"
        if episode_number is not None and int(episode_number) != 0:
            opts += f"&numberepisode={int(episode_number)}"
            # opts += '&numberepisode=' + str(int(episode_number))
    return opts

def build_url(token: str, query: str, type_: str, opts: str, debridresolve: str = "user") -> str:
    """
    Build the URL for Query.

    Parameters
    ----------
    token: str
        Orion Search Engine Token.
    query: str
        Query for Orion Search Engine.
    type_: str
        Type of Query.
    opts: list
        Options for Query.
    debridresolve: str, optional
        The debrid service to use for resolving links. If set, the streaming link is added as a debrid attribute to the 
        results. The value can be 'user', 'premiumize', 'offcloud', 'realdebrid', 'debridlink', 'alldebrid', 'list', 
        'choice', 'link', 'redirect', 'original', 'stream', 'sequential', or 'ip'. If not set, no debrid links will be 
        added.

    Returns
    -------
    str
        URL for Query.
    """
    if re.search(r'(tt[0-9]+)', query, re.I):
        idimdb = query[2:]
        query_params = urlencode({'token': token, 'mode': 'stream', 'action': 'retrieve', 'type': type_, 'idimdb': idimdb})
    else:
        query_params = urlencode({'token': token, 'mode': 'stream', 'action': 'retrieve', 'type': type_, 'query': query})

    if debridresolve:
        query_params += f"&debridlookup={debridresolve}"

    return f'https://api.orionoid.com?{query_params}&{opts}'

def response_is_successful(response: dict) -> bool:
    """
    Check the Response is Successful.

    Parameters
    ----------
    response: dict
        Response from Orion Search Engine.

    Returns
    -------
    bool
        Check the Response is Successful.
    """
    return response['result']['status'] == 'success'

def response_has_data(response: dict) -> bool:
    """
    Check the Response has Data.

    Parameters
    ----------
    response: dict
        Response from Orion Search Engine.

    Returns
    -------
    bool
        Check the Response has Data.
    """
    return "data" in response and "streams" in response["data"]

def extract_match_type_total_retrieved(response: dict, query: str, type_: str) -> Tuple[str, int, int]:
    """
    Extract the Match, Type, Total, Retrieved from the Response.

    Parameters
    ----------
    response: dict
        Response from Orion Search Engine.
    query: str
        Query for Orion Search Engine.
    type_: str
        Type of Query.

    Returns
    -------
    tuple
        Match, Type, Total, Retrieved.
    """
    match = "None"
    total = 0
    retrieved = 0

    if "data" in response:
        if "movie" in response["data"]:
            match = response["data"]["movie"]["meta"]["title"] + ' ' + str(response["data"]["movie"]["meta"]["year"])
        elif "show" in response["data"]:
            match = response["data"]["show"]["meta"]["title"] + ' ' + str(response["data"]["show"]["meta"]["year"])

        total = response["data"]["count"]["total"]
        retrieved = response["data"]["count"]["retrieved"]

        print(f"Match: '{query}' to {type_} '{match}' - found {total} releases (total), retrieved {retrieved}")

    return match, total, retrieved

from alldebrid import AllDebrid
ad = AllDebrid(apikey=DEFAULT_API_KEY)

def extract_scraped_releases(response: dict) -> List[Dict]:
    """
    Extract the Scraped Releases from the Response.

    Parameters
    ----------
    response: dict
        Response from Orion Search Engine.

    Returns
    -------
    dict
        Scraped Releases.
    """
    scraped_releases = []

    for res in response["data"]["streams"]:
        title = clean_title(res['file']['name'].split('\n')[0].replace(' ', '.'))
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
    
def search(query: str, altquery: str, quality_opts) -> Optional[Dict]:
    """
    Search the Orion Search Engine.

    Parameters
    ----------
    query: str
        Query for Orion Search Engine.
    altquery: str
        Alternative Query for Orion Search Engine.

    Returns
    -------
    dict
        Scraped Releases.
    """
    query, altquery = normalize_queries(query, altquery)
    type_ = determine_type(altquery)
    opts = build_opts(quality_opts)
    season_number, episode_number = extract_season_episode(altquery, type_)
    opts = add_season_episode(opts, season_number, episode_number)
    url = build_url(TOKEN, query, type_, opts, debridresolve="alldebrid")
    print(url)
    response = session.get(url).json()

    if not response_is_successful(response):
        print("Error: Did not receive a successful response from the server.")
        return None

    if not response_has_data(response):
        print("data not found in response")
        return None

    print("data found in response, streams found in data, continuing...")
    match, total, retrieved = extract_match_type_total_retrieved(response, query, type_) #pylint: disable=W0612
    scraped_releases = extract_scraped_releases(response)

    if not scraped_releases:
        print("No scraped releases found in response")
        return None

    return scraped_releases

def batch_search(queries: List[str], altqueries: List[str], quality_opts: List[List[str]], batch_size: int) -> List[Optional[Dict]]:
    results = []
    for i in range(0, len(queries), batch_size):
        batch_queries = queries[i:i+batch_size]
        batch_altqueries = altqueries[i:i+batch_size]
        batch_quality_opts = quality_opts[i:i+batch_size]
        batch_results = [search(query=q, altquery=a, quality_opts=o) for q, a, o in zip(batch_queries, batch_altqueries, batch_quality_opts)]
        results.extend(batch_results)
    return results

def custom_sort(item: Dict[str, Union[float, int]]) -> Tuple[float, int]:
    """
    Calculate the custom sort value for a given item based on its size, seeds, and cache status.

    Parameters
    ----------
    item: Dict[str, Union[float, int]]
        A dictionary representing a media item containing "size", "seeds", and "cached" keys.

    Returns
    -------
    Tuple[float, int]
        A tuple containing the size_weight as the first element and the seeds_weight as the second element.
    """
    size_weight = item.get("size", 0) or 0
    seeds_weight = item.get("seeds", 0) or 0
    instant_weight = int(not item.get("cached", False))
    return (size_weight, instant_weight, seeds_weight)

def get_season_data(title: str, retries: int = 3, backoff_factor: float = 2.0) -> Optional[Dict]:
    """
    Get the season data of tv show.

    Parameters
    ----------
    title: str
        Title of tv show.
    retries: int
        Number of retries to make.
    backoff_factor: float
        Sleep time between retries.

    Returns
    -------
    Optional[Dict]
        Season Data of Tv Show.
    """
    search_params = { "api_key": TMDB_API_KEY, "query": title }
    search_url = f"{BASE_URL}/search/tv?{urlencode(search_params)}"
    for attempt in range(retries + 1):
        try:
            with requests.get(search_url, timeout=60, stream=True) as response:
                response.raise_for_status()
                with gzip.open(response.raw, mode='rt', encoding='utf-8') as gzip_file:
                    search_data = ijson.items(gzip_file, 'results.item')
                    tv_show = next(search_data, None)
                    if tv_show:
                        tv_show_id = tv_show["id"]
                        tv_show_url = f"{BASE_URL}/tv/{tv_show_id}?api_key={TMDB_API_KEY}"

                        with requests.get(tv_show_url, timeout=60, stream=True) as tv_show_response:
                            tv_show_response.raise_for_status()
                            with gzip.open(tv_show_response.raw, mode='rt', encoding='utf-8') as gzip_tv_show_file:
                                tv_show_data = ijson.items(gzip_tv_show_file, '')
                                tv_show_details = next(tv_show_data, None)
                                return {"total_seasons": tv_show_details["number_of_seasons"]} if tv_show_details else None
        except requests.exceptions.RequestException as exc:
            if attempt == retries:
                print(f"Failed after {retries} attempts. Error: {exc}")
                return None
            else:
                sleep_time = backoff_factor * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed. Retrying in {sleep_time} seconds. Error: {exc}")
                time.sleep(sleep_time)

def save_filtered_results(results: List[dict], filename: str, encoding: str = 'utf-8') -> None:
    filtered_results = [item for item in results[1:] if item.get("seeds") is not None]

    with open(filename, 'w', encoding=encoding) as file:
        for chunk in json.JSONEncoder(indent=4, sort_keys=True).iterencode(filtered_results):
            file.write(chunk)

def get_cached_instants(ad: 'AllDebrid', magnets: List[str]) -> List[Union[str, bool]]:
    checkmagnets = ad.check_magnet_instant(magnets=magnets)
    
    if checkmagnets and checkmagnets['status'] == 'success':
        cached = checkmagnets['data']['magnets']
        instant_values = [magnet_data.get('instant', False) for magnet_data in cached]
    else:
        instant_values = [False] * len(magnets)

    return instant_values

def search_best_qualities(title: str, qualities_sets: List[List[str]], filename_prefix: str):
    start_time = time.perf_counter()
    title_type = is_movie_or_tv_show(title=title, api_key=TMDB_API_KEY, api_url="https://api.themoviedb.org/3")

    def process_quality(qualities: List[str], season: Optional[int] = None):
        altquery = title if title_type == MEDIA_TYPE_MOVIE else f"{title} S{season:02d}"
        default_opts = [
            ["sortvalue", "best"],
            ["streamtype", "torrent"],
            ["limitcount", "20"],
            ["filename", "true"],
            ["videoquality", ','.join(qualities)],
        ]
        result = search(query=title, altquery=altquery, quality_opts=default_opts)

        filtered_results = [item for item in result if item.get("seeds") is not None]

        magnets = (item['links'][0] for item in filtered_results)
        cached_instants = get_cached_instants(ad, magnets)
        for item, instant in zip(filtered_results, cached_instants):
            item["cached"] = instant if instant is not False else False

        post_processed_results = [item for item in filtered_results if item["cached"] is not False]
        post_processed_results.sort(key=custom_sort, reverse=True)

        season_suffix = f"_{season:02d}" if season else ""
        post_processed_filename = f'postprocessing_results/{filename_prefix}_{"_".join(qualities)}_orionoid{season_suffix}_post_processed.json'
        save_filtered_results(post_processed_results, post_processed_filename)

    futures = []
    with ThreadPoolExecutor() as executor:
        if title_type == MEDIA_TYPE_TV:
            season_data = get_season_data(title)
            if season_data:
                total_seasons = season_data["total_seasons"]
                for season in range(1, total_seasons + 1):
                    for qualities in qualities_sets:
                        futures.append(executor.submit(process_quality, qualities, season))
            else:
                print(f"Could not get season data for {title}")

        elif title_type == MEDIA_TYPE_MOVIE:
            for qualities in qualities_sets:
                futures.append(executor.submit(process_quality, qualities))
        else:
            print(f"Unknown type for {title}")

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Exception occurred in a task: {exc}")

    end_time = time.perf_counter()
    print(f"Finished in {end_time - start_time:0.4f} seconds")

QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
FILENAME_PREFIX = "result"
search_best_qualities(title="Breaking Bad", qualities_sets=QUALITIES_SETS, filename_prefix=FILENAME_PREFIX)
