#pylint: disable=C0301,C0303
"""
Module for searching movies (and TV shows) from IMDB.

Classes
-------
IMDBSearcher

Functions
---------
search_movie(title)

Constants
---------
api_key
api_base_url
http_client (http_client is optional, but if you'd like to cache the data, you can pass requests_cache.CachedSession)

Example
-------
>>> from imdb import OMDbSearcher
>>> movie_searcher = OMDbSearcher(api_key=api_key, api_base_url=api_base_url, http_client=cached_session)
>>> result = movie_searcher.search('Inception')
>>> print(result['results'][0]['id'])
tt1375666
"""
import requests
import requests_cache

class OMDbSearcher:
    def __init__(self, api_key: str, api_base_url: str = "http://www.omdbapi.com", http_client=None):
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.http_client = http_client or requests

    def search(self, title: str) -> dict:
        self._validate_title(title)
        title = self._quote_title(title)
        url = self._build_url(title)
        response = self._fetch_data(url)

        if response is None:
            return None

        json_data = response.json()
        return self._handle_response(json_data)

    def _validate_title(self, title: str) -> None:
        if not isinstance(title, str):
            raise TypeError('Movie title must be a string')
        if not title:
            raise ValueError('No movie title provided')

    def _quote_title(self, title: str) -> str:
        return requests.utils.quote(title)

    def _build_url(self, title: str) -> str:
        return f'{self.api_base_url}/?apikey={self.api_key}&t={title}'

    def _fetch_data(self, url: str) -> dict:
        try:
            response = self.http_client.get(url, timeout=60)
            response.raise_for_status()
            return response
        except self.http_client.exceptions.RequestException as err:
            print('Error:', err)
            return None

    def _handle_response(self, json_data: dict) -> dict:
        if json_data['Response'] == 'False':
            print('Error:', json_data['Error'])
            return None
        else:
            return json_data

API_URL = '72cb4f7f'
CACHE_EXPIRATION_TIME = 43200 # 12 hours

requests_cache.install_cache('imdb_cache', expire_after=CACHE_EXPIRATION_TIME, backend='sqlite')
cached_session = requests_cache.CachedSession()

movie_searcher = OMDbSearcher(api_key=API_URL, http_client=cached_session)
result = movie_searcher.search('Game of Thrones')
print(result['imdbID']) 
