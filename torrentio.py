# #pylint: disable=C0114,C0301
# import json
# import copy
# import regex
# import requests
# from exceptions import IMDBIdNotFoundError, TorrentIOError
# from filters import clean_title

# DEFAULT_OPTS = "https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/manifest.json"
# #LAST_CALL_TIME = 0
# session = requests.Session()

# def get(url: str) -> None:
#     """
#     Sends a GET request to URL.

#     Parameters
#     ----------
#     url: str
#         URL for GET request.

#     Returns
#     -------
#     None
#     """
#     try:
#         response = session.get(url,timeout=60)
#         response = json.loads(response.content)
#         return response
#     except Exception: # pylint: disable=W0703
#         return None

# def scrape(query: str, altquery: str):
#     """
#     Scrape the torrent from torrentio.

#     Parameters
#     ----------
#     query: str
#         Name of the movie or tv series.
#     altquery: str
#         Name of the movie or tv series.

#     Returns
#     -------
#     list
#         List of scraped torrents.
#     """
#     scraped_releases = []
    
#     if altquery == "(.*)":
#         altquery = query
    
#     type_ = ("show" if regex.search(r'(S[0-9]|complete|S\?[0-9])',altquery,regex.I) else "movie")
    
#     opts = DEFAULT_OPTS.split("/")[-2] if DEFAULT_OPTS.endswith("manifest.json") else ""
    
#     if type_ == "show":
#         season_number = (regex.search(r'(?<=S)([0-9]+)',altquery,regex.I).group() if regex.search(r'(?<=S)([0-9]+)',altquery,regex.I) else None)
#         episode_number = (regex.search(r'(?<=E)([0-9]+)',altquery,regex.I).group() if regex.search(r'(?<=E)([0-9]+)',altquery,regex.I) else None)
        
#         if season_number is None or int(season_number) == 0:
#             season_number = 1
        
#         if episode_number is None or int(episode_number) == 0:
#             episode_number = 1
    
#     plain_text = ""
    
#     if regex.search(r'(tt[0-9]+)', altquery, regex.I):
#         query = regex.search(r'(tt[0-9]+)', altquery, regex.I).group()
#     else:
#         plain_text = copy.deepcopy(query)
        
#         try:
#             if type_ == "show":
#                 url = "https://v3-cinemeta.strem.io/catalog/series/top/search=" + query + ".json"
#                 meta = get(url)
#             else:
#                 url = "https://v3-cinemeta.strem.io/catalog/movie/top/search=" + query + ".json"
#                 meta = get(url)

#             query = meta['metas'][0]['imdb_id']
            
#         except IMDBIdNotFoundError:
#             try:
#                 if type_ == "movie":
#                     type_ = "show"
#                     s = 1
#                     e = 1
#                     url = "https://v3-cinemeta.strem.io/catalog/series/top/search=" + query + ".json"
#                     meta = get(url)
#                 else:
#                     type_ = "movie"
#                     url = "https://v3-cinemeta.strem.io/catalog/movie/top/search=" + query + ".json"
#                     meta = get(url)
                    
#                 query = meta.json()['metas'][0]['imdb_id']
                
#             except IMDBIdNotFoundError:
#                 print('[torrentio] error: could not find IMDB ID')
#                 return scraped_releases
    
#     if type_ == "movie":
#         url = 'https://torrentio.strem.fun/' + opts + ("/" if len(opts) > 0 else "") + 'stream/movie/' + query + '.json'
#         response = get(url)
        
#         if not 'streams' in response or len(response['streams']) == 0:
#             type_ = "show"
#             s = 1
#             e = 1
            
#             if plain_text != "":
#                 try:
#                     url = "https://v3-cinemeta.strem.io/catalog/series/top/search=" + plain_text + ".json"
#                     meta = get(url)
#                     query = meta.json()['metas'][0]['imdb_id']
                    
#                 except IMDBIdNotFoundError:
#                     print('[torrentio] error: could not find IMDB ID')
#                     return scraped_releases
    
#     if type_ == "show":
#         url = 'https://torrentio.strem.fun/' + opts + ("/" if len(opts) > 0 else "") + 'stream/series/' + query + ':' + str(int(s)) + ':' + str(int(e)) + '.json'
#         response = get(url)
        
#     if not 'streams' in response:
#         try:
#             if not response is None:
#                 print('[torrentio] error: ' + str(response))
                
#         except TorrentIOError:
#             print('[torrentio] error: unknown error')
            
#         return scraped_releases
    
#     for result in response['streams']:
#         title = clean_title(result['title'].split('\n')[0].replace(' ','.'))
#         size = (float(regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= GB)',result['title']).group()) if regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= GB)',result['title']) else float(regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= MB)',result['title']).group())/1000 if regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= MB)',result['title']) else 0)
#         links = ['magnet:?xt=urn:btih:' + result['infoHash'] + '&dn=&tr=']
#         seeds = (int(regex.search(r'(?<=👤 )([0-9]+)',result['title']).group()) if regex.search(r'(?<=👤 )([1-9]+)',result['title']) else 0)
#         source = ((regex.search(r'(?<=⚙️ )(.*)(?=\n|$)',result['title']).group()) if regex.search(r'(?<=⚙️ )(.*)(?=\n|$)',result['title']) else "unknown")
#         scraped_releases.append({'title': title, 'size': size, 'links': links, 'seeds': seeds, 'source': source})

#     return scraped_releases

from functools import lru_cache
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed
import gzip
import json
import os
import re
import time
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode
import ijson
import requests
from requests import session
from alldebrid import AllDebrid

from filters import clean_title
from tmdb import MEDIA_TYPE_MOVIE, MEDIA_TYPE_TV, is_movie_or_tv_show

session = requests.Session()
DEFAULT_API_KEY = "tXQQw2JPx8iKEyeeOoJE"
TMDB_API_KEY = "cea9c08287d26a002386e865744fafc8"
BASE_URL = "https://api.themoviedb.org/3"
ad = AllDebrid(apikey=DEFAULT_API_KEY)


