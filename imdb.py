import requests
import requests_cache

class TMDbSearcher:
    def __init__(self, api_key: str, api_base_url: str = "https://api.themoviedb.org/3", http_client=None):
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.http_client = http_client or requests

    def search_and_get_details(self, title: str) -> dict:
        search_result = self.search(title)
        if search_result:
            movie_details = self.get_movie_details(search_result['id'])
            return movie_details
        else:
            return None

    def search(self, title: str) -> dict:
        self._validate_title(title)
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

    def _build_url(self, title: str) -> str:
        return f'{self.api_base_url}/search/movie?api_key={self.api_key}&query={title}'

    def _fetch_data(self, url: str) -> dict:
        try:
            response = self.http_client.get(url, timeout=60)
            response.raise_for_status()
            return response
        except self.http_client.exceptions.RequestException as err:
            print('Error:', err)
            return None

    def _handle_response(self, json_data: dict) -> dict:
        if not json_data['results']:
            print('No results found')
            return None
        else:
            return json_data['results'][0]

    def get_movie_details(self, movie_id: str) -> dict:
        url = f"{self.api_base_url}/movie/{movie_id}?api_key={self.api_key}"
        response = self._fetch_data(url)

        if response is None:
            return None

        return response.json()

API_KEY = 'cea9c08287d26a002386e865744fafc8'
CACHE_EXPIRATION_TIME = 43200  # 12 hours

requests_cache.install_cache('tmdb_cache', expire_after=CACHE_EXPIRATION_TIME, backend='sqlite')
cached_session = requests_cache.CachedSession()

movie_searcher = TMDbSearcher(api_key=API_KEY, http_client=cached_session)
result = movie_searcher.search_and_get_details('Jack Reacher: Never Go Back')
print(result['imdb_id'])