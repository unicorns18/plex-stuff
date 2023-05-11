#pylint: disable=C0301,C0116,c0303
"""
TODO: Write a docstring
"""
import cProfile
from collections import namedtuple
from functools import lru_cache, partial
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed
import gzip
import json
import os
import re
import time
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode, urlparse
import dns
import ijson
import redis
import requests
from requests import session
import requests_cache
from urllib3 import Retry
from alldebrid import AllDebrid

from filters import clean_title
from tmdb import MEDIA_TYPE_MOVIE, MEDIA_TYPE_TV

session = requests.Session()
TOKEN = "ZZBAYPMQTXGGVHPKZJO5Y4SQJO3NA3XE7WBJLN67DOA3TLLQ3A7VMP532XSIDGKRPNQPCHNEV5HUGTD4UEU5IE6FBP4N7VV3ZZBKM6LZRUZ2WM7KKDKIYFJLV6C26JHA"
API_HOST = "https://api.orionoid.com"
DEFAULT_API_KEY = "tXQQw2JPx8iKEyeeOoJE"
TMDB_API_KEY = "cea9c08287d26a002386e865744fafc8"
BASE_URL = "https://api.themoviedb.org/3"
BASE_URL_ORIONOID = 'https://api.orionoid.com'
ad = AllDebrid(apikey=DEFAULT_API_KEY)

def normalize_queries(query: str, altquery: str) -> Tuple[str, str]:
    if altquery == "(.*)":
        altquery = query
    return query, altquery

def determine_type(altquery: str) -> str:
    TV_SHOW_PATTERN = r'(S[0-9]|complete|S\?[0-9])'
    return "tv" if re.search(TV_SHOW_PATTERN, altquery, re.I) else "movie"

def build_opts(default_opts) -> str:
    return '&'.join(['='.join(opt) for opt in default_opts])

def extract_season_episode(altquery: str, type_: str) -> Tuple[Optional[str], Optional[str]]:
    if type_ == "tv":
        season_number = re.findall(r'S(\d+)', altquery, re.I)
        episode_number = re.findall(r'E(\d+)', altquery, re.I)
        return (season_number[0] if season_number else None, episode_number[0] if episode_number else None)
    return None, None

def add_season_episode(opts: str, season_number: Optional[str], episode_number: Optional[str]) -> str:
    if season_number:
        season_num = int(season_number)
        if season_num != 0:
            opts = f"{opts}&numberseason={season_num}"
            if episode_number:
                episode_num = int(episode_number)
                if episode_num != 0:
                    opts = f"{opts}&numberepisode={episode_num}"
    return opts

def build_url(token: str, query: str, type_: str, opts: str) -> str:
    params = {'token': token, 'mode': 'stream', 'action': 'retrieve', 'type': type_}

    if query.startswith('tt'):
        params['idimdb'] = query[2:]
    else:
        params['query'] = query

    query_params = urlencode(params)
    return f'{BASE_URL_ORIONOID}?{query_params}&{opts}'

def response_is_successful(response: dict) -> bool:
    return response.get('result', {}).get('status') == 'success'

def response_has_data(response: dict) -> bool:
    return bool(response.get("data", {}).get("streams"))

def extract_match_type_total_retrieved(response: dict, query: str, type_: str) -> Tuple[Optional[str], int, int]:
    NONE = "None"
    MOVIE = "movie"
    SHOW = "show"
    META = "meta"
    TITLE = "title"
    YEAR = "year"
    COUNT = "count"
    TOTAL = "total"
    RETRIEVED = "retrieved"
    
    match = NONE
    total = 0
    retrieved = 0

    data = response.get("data")

    if data:
        if MOVIE in data:
            movie_meta = data[MOVIE].get(META, {})
            match = f'{movie_meta.get(TITLE, "")} {movie_meta.get(YEAR, "")}'
        elif SHOW in data:
            show_meta = data[SHOW].get(META, {})
            match = f'{show_meta.get(TITLE, "")} {show_meta.get(YEAR, "")}'

        count = data.get(COUNT, {})
        total = count.get(TOTAL, 0)
        retrieved = count.get(RETRIEVED, 0)

        # print(f"Match: '{query}' to {type_} '{match}' - found {total} releases (total), retrieved {retrieved}")

    return match, total, retrieved

def extract_scraped_releases(response: dict) -> List[Dict]:
    scraped_releases = []

    for res in response["data"]["streams"]:
        title = clean_title(res['file']['name'].split('\n')[0].replace(' ', '.'))
        size = (float(res["file"]["size"]) / 1000000000 if res["file"].get("size") else 0)
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
    query, altquery = normalize_queries(query, altquery)
    type_ = determine_type(altquery)
    opts = build_opts(quality_opts)
    season_number, episode_number = extract_season_episode(altquery, type_)
    opts = add_season_episode(opts, season_number, episode_number)
    url = build_url(TOKEN, query, type_, opts)
    response = session.get(url).json()

    if not response_is_successful(response):
        print("Error: Did not receive a successful response from the server.")
        return []

    if not response_has_data(response):
        # print("data not found in response")
        return []

    # print("data found in response, streams found in data, continuing...")
    match, total, retrieved = extract_match_type_total_retrieved(response, query, type_) #pylint: disable=W0612
    scraped_releases = extract_scraped_releases(response)

    if not scraped_releases:
        print("No scraped releases found in response")
        return []

    return scraped_releases

def custom_sort_size_and_seeds(item: Dict[str, Union[float, int]]) -> Tuple[float, int]:
    size_weight = item.get("size", 0) or 0
    seeds_weight = item.get("seeds", 0) or 0
    return (size_weight, seeds_weight)

TorrentItem = Dict[str, Union[float, int]]
TorrentWeights = namedtuple('TorrentWeights', ['size', 'instant', 'seeds'])

def custom_sort(item: TorrentItem) -> Tuple[float, int]:
    weights = TorrentWeights(item.get("size", 0), int(not item.get("cached", False)), item.get("seeds", 0))
    return tuple(weights)

ReleaseTags = namedtuple('ReleaseTags', ['dolby_vision', 'hdr10plus', 'hdr', 'remux', 'proper_remux', 'score'])

REMUX_REGEX = re.compile(r'remux|bdrip', re.IGNORECASE)
PROPER_REGEX = re.compile(r'\d{4}.*\bproper\b', re.IGNORECASE)
DV_REGEX = re.compile(r'\bDV\b|\bDoVi\b', re.IGNORECASE)
HDR10PLUS_REGEX = re.compile(r'\bHDR10plus\b', re.IGNORECASE)
HDR_REGEX = re.compile(r'\bhdr\b|\bVISIONPLUSHDR\b', re.IGNORECASE)

def getReleaseTags(title: str, fileSize: int) -> Dict[str, Union[bool, int]]:
    remux = bool(REMUX_REGEX.search(title))
    proper_remux = bool(PROPER_REGEX.search(title))
    dolby_vision = bool(DV_REGEX.search(title))
    hdr10plus = bool(HDR10PLUS_REGEX.search(title))
    hdr = remux or dolby_vision or hdr10plus or bool(HDR_REGEX.search(title))

    score = fileSize
    if remux:
        score += 25
    if dolby_vision or hdr10plus:
        score += 15
    if hdr:
        score += 5
    if proper_remux:
        score += 2

    return ReleaseTags(dolby_vision, hdr10plus, hdr, remux, proper_remux, score)


from requests.adapters import HTTPAdapter
import simdjson as sj

@lru_cache(maxsize=128)
def resolve_hostname(hostname: str) -> str:
    resolver = dns.resolver.Resolver()
    answer = resolver.resolve(hostname, 'A')
    return answer[0].to_text()

hostname_cache = {}
response_cache = {}

caches_path = 'caches/'

redis_host = '127.0.0.1'
redis_port = 6379
redis_db = 0

redis_connection = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
requests_cache.install_cache(f'{caches_path}tv_show_cache', expire_after=3600, backend='redis', connection=redis_connection)

def get_season_data(title: str, retries: int = 3, backoff_factor: float = 2.0) -> Optional[Dict]:
    search_params = {"api_key": TMDB_API_KEY, "query": title}
    search_url = f"{BASE_URL}/search/tv?{urlencode(search_params)}"

    retry_strategy = Retry(total=retries, backoff_factor=backoff_factor)
    adapter = HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as req_session:
        req_session.mount("https://", adapter)
        req_session.mount("http://", adapter)

        hostname = urlparse(BASE_URL).hostname

        if hostname not in hostname_cache:
            hostname_cache[hostname] = resolve_hostname(hostname)
        ip_address = hostname_cache[hostname]
        headers = {"Host": hostname, "X-Forwarded-For": ip_address}

        try:
            cache_key = f"{title}-{TMDB_API_KEY}"

            if cache_key not in response_cache:
                response_cache[cache_key] = req_session.get(search_url, timeout=10, headers=headers, verify=False)
            response = response_cache[cache_key]

            response.raise_for_status()
            search_data = sj.loads(response.content)
            tv_show = search_data.get("results", [])[0] if search_data.get("results") else None

            if tv_show:
                tv_show_id = tv_show["id"]
                tv_show_url = f"{BASE_URL}/tv/{tv_show_id}?api_key={TMDB_API_KEY}"

                tv_show_cache_key = f"{tv_show_id}-{TMDB_API_KEY}"

                if tv_show_cache_key not in response_cache:
                    response_cache[tv_show_cache_key] = req_session.get(tv_show_url, timeout=10, headers=headers, verify=False)
                tv_show_response = response_cache[tv_show_cache_key]
                tv_show_response.raise_for_status()
                tv_show_data = sj.loads(tv_show_response.content)
                return {"total_seasons": tv_show_data.get("number_of_seasons")} if tv_show_data else None
        except requests.exceptions.RequestException as exc:
            print(f"Error: {exc}")
            return None

def save_filtered_results(results: List[dict], filename: str, encoding: str = 'utf-8') -> None:
    if not filename:
        raise ValueError("Filename must not be empty")

    directory = os.path.dirname(filename)
    if directory and not os.path.exists(os.path.dirname(filename)):
        os.makedirs(directory)

    filtered_results = [item for item in results[1:] if item.get("seeds") is not None]

    with open(filename, 'w', encoding=encoding, buffering=8192) as file:
        for chunk in json.JSONEncoder(indent=4, sort_keys=True).iterencode(filtered_results):
            file.write(chunk)
        
def get_cached_instants(alldebrid: 'AllDebrid', magnets: List[str]) -> List[Union[str, bool]]:
    checkmagnets = alldebrid.check_magnet_instant(magnets=magnets)
    instant_values = [magnet_data.get('instant', False) if checkmagnets and checkmagnets['status'] == 'success' else False for magnet_data in checkmagnets['data']['magnets']] if checkmagnets else [False] * len(magnets)
    return instant_values

DEBUG = False

def search_best_qualities(title: str, title_type: str, qualities_sets: List[List[str]], filename_prefix: str):
    start_time = time.perf_counter()
    # title_type = "movie"

    def process_quality(qualities: List[str], season: Optional[int] = None):
        altquery = title if title_type == "movie" else f"{title} S{season:02d}"
        default_opts = [
            ["sortvalue", "best"],
            ["streamtype", "torrent"],
            ["limitcount", "10"],
            ["filename", "true"],
            ["videoquality", ','.join(qualities)],
        ]
        result = search(query=title, altquery=altquery, quality_opts=default_opts)
        # save_filtered_results(results=result, filename=f"postprocessing_results/{filename_prefix}_{altquery}_{','.join(qualities)}.json")
            
        if not result:
            if title_type == "tv":
                if DEBUG:
                    print(f"No results found for {title} S{season:02d} {qualities}")
            else:
                if DEBUG:
                    print(f"No results found for {title} {qualities}")
            return
        else:
            filtered_results = [item for item in result if item.get("seeds") is not None]

        magnets = (item['links'][0] for item in filtered_results)
        cached_instants = get_cached_instants(ad, magnets)
        for item, instant in zip(filtered_results, cached_instants):
            item["cached"] = instant if instant is not False else False
            print(item["cached"])

        for item in filtered_results:
            item_title = item['title']
            size = item['size']
            item['score'] = getReleaseTags(item_title, size).score

        post_processed_results = [item for item in filtered_results if item["cached"]]

        custom_sort = partial(sorted, key=lambda item: (item["cached"], item["size"], item["score"], item["seeds"]), reverse=True)
        custom_sort_size_and_seeds = partial(sorted, key=lambda item: (item["size"], item["score"], item["seeds"]), reverse=True)

        if not post_processed_results:
            post_processed_results = custom_sort_size_and_seeds(filtered_results)
        else:
            post_processed_results = custom_sort(post_processed_results)

        season_suffix = f"_{season:02d}" if season else ""
        post_processed_filename = f'postprocessing_results/{title}_{filename_prefix}_{"_".join(qualities)}_orionoid{season_suffix}_post_processed.json'

        save_filtered_results(post_processed_results, post_processed_filename)

        return post_processed_results

    num_workers = os.cpu_count()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        if title_type == MEDIA_TYPE_TV:
            season_data = get_season_data(title)
            if season_data:
                total_seasons = season_data["total_seasons"]
                futures = [executor.submit(process_quality, qualities, season) for season in range(1, total_seasons + 1) for qualities in qualities_sets]
            else:
                print(f"Could not get season data for {title}")
                return

        elif title_type == MEDIA_TYPE_MOVIE:
            futures = [executor.submit(process_quality, qualities) for qualities in qualities_sets]
        else:
            print(f"Unknown type for {title}")
            return

        for future in as_completed(futures):
            try:
                future.result()
            except (TimeoutError, CancelledError) as exc:
                print(f"Exception occurred in a task: {exc}")

    end_time = time.perf_counter()
    print(f"Finished in {end_time - start_time:0.4f} seconds")

def main():
    QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
    FILENAME_PREFIX = "result"
    search_best_qualities(title="tt3606756", title_type="movie", qualities_sets=QUALITIES_SETS, filename_prefix=FILENAME_PREFIX)

if __name__ == "__main__":
    cProfile.run("main()", filename="profiling_results.prof", sort="cumtime")
