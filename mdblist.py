from concurrent.futures import ThreadPoolExecutor
import json
import logging
import redis
from requests.adapters import HTTPAdapter
import requests
import requests_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_cache = redis.StrictRedis(host='localhost', port=6379, db=0)
requests_cache.install_cache('mdblist_cache', backend='redis', connection=redis_cache, expire_after=604800)

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

def get_movie_streams(username, listname):
    url = f"https://mdblist.com/lists/{username}/{listname}/json"
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
