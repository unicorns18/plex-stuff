from concurrent.futures import ThreadPoolExecutor
import json
import logging
from requests.adapters import HTTPAdapter
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_stream_data(session, imdb_id):
    streams_url = f"https://mdblist.com/api/?apikey=uwk2jbhy7acivnyzpq44hh70y&i={imdb_id}"
    try:
        response = session.get(streams_url).json()
        if not response.get('response', True):
            # logger.info(f"No response for imdb_id {imdb_id}. API limit may have been reached.")
            return None
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException for imdb_id {imdb_id}: {e}")
        return None

def get_movie_streams():
    url = "https://mdblist.com/lists/suitability/to-watch-movies-all-time/json"
    try:
        response = requests.get(url)
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {e}")
        return {}

    title_imdb_dict = {item['title']: item['imdb_id'] for item in data}

    with requests.Session() as session:
        # Increase the maxsize of the connection pool
        session.mount('https://', HTTPAdapter(pool_maxsize=100))

        with ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(fetch_stream_data, [session] * len(title_imdb_dict.values()), title_imdb_dict.values())
            results = [res for res in results if res is not None]

    return title_imdb_dict
