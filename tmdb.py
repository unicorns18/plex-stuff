"""
TODO: Add docstring. (DEPRECATED)
"""
# from functools import lru_cache
# import logging
# from typing import Optional
# from urllib.parse import urljoin
# import httpx

# import requests
# TMDB_API_KEY = "cea9c08287d26a002386e865744fafc8"
# TMDB_API_URL = "https://api.themoviedb.org/3"

# TIMEOUT = 10
# MEDIA_TYPE_MOVIE = "movie"
# MEDIA_TYPE_TV = "tv" or "show"

# def is_movie_or_tv_show(title: str, api_key: str, api_url: str) -> Optional[str]:
#     """
#     Check whether a given title is a movie or a TV show.

#     Parameters
#     ----------
#     title : str
#         The title to check.
#     api_key : str
#         The API key to use for the request.
#     api_url : str
#         The base URL of the API.

#     Returns
#     -------
#     Optional[str]
#         "movie" if the title is a movie, "tv" if the title is a TV show,
#         or None if the title is not found or the API request fails.
#     """
#     response = make_api_request(title, api_key, api_url)
#     if response is not None:
#         return process_response(response)
#     else:
#         return None

# @lru_cache(maxsize=None)
# def make_api_request(title: str, api_key: str, api_url: str) -> Optional[httpx.Response]:
#     endpoint = "3/search/multi"
#     params = {
#         "api_key": api_key,
#         "query": title,
#     }
#     try:
#         response = httpx.get(urljoin(api_url, endpoint), params=params, timeout=TIMEOUT)
#         response.raise_for_status()
#         return response
#     except (httpx.RequestError, httpx.HTTPStatusError) as exc:
#         logging.error("Error while checking title %s: %s", title, exc)
#         return None

# def process_response(response: requests.Response) -> Optional[str]:
#     """
#     TODO: Add docstring.
#     """
#     data = response.json()
#     print(data)
#     if data.get("results"):
#         result = data.get("results")[0]
#         if result.get("media_type") == MEDIA_TYPE_MOVIE:
#             return MEDIA_TYPE_MOVIE
#         elif result.get("media_type") == MEDIA_TYPE_TV:
#             return MEDIA_TYPE_TV
#     return None