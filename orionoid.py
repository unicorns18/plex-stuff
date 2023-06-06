# pylint: disable=C0301,C0116,c0303,W0612,c0103
"""
TODO: Write a docstring
"""
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import json
import logging
import os
import re
import time
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode
import redis
import requests
import requests_cache
import urllib3
import simdjson as sj
from alldebrid import APIError, AllDebrid
from constants import (
    BASE_URL,
    BASE_URL_ORIONOID,
    DEFAULT_API_KEY,
    MDBLIST_API_KEY,
    TMDB_API_KEY,
    TOKEN,
)
from exceptions import ExecutionError
from filters import clean_title

# from matching_algorithms import jaccard_similarity
from uploader import check_file_extensions

logging.basicConfig(
    filename="orionoid.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)  # noqa: E501

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

redis_cache = redis.StrictRedis(host="localhost", port=6379, db=0)
requests_cache.install_cache(
    "orionoid_cache",
    backend="redis",
    connection=redis_cache,
    expire_after=604800,  # noqa: E501
)

session = requests.Session()
ad = AllDebrid(apikey=DEFAULT_API_KEY)
SEASON_EPISODE_REGEX = re.compile(r"(S[0-9]|complete|S\?[0-9])", re.I)

SEASON_REGEX = re.compile(r"S(\d+)", re.I)
EPISODE_REGEX = re.compile(r"E(\d+)", re.I)


def build_url(token: str, query: str, type_: str, opts: str) -> str:
    if query is None:
        raise ValueError("Query cannot be None")

    params = {
        "token": token,
        "mode": "stream",
        "action": "retrieve",
        "type": type_,
    }  # noqa: E501

    if query.startswith("tt"):
        params["idimdb"] = query[2:]
    else:
        params["query"] = query

    query_params = urlencode(params)
    return f"{BASE_URL_ORIONOID}?{query_params}&{opts}"


NONE = "None"
MOVIE = "movie"
SHOW = "show"
META = "meta"
TITLE = "title"
YEAR = "year"
COUNT = "count"
TOTAL = "total"
RETRIEVED = "retrieved"

def extract_match_type_total_retrieved(response: dict) -> Tuple[Optional[str], int, int]:
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

    return match, total, retrieved



def extract_details(res: Dict) -> Dict:
    """Extract specific details from a response object."""
    meta = res.get("meta", {})
    video = res.get("video", {})
    audio = res.get("audio", {})

    details = {
        "release": meta.get("release", {}),
        "uploader": meta.get("uploader", {}),
        "quality": video.get("quality", ""),
        "codec": video.get("codec", ""),
        "audio_type": audio.get("type", ""),
        "channels": audio.get("channels", 0),
        "audio_system": audio.get("system", ""),
        "audio_codec": audio.get("codec", ""),
        "audio_languages": audio.get("languages", []),
    }

    return details


def extract_scraped_releases(response: dict) -> List[Dict]:
    scraped_releases = []

    try:
        for res in response["data"]["streams"]:
            try:
                title = clean_title(
                    res["file"]["name"].split("\n")[0].replace(" ", ".")
                )
            except TypeError as exc:
                title = None
                print(f"Error processing title: {exc}")

            try:
                size = (
                    float(res["file"]["size"]) / 1000000000
                    if "size" in res["file"]
                    and res["file"]["size"] is not None  # noqa: E501
                    else 0
                )
            except (TypeError, ValueError) as e:
                size = 0
                print(f"Error processing size: {e}")

            links = res.get("links", [])
            seeds = res.get("stream", {}).get("seeds", 0)
            source = res.get("stream", {}).get("source", "")

            details = extract_details(res)

            scraped_releases.append(
                {
                    "title": title,
                    "size": size,
                    "links": links,
                    "seeds": seeds,
                    "source": source,
                    **details,
                }
            )

    except KeyError as e:
        print(f"Error processing response data: {e}")

    return scraped_releases


SEASON_REGEX = re.compile(r"S(\d+)", re.I)
EPISODE_REGEX = re.compile(r"E(\d+)", re.I)


def search(
    query: str,
    type_: str,
    quality_opts,
    season_number: Optional[int] = None,
    max_retries: int = 3,
) -> Optional[Dict]:
    opts = "&".join(["=".join(opt) for opt in quality_opts])
    if type_ in ("show", "tv"):
        if season_number is not None:
            opts = f"{opts}&numberseason={season_number}"
    url = build_url(TOKEN, query, type_, opts)
    print(url)

    retries = 0
    while retries < max_retries:
        try:
            response = session.get(url).json()
            break
        except (
            ConnectionError,
            requests.Timeout,
            requests.TooManyRedirects,
        ) as exc:  
            retries += 1
            print(
                f"Error occurred while attempting to fetch data: {exc}. Retrying in 5 seconds. Attempt {retries} of {max_retries}"  
            )
            time.sleep(5)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"An unexpected error occurred: {exc}")
            logging.exception("An unexpected error occurred")
            return {"error": str(exc)}
        finally:
            session.close()
    else:
        error_message = (
            f"Failed to retrieve data after {max_retries} attempts."  
        )
        print(error_message)
        return {"error": error_message}

    if response.get("result", {}).get("status") != "success":
        error_message = "Error: Did not receive a successful response from the server." 
        print(error_message)
        return {"error": error_message}

    if "data" not in response or "streams" not in response["data"]:
        error_message = "Data not found in response"
        print(error_message)
        return {"error": error_message}

    _, _, _ = extract_match_type_total_retrieved(response) 
    scraped_releases = extract_scraped_releases(response)

    if not scraped_releases:
        error_message = "No scraped releases found in response"
        print(error_message)
        return {"error": error_message}

    return scraped_releases


def custom_sort_size_and_seeds(
    item: Dict[str, Union[float, int]]
) -> Tuple[float, int]:  # noqa: E501
    size_weight = item.get("size", 0) or 0
    seeds_weight = item.get("seeds", 0) or 0
    return (size_weight, seeds_weight)


TorrentItem = Dict[str, Union[float, int]]
TorrentWeights = namedtuple("TorrentWeights", ["size", "instant", "seeds"])


def custom_sort(item: TorrentItem) -> Tuple[float, int]:
    weights = TorrentWeights(
        item.get("size", 0),
        int(not item.get("cached", False)),
        item.get("seeds", 0),  # noqa: E501
    )
    return tuple(weights)


ReleaseTags = namedtuple(
    "ReleaseTags",
    ["dolby_vision", "hdr10plus", "hdr", "remux", "proper_remux", "score"],
)

REMUX_REGEX = re.compile(r"remux|bdrip", re.IGNORECASE)
PROPER_REGEX = re.compile(r"\d{4}.*\bproper\b", re.IGNORECASE)
DV_REGEX = re.compile(r"\bDV\b|\bDoVi\b", re.IGNORECASE)
HDR10PLUS_REGEX = re.compile(r"\bHDR10plus\b", re.IGNORECASE)
HDR_REGEX = re.compile(r"\bhdr\b|\bVISIONPLUSHDR\b", re.IGNORECASE)


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

    return ReleaseTags(
        dolby_vision, hdr10plus, hdr, remux, proper_remux, score
    )  # noqa: E501


hostname_cache = {}
response_cache = {}


def get_season_data(
    title: str = None, retries: int = 3, backoff_factor: float = 2.0
) -> Optional[Dict]:
    if re.match(r"tt\d{7,8}", title):
        return get_season_data_imdb(title, retries, backoff_factor)
    return get_season_data_title(title, retries, backoff_factor)


def get_season_data_imdb(
    imdb_id: str, retries: int, backoff_factor: float
) -> Optional[Dict]:

    retry_strategy = urllib3.util.Retry(
        total=retries, backoff_factor=backoff_factor
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as req_session:
        req_session.mount("https://", adapter)
        req_session.mount("http://", adapter)

        try:
            search_params = {
                "api_key": TMDB_API_KEY,
                "external_source": "imdb_id",
            }
            response = req_session.get(
                f"{BASE_URL}/find/{imdb_id}?{urlencode(search_params)}", 
                timeout=10,
            )
            response.raise_for_status()

            tv_show_id = sj.loads(response.content).get("tv_results", [{}])[0].get("id")
            if tv_show_id is not None:
                response = req_session.get(
                    f"{BASE_URL}/tv/{tv_show_id}?api_key={TMDB_API_KEY}", 
                    timeout=10,
                )
                response.raise_for_status()
                return {"total_seasons": sj.loads(response.content).get("number_of_seasons")}

        except requests.exceptions.RequestException as exc:
            print(f"Error: {exc}")

    return None


def get_season_data_title(
    title: str, retries: int, backoff_factor: float
) -> Optional[Dict]:

    retry_strategy = urllib3.util.Retry(
        total=retries, backoff_factor=backoff_factor
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as req_session:
        req_session.mount("https://", adapter)
        req_session.mount("http://", adapter)

        try:
            search_params = {"api_key": TMDB_API_KEY, "query": title}
            response = req_session.get(f"{BASE_URL}/search/tv?{urlencode(search_params)}", timeout=10)
            response.raise_for_status()

            tv_show_id = sj.loads(response.content).get("results", [{}])[0].get("id")
            if tv_show_id is not None:
                response = req_session.get(
                    f"{BASE_URL}/tv/{tv_show_id}?api_key={TMDB_API_KEY}",
                    timeout=10,
                )
                response.raise_for_status()
                return {"total_seasons": sj.loads(response.content).get("number_of_seasons")}

        except requests.exceptions.RequestException as exc:
            print(f"Error: {exc}")

    return None


def get_cached_instants(
    alldebrid: "AllDebrid", magnets: List[str]
) -> List[Union[str, bool]]:
    # EXCLUDED_EXTENSIONS = [".rar", ".iso", ".zip", ".7z", ".gz", ".bz2", ".xz"]  # noqa: E501
    magnets = list(magnets)  # convert generator to list
    try:
        checkmagnets = alldebrid.check_magnet_instant(magnets=magnets)
        if not checkmagnets or checkmagnets["status"] != "success":
            print(
                "Failed to check magnets. Defaulting to False for all magnets."
            )  # noqa: E501
            return [False] * len(magnets)

        return [
            magnet_data.get("cached", False)
            for magnet_data in checkmagnets["data"]["magnets"]
        ]
        # return [magnet_data.get('instant', False) for magnet_data in checkmagnets['data']['magnets']]  # noqa: E501
    except APIError as exc:
        print(f"APIError occured: {exc}")
    except ValueError as exc:
        print(f"ValueError occured: {exc}")
    return [False] * len(magnets)


multi_season_regex = re.compile(r"S\d{2}-S\d{2}", re.IGNORECASE)


def get_title_type(title: str, year: Optional[int] = None):
    # Your API key
    api_key = MDBLIST_API_KEY

    # IMDB ID pattern
    imdb_id_pattern = r"^tt\d+$"

    # Define the endpoint URLs
    if re.match(imdb_id_pattern, title):
        url_template = f"https://mdblist.com/api/?apikey={api_key}&i={title}"
    else:
        url_template = f"https://mdblist.com/api/?apikey={api_key}&s={title}&y={year}"  # noqa: E501

    print(url_template)

    cached_response = redis_cache.get(url_template)
    if cached_response:
        data = json.loads(cached_response)
    else:
        try:
            response = requests.get(url_template, timeout=30)
            response.raise_for_status()  # Will raise an HTTPError if the status is 4xx, 5xx  # noqa: E501
        except requests.exceptions.RequestException as err:
            print(f"Error: Request to MDBlist API failed due to {err}")
            return None

        data = response.json()

        redis_cache.set(url_template, json.dumps(data), ex=86400)

    try:
        if re.match(imdb_id_pattern, title):
            title_type = data["type"]
        else:
            title_type = data["search"][0]["type"]
    except (KeyError, IndexError) as err:
        print(
            f"Error: Expected data not found in the MDBlist API response. Details: {err}"  # noqa: E501
        )
        return None

    return title_type


# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
def search_best_qualities(
    title: str,
    qualities_sets: List[List[str]],
    title_type: Optional[str] = None,
    season: Optional[int] = None,
    max_results: Optional[int] = None,
    sort_order: Optional[str] = "best",
    min_seeds: Optional[int] = None,
    filter_uncached: Optional[bool] = False,
    sort_by_quality: Optional[bool] = False,
):
    start_time = time.perf_counter()

    year_match = re.search(r"\b\d{4}\b", title)
    year = int(year_match.group(0)) if year_match else None
    title = title.replace(str(year), "") if year else title
    title = title.replace("()", "").strip()
    title_type = get_title_type(title.strip(), year)

    if title_type not in ("movie", "show"):
        raise ValueError("title_type must be either 'movie' or 'show'")

    def process_quality(qualities: List[str], season: Optional[int] = None):
        result = search(
            query=title,
            type_=title_type,
            quality_opts=[
                ["sortvalue", sort_order],
                ["streamtype", "torrent"],
                ["limitcount", str(max_results) if max_results else "100"],
                ["filename", "true"],
                ["videoquality", ",".join(qualities)],
            ],
            season_number=season,
        )
        if "error" in result:
            print(f"An error occurred during the search: {result['error']}")
            return

        filtered_results = [
            item
            for item in result
            if item.get("seeds") is not None
            and not multi_season_regex.search(item["title"])
            and (min_seeds is None or item.get("seeds", 0) >= min_seeds)
        ]
        magnets = (item["links"][0] for item in filtered_results)
        cached_instants = get_cached_instants(ad, magnets)
        for item, instant in zip(filtered_results, cached_instants):
            item["cached"] = instant if instant else False
            item["has_excluded_extension"] = False
            item["reason"] = None
            if item["cached"]:
                for link in item["links"]:
                    has_excluded_extension, reason = check_file_extensions(
                        link
                    )  # noqa: E501
                    if has_excluded_extension:
                        item["has_excluded_extension"] = True
                        item["reason"] = reason
                        break

        if filter_uncached:
            filtered_results = [item for item in filtered_results if item["cached"]]  # noqa: E501

        for item in filtered_results:
            item["score"] = getReleaseTags(item["title"], item["size"]).score

        if sort_by_quality:
            quality_index = qualities_sets.index(qualities)
            post_processed_results = sorted(
                filtered_results,
                key=lambda item: (
                    item["cached"],
                    item["size"],
                    item["score"],
                    item["seeds"],
                    quality_index,
                ),
                reverse=True,
            )
        else:
            post_processed_results = sorted(
                filtered_results,
                key=lambda item: (
                    item["cached"],
                    item["size"],
                    item["score"],
                    item["seeds"],
                ),
                reverse=True,
            )

        return post_processed_results if filtered_results else None

    results = []
    exceptions = []
    num_workers = os.cpu_count()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {}
        if title_type in ("tv", "show"):
            season_data = get_season_data(title)
            if not season_data:
                print(f"Could not get season data for {title}")
                return
            total_seasons = season_data["total_seasons"]
            all_combinations = list(
                itertools.product(range(1, total_seasons + 1), qualities_sets)
            )
            if season:
                all_combinations = [
                    combo for combo in all_combinations if combo[0] == season
                ]
            futures = {
                executor.submit(process_quality, qualities, season): (
                    qualities,
                    season,
                )  # noqa: E501
                for season, qualities in all_combinations
            }
        elif title_type == "movie":
            futures = {
                executor.submit(process_quality, qualities): qualities
                for qualities in qualities_sets
            }
        else:
            print(f"Invalid title type for {title}")
            return

        for future in as_completed(futures):
            if title_type == "movie":
                qualities = futures[future]
                season = None
            else:
                qualities, season = futures[future]
            try:
                data = future.result()
                if isinstance(data, list):
                    results.extend(data)
                elif data is not None:
                    results.append(data)
            except ExecutionError as exc:
                print(
                    f'{qualities} {season if season else ""} generated an exception: {exc}'  # noqa: E501
                )
                exceptions.append(exc)

    if exceptions:
        raise exceptions[0]

    end_time = time.perf_counter()
    rounded_end_time = round(end_time - start_time, 2)
    print(f"Finished in {rounded_end_time} seconds")
    return results
