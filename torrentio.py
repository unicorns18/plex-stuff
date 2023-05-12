#pylint: disable=C0114,C0301
import json
import copy
import time
from alldebrid import AllDebrid
import regex
import requests
from exceptions import IMDBIdNotFoundError, TorrentIOError
from filters import clean_title
from orionoid import get_cached_instants, save_filtered_results

DEFAULT_OPTS = "https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/manifest.json"
#LAST_CALL_TIME = 0
session = requests.Session()

def get(url: str) -> None:
    """
    Sends a GET request to URL.

    Parameters
    ----------
    url: str
        URL for GET request.

    Returns
    -------
    None
    """
    try:
        response = session.get(url,timeout=60)
        response = json.loads(response.content)
        return response
    except Exception: # pylint: disable=W0703
        return None

def scrape(query: str, altquery: str):
    """
    Scrape the torrent from torrentio.

    Parameters
    ----------
    query: str
        Name of the movie or tv series.
    altquery: str
        Name of the movie or tv series.

    Returns
    -------
    list
        List of scraped torrents.
    """
    scraped_releases = []
    
    if altquery == "(.*)":
        altquery = query
    
    type_ = ("show" if regex.search(r'(S[0-9]|complete|S\?[0-9])',altquery,regex.I) else "movie")
    
    opts = DEFAULT_OPTS.split("/")[-2] if DEFAULT_OPTS.endswith("manifest.json") else ""
    
    if type_ == "show":
        season_number = (regex.search(r'(?<=S)([0-9]+)',altquery,regex.I).group() if regex.search(r'(?<=S)([0-9]+)',altquery,regex.I) else None)
        episode_number = (regex.search(r'(?<=E)([0-9]+)',altquery,regex.I).group() if regex.search(r'(?<=E)([0-9]+)',altquery,regex.I) else None)
        
        if season_number is None or int(season_number) == 0:
            season_number = 1
        
        if episode_number is None or int(episode_number) == 0:
            episode_number = 1
    
    plain_text = ""
    
    if regex.search(r'(tt[0-9]+)', altquery, regex.I):
        query = regex.search(r'(tt[0-9]+)', altquery, regex.I).group()
    else:
        plain_text = copy.deepcopy(query)
        
        try:
            if type_ == "show":
                url = "https://v3-cinemeta.strem.io/catalog/series/top/search=" + query + ".json"
                meta = get(url)
            else:
                url = "https://v3-cinemeta.strem.io/catalog/movie/top/search=" + query + ".json"
                meta = get(url)
                
            query = meta['metas'][0]['imdb_id']
            
        except IMDBIdNotFoundError:
            try:
                if type_ == "movie":
                    type_ = "show"
                    s = 1
                    e = 1
                    url = "https://v3-cinemeta.strem.io/catalog/series/top/search=" + query + ".json"
                    meta = get(url)
                else:
                    type_ = "movie"
                    url = "https://v3-cinemeta.strem.io/catalog/movie/top/search=" + query + ".json"
                    meta = get(url)
                    
                query = meta.json()['metas'][0]['imdb_id']
                
            except IMDBIdNotFoundError:
                print('[torrentio] error: could not find IMDB ID')
                return scraped_releases
    
    if type_ == "movie":
        url = 'https://torrentio.strem.fun/' + opts + ("/" if len(opts) > 0 else "") + 'stream/movie/' + query + '.json'
        response = get(url)
        
        if not 'streams' in response or len(response['streams']) == 0:
            type_ = "show"
            s = 1
            e = 1
            
            if plain_text != "":
                try:
                    url = "https://v3-cinemeta.strem.io/catalog/series/top/search=" + plain_text + ".json"
                    meta = get(url)
                    query = meta.json()['metas'][0]['imdb_id']
                    
                except IMDBIdNotFoundError:
                    print('[torrentio] error: could not find IMDB ID')
                    return scraped_releases
    
    if type_ == "show":
        url = 'https://torrentio.strem.fun/' + opts + ("/" if len(opts) > 0 else "") + 'stream/series/' + query + ':' + str(int(s)) + ':' + str(int(e)) + '.json'
        response = get(url)
        
    if not 'streams' in response:
        try:
            if not response is None:
                print('[torrentio] error: ' + str(response))
                
        except TorrentIOError:
            print('[torrentio] error: unknown error')
            
        return scraped_releases
    
    for result in response['streams']:
        title = clean_title(result['title'].split('\n')[0].replace(' ','.'))
        size = (float(regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= GB)',result['title']).group()) if regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= GB)',result['title']) else float(regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= MB)',result['title']).group())/1000 if regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= MB)',result['title']) else 0)
        links = ['magnet:?xt=urn:btih:' + result['infoHash'] + '&dn=&tr=']
        seeds = (int(regex.search(r'(?<=👤 )([0-9]+)',result['title']).group()) if regex.search(r'(?<=👤 )([1-9]+)',result['title']) else 0)
        source = ((regex.search(r'(?<=⚙️ )(.*)(?=\n|$)',result['title']).group()) if regex.search(r'(?<=⚙️ )(.*)(?=\n|$)',result['title']) else "unknown")
        scraped_releases.append({'title': title, 'size': size, 'links': links, 'seeds': seeds, 'source': source})

    return scraped_releases

DEFAULT_API_KEY = "tXQQw2JPx8iKEyeeOoJE"
ad = AllDebrid(apikey=DEFAULT_API_KEY)

start_time = time.perf_counter()
res = scrape("Incredibles 2", "(.*)")
filtered_results = [item for item in res if item.get("seeds") is not None]
magnets = (item['links'][0] for item in filtered_results)
cached_instants = get_cached_instants(ad, magnets)
for item, instant in zip(filtered_results, cached_instants):
    item["cached"] = instant if instant else False
results_to_save = [item for item in filtered_results if item.get("cached") is not None]
post_processed_filename = "torrentio_parsed.json"
save_filtered_results(results_to_save, post_processed_filename)
end_time = time.perf_counter()
print(f"Finished in {end_time - start_time} seconds")
# with open('raw_results.json', 'w', encoding='utf-8') as file:
#     json.dump(res, file, ensure_ascii=False, indent=4)