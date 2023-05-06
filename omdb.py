"""
Module for the OMDB API.

Classes
-------
OmdbApi

Exceptions
----------
RequestException
ValueError

Functions
---------
get_title(title: str) -> str

Example
-------
>>> from omdb import OmdbApi
>>> omdb = OmdbApi("YOUR_API_KEY")
>>> omdb.get_title("Breaking Bad")
'TV Show'
"""
from typing import Dict, Union
import requests
from requests.exceptions import RequestException

class OmdbApi:
    """
    A class to fetch and identify if a given title is a movie or a TV show
    using the OMDb API.
    """

    TITLE_NOT_FOUND = "Title not found"
    MOVIE = "Movie"
    TV_SHOW = "TV Show"
    UNKNOWN = "Unknown"
    ERROR = "Error"
    RESPONSE_FALSE = {"Response": "False"}

    def __init__(self, api_key: str):
        """
        Initialize MovieOrShowFinder with the API key.

        Parameters
        ----------
        api_key : str
        """
        self.api_key = api_key

    def _build_url(self, title: str) -> str:
        """
        Build the URL for the OMDb API request.

        Parameters
        ----------
        title : str
        
        Returns
        -------
        str
        """
        return f"http://www.omdbapi.com/?t={title}&apikey={self.api_key}"

    def _fetch_data(self, url: str) -> Dict[str, Union[str, bool]]:
        """
        Fetch data from the OMDb API.

        Parameters
        ----------
        url : str
        
        Returns
        -------
        dict
        """
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            print(f"Request error: {exc}")
            return self.RESPONSE_FALSE
        except ValueError as exc:
            print(f"JSON decoding error: {exc}")
            return self.RESPONSE_FALSE

    def _get_title_type(self, data: Dict[str, Union[str, bool]]) -> str:
        """
        Determine the type of the title from the API response data.

        Parameters
        ----------
        data : dict
        
        Returns
        -------
        str
        """
        if data.get("Response") == "False":
            return self.TITLE_NOT_FOUND
        elif data.get("Type") == "movie":
            return self.MOVIE
        elif data.get("Type") == "series":
            return self.TV_SHOW
        else:
            return self.UNKNOWN

    def get_title(self, title: str) -> str:
        """
        Get the type of the title (movie, TV show, or unknown).

        Parameters
        ----------
        title : str
        
        Returns
        -------
        str
        """
        try:
            url = self._build_url(title)
            data = self._fetch_data(url)
            return self._get_title_type(data)
        except (RequestException, ValueError) as exc:
            print(f"Request or JSON decoding error: {exc}")
            return self.ERROR

# if __name__ == "__main__":
#     APIKEY = "ff90d66b"
#     FINDER = OmdbApi(APIKEY)
#     TITLE = "Breaking Bad"
#     RESULT = FINDER.get_title(TITLE)
#     print(f"{TITLE} is a {RESULT}")
