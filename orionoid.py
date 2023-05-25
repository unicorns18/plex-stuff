#pylint: disable=C0301,C0116,c0303
"""
TODO: Write a docstring
"""
import cProfile
from collections import namedtuple
from functools import partial, wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import json
import os
import re
import time
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode
import redis
import requests
import requests_cache
import urllib3
import requests
import simdjson as sj
import ujson
from alldebrid import APIError, AllDebrid
from constants import BASE_URL, BASE_URL_ORIONOID, DEFAULT_API_KEY, TMDB_API_KEY, TOKEN
from filters import clean_title
from matching_algorithms import jaccard_similarity, levenshtein_distance
from uploader import debrid_persistence_checks, check_file_extensions, extract_title_from_magnets_dn, process_magnet

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

redis_cache = redis.StrictRedis(host='localhost', port=6379, db=0)
requests_cache.install_cache('orionoid_cache', backend='redis', connection=redis_cache, expire_after=604800)

session = requests.Session()
ad = AllDebrid(apikey=DEFAULT_API_KEY)
SEASON_EPISODE_REGEX = re.compile(r'(S[0-9]|complete|S\?[0-9])', re.I)

SEASON_REGEX = re.compile(r'S(\d+)', re.I)
EPISODE_REGEX = re.compile(r'E(\d+)', re.I)

def build_url(token: str, query: str, type_: str, opts: str) -> str:
    if query is None:
        raise ValueError("Query cannot be None")

    params = {'token': token, 'mode': 'stream', 'action': 'retrieve', 'type': type_}

    if query.startswith('tt'):
        params['idimdb'] = query[2:]
    else:
        params['query'] = query

    query_params = urlencode(params)
    return f'{BASE_URL_ORIONOID}?{query_params}&{opts}'

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

    try:
        for res in response["data"]["streams"]:
            try:
                title = clean_title(res['file']['name'].split('\n')[0].replace(' ', '.'))
            except Exception as e:
                title = None
                print(f"Error processing title: {e}")

            try:
                size = (float(res["file"]["size"]) / 1000000000 if "size" in res["file"] and res["file"]["size"] is not None else 0)
            except Exception as e:
                size = 0
                print(f"Error processing size: {e}")

            links = res.get("links", [])
            seeds = res.get("stream", {}).get("seeds", 0)
            source = res.get("stream", {}).get("source", "")
            quality = res.get("video", {}).get("quality", "")

            # additional information useful for filtering and scoring
            meta = res.get("meta", {})
            release = meta.get("release", {})
            uploader = meta.get("uploader", {})

            video = res.get("video", {})
            quality = video.get("quality", "")
            codec = video.get("codec", "")

            audio = res.get("audio", {})
            audio_type = audio.get("type", "")
            channels = audio.get("channels", 0)
            audio_system = audio.get("system", "")
            audio_codec = audio.get("codec", "")
            audio_langs = audio.get("languages", [])

            scraped_releases.append({
                "title": title,
                "size": size,
                "links": links,
                "seeds": seeds,
                "source": source,
                "quality": quality,
                "release": release,
                "uploader": uploader,
                "codec": codec,
                "audio_type": audio_type,
                "channels": channels,
                "audio_system": audio_system,
                "audio_codec": audio_codec,
                "audio_languages": audio_langs
            })

    except Exception as e:
        print(f"Error processing response data: {e}")

    return scraped_releases

SEASON_REGEX = re.compile(r'S(\d+)', re.I)
EPISODE_REGEX = re.compile(r'E(\d+)', re.I)
    
def search(query: str, altquery: str, type_: str, quality_opts, season_number: Optional[int] = None, max_retries: int = 3) -> Optional[Dict]:
    if altquery == "(.*)":
        altquery = query
    else:
        query = f"{query} {altquery}"
    opts = '&'.join(['='.join(opt) for opt in quality_opts])
    if type_ == "show" or type_ == "tv": 
        if season_number is not None:
            opts = f"{opts}&numberseason={season_number}"
    url = build_url(TOKEN, query, type_, opts,) 

    retries = 0
    while retries < max_retries:
        try:
            response = session.get(url).json()
            break
        except (ConnectionError, requests.Timeout, requests.TooManyRedirects) as e:
            retries += 1
            print(f"Error occurred while attempting to fetch data: {e}. Retrying in 5 seconds. Attempt {retries} of {max_retries}")
            time.sleep(5)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    else:
        error_message = f"Failed to retrieve data after {max_retries} attempts."
        print(error_message)
        return {"error": error_message}

    if response.get('result', {}).get('status') != 'success':
        error_message = "Error: Did not receive a successful response from the server."
        print(error_message)
        return {"error": error_message}

    if "data" not in response or "streams" not in response["data"]:
        error_message = "Data not found in response"
        print(error_message)
        return {"error": error_message}

    match, total, retrieved = extract_match_type_total_retrieved(response, query, type_) #pylint: disable=W0612
    scraped_releases = extract_scraped_releases(response)

    if not scraped_releases:
        error_message = "No scraped releases found in response"
        print(error_message)
        return {"error": error_message}

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

hostname_cache = {}
response_cache = {}

def get_season_data(title: str = None, retries: int = 3, backoff_factor: float = 2.0) -> Optional[Dict]:
    if re.match(r'tt\d{7,8}', title):
        return get_season_data_imdb(title, retries, backoff_factor)
    else:
        return get_season_data_title(title, retries, backoff_factor)
    
def get_season_data_imdb(imdb_id: str, retries: int, backoff_factor: float) -> Optional[Dict]:
    retry_strategy = urllib3.util.Retry(total=retries, backoff_factor=backoff_factor)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as req_session:
        req_session.mount("https://", adapter)
        req_session.mount("http://", adapter)

        try:
            search_params = {"api_key": TMDB_API_KEY, "external_source": "imdb_id"}
            search_url = f"{BASE_URL}/find/{imdb_id}?{urlencode(search_params)}"
            
            response = req_session.get(search_url, timeout=10, verify=False)
            response.raise_for_status()
            search_data = sj.loads(response.content)

            tv_results = search_data.get("tv_results", [])
            if tv_results:
                tv_show = tv_results[0]
                tv_show_id = tv_show["id"]
                tv_show_url = f"{BASE_URL}/tv/{tv_show_id}?api_key={TMDB_API_KEY}"

                tv_show_response = req_session.get(tv_show_url, timeout=10, verify=False)
                tv_show_response.raise_for_status()
                tv_show_data = sj.loads(tv_show_response.content)
                
                return {"total_seasons": tv_show_data.get("number_of_seasons")} if tv_show_data else None
        except requests.exceptions.RequestException as exc:
            print(f"Error: {exc}")
            return None

def get_season_data_title(title: str, retries: int, backoff_factor: float) -> Optional[Dict]:
    retry_strategy = urllib3.util.Retry(total=retries, backoff_factor=backoff_factor)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as req_session:
        req_session.mount("https://", adapter)
        req_session.mount("http://", adapter)

        try:
            search_params = {"api_key": TMDB_API_KEY, "query": title}
            search_url = f"{BASE_URL}/search/tv?{urlencode(search_params)}"
            
            response = req_session.get(search_url, timeout=10, verify=False)
            response.raise_for_status()
            search_data = sj.loads(response.content)

            results = search_data.get("results", [])
            if results:
                tv_show = results[0]
                tv_show_id = tv_show["id"]
                tv_show_url = f"{BASE_URL}/tv/{tv_show_id}?api_key={TMDB_API_KEY}"

                tv_show_response = req_session.get(tv_show_url, timeout=10, verify=False)
                tv_show_response.raise_for_status()
                tv_show_data = sj.loads(tv_show_response.content)
                
                return {"total_seasons": tv_show_data.get("number_of_seasons")} if tv_show_data else None
        except requests.exceptions.RequestException as exc:
            print(f"Error: {exc}")
            return None

def get_cached_instants(alldebrid: 'AllDebrid', magnets: List[str]) -> List[Union[str, bool]]:
    EXCLUDED_EXTENSIONS = ['.rar', '.iso', '.zip', '.7z', '.gz', '.bz2', '.xz']
    magnets = list(magnets)  # convert generator to list
    try:
        checkmagnets = alldebrid.check_magnet_instant(magnets=magnets)
        if not checkmagnets or checkmagnets['status'] != 'success':
            print("Failed to check magnets. Defaulting to False for all magnets.")
            return [False] * len(magnets)
        
        return [magnet_data.get('instant', False) for magnet_data in checkmagnets['data']['magnets']]
    except APIError as exc:
        print(f"APIError occured: {exc}")
    except ValueError as exc:
        print(f"ValueError occured: {exc}")
    except Exception as exc:
        print(f"Unknown error occured: {exc}")
    return [False] * len(magnets)

multi_season_regex = re.compile(r'S\d{2}-S\d{2}', re.IGNORECASE)

def get_title_type(title: str, year: Optional[int] = None):
    # Your API key
    api_key = "uwk2jbhy7acivnyzpq44hh70y"

    # IMDB ID pattern
    imdb_id_pattern = r"^tt\d+$"

    # Define the endpoint URLs
    if re.match(imdb_id_pattern, title):
        url_template = f"https://mdblist.com/api/?apikey={api_key}&i={title}"
    else:
        url_template = f"https://mdblist.com/api/?apikey={api_key}&s={title}&y={year}"

    print(url_template)

    cached_response = redis_cache.get(url_template)
    if cached_response:
        data = json.loads(cached_response)
    else:
        try:
            response = requests.get(url_template)
            response.raise_for_status()  # Will raise an HTTPError if the status is 4xx, 5xx
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
        print(f"Error: Expected data not found in the MDBlist API response. Details: {err}")
        return None

    return title_type

def search_best_qualities(title: str, qualities_sets: List[List[str]], filename_prefix: str, title_type: Optional[str] = None):
    start_time = time.perf_counter()

    year_match = re.search(r'\b\d{4}\b', title)
    year = int(year_match.group(0)) if year_match else None
    title = title.replace(str(year), '') if year else title
    title = title.replace('()', '').strip()
    title_type = get_title_type(title.strip(), year)

    if title_type not in ("movie", "show"):
        raise ValueError("title_type must be either 'movie' or 'show'")

    def process_quality(qualities: List[str], season: Optional[int] = None):
        altquery = title_type if title_type == "movie" else f"{title} S{season:02d}"
        default_opts = [
            ["sortvalue", "best"],
            ["streamtype", "torrent"],
            ["limitcount", "20"],
            ["filename", "true"],
            ["videoquality", ','.join(qualities)],
        ]
        # print(title, altquery)
        result = search(query=title, altquery=altquery, type_=title_type, quality_opts=default_opts, season_number=season)
        if "error" in result:
            print(f"An error occurred during the search: {result['error']}")
            return

        filtered_results = [item for item in result if item.get("seeds") is not None and not multi_season_regex.search(item['title'])]

        magnets = (item['links'][0] for item in filtered_results)
        cached_instants = get_cached_instants(ad, magnets)
        for item, instant in zip(filtered_results, cached_instants):
            item["cached"] = instant if instant else False
            item['has_excluded_extension'] = False
            item['reason'] = None
            if item["cached"]:
                for link in item["links"]:
                    has_excluded_extension, reason = check_file_extensions(link)
                    if has_excluded_extension:
                        item['has_excluded_extension'] = True
                        item['reason'] = reason
                        break

        for item in filtered_results:
            item_title = item['title']
            size = item['size']
            item['score'] = getReleaseTags(item_title, size).score

        post_processed_results = [item for item in filtered_results if item["cached"] or not item["cached"]]

        custom_sort = partial(sorted, key=lambda item: (item["cached"], item["size"], item["score"], item["seeds"]), reverse=True)
        custom_sort_size_and_seeds = partial(sorted, key=lambda item: (item["size"], item["score"], item["seeds"]), reverse=True)

        if not post_processed_results:
            post_processed_results = custom_sort_size_and_seeds(filtered_results)
        else:
            post_processed_results = custom_sort(post_processed_results)

        season_suffix = f"_{season:02d}" if season else ""
        post_processed_filename = f'results/{title}_{filename_prefix}_{"_".join(qualities)}_orionoid{season_suffix}_post_processed.json'
        results_to_save = post_processed_results if post_processed_results else filtered_results

        return results_to_save
    
    results = []
    exceptions = []
    num_workers = os.cpu_count()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        if title_type == "tv" or title_type == "show":
            season_data = get_season_data(title)
            if season_data:
                total_seasons = season_data["total_seasons"]
                all_combinations = list(itertools.product(range(1, total_seasons + 1), qualities_sets))
                futures = {executor.submit(process_quality, qualities, season): (qualities, season) for season, qualities in all_combinations}
            else:
                print(f"Could not get season data for {title}")
                return
        elif title_type == "movie":
            futures = {executor.submit(process_quality, qualities): qualities for qualities in qualities_sets}
        else:
            print(f"Unknown type for {title}")
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
                else:
                    results.append(data)
            except Exception as exc:
                print(f'{qualities} {season if season else ""} generated an exception: {exc}')
                exceptions.append(exc)

    if exceptions:
        raise exceptions[0]

    end_time = time.perf_counter()
    rounded_end_time = round(end_time - start_time, 2)
    print(f"Finished in {rounded_end_time} seconds")
    return results

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB

CORS(app)

QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
FILENAME_PREFIX = "result"

@app.route("/upload_to_debrid", methods=['POST'])
def upload_to_debrid():
    magnet = request.get_json()['magnet']

    if not magnet:
        print("Debug: Missing or invalid magnet parameter.")
        return jsonify({'error': 'Missing or invalid magnet parameter.'}), 400

    max_retries = 3
    delay_between_retries = 5  # seconds

    for attempt in range(max_retries):
        print(f"Debug: Attempt {attempt + 1} of {max_retries}")
        try:
            response, status_code = process_magnet(magnet)

            if status_code == 200:
                title = extract_title_from_magnets_dn(magnet)
                print(f"Debug: Title extracted - {title}")
                persistence_check = debrid_persistence_checks(title=title)

                if persistence_check['status'] == 'error':
                    if attempt < max_retries - 1:  # If we haven't reached max retries yet, we sleep and then retry
                        time.sleep(delay_between_retries)
                        continue
                    else:  # We've reached max retries, so we return an error
                        return jsonify({'error': 'Max retries reached during process_magnet phase. DM unicorns pls.'}), 500
                
                for links in persistence_check['data']['links']:
                    if 'filename' in links:
                        filename = os.path.splitext(links['filename'])[0]
                        similarity = jaccard_similarity(title, filename)
                        confidence = similarity * 100
                        print(f"Debug: {title} is {confidence}% similar to {links['filename']}")
                        if confidence >= 60:
                            return jsonify({'success': 'Magnet processed successfully and exists in AllDebrids links.'}), 200
                        else:
                            print(f"Debug: {title} is not in {links['filename']}")
                            continue

        except (ValueError, APIError) as exc:
            print(f"Debug: Exception caught - {exc}")
            return jsonify({'error': 'Something went wrong during the process_magnet phase. DM unicorns pls.'}), 500

@app.route("/search_id", methods=["POST"])
def search_id():
    imdb_id = request.args.get('imdb_id')

    if not imdb_id or not re.match(r'tt\d{7}', imdb_id):
        return jsonify({'error': 'Invalid IMDb ID format.'}), 400

    try:
        res = search_best_qualities(title=imdb_id, qualities_sets=QUALITIES_SETS, filename_prefix=FILENAME_PREFIX)
    except ValueError as ve:
        print(ve)
        return jsonify({'error': 'Invalid input value.'}), 400
    except Exception as exc:
        print(exc)
        return jsonify({'error': 'Something went wrong during the search_best_qualities phase. DM unicorns pls.'}), 500
    
    return jsonify(res)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='1337', debug=True)
