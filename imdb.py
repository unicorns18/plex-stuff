import requests
import requests_cache

requests_cache.install_cache('imdb_cache', expire_after=43200, backend='sqlite')

def search_movie(movie_title):
    api_key = 'k_ghjyr73l'

    if not isinstance(movie_title, str):
        raise TypeError('Movie title must be a string')

    if not movie_title:
        print('Error: No movie title provided')
        return None
    
    movie_title = requests.utils.quote(movie_title)
    url = f'https://imdb-api.com/en/API/SearchMovie/{api_key}/{movie_title}'

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        json_data = response.json()
    except requests.exceptions.HTTPError as err:
        print('Error:', err)
        return None
    except requests.exceptions.ConnectionError as err:
        print('Error:', err)
        return None
    except requests.exceptions.Timeout as err:
        print('Error:', err)
        return None
    except requests.exceptions.RequestException as err:
        print('Error:', err)
        return None

    if json_data['errorMessage']:
        print('Error:', json_data['errorMessage'])
        return None
    elif not json_data['results']:
        print('Error: No results found')
        return None
    else:
        return json_data

def extract_movie_data(json_data):
    return json_data['results'][0]

def get_imdb_id(movie_title):
    json_data = search_movie(movie_title)
    if json_data is None:
        return None
    movie_data = extract_movie_data(json_data)
    tt_number = movie_data['id']
    return tt_number
    
list_of_titles = ['Inception', 'Shawshank Redemption']
for title in list_of_titles:
    tt_number = get_imdb_id(title)
    print(f'{title}: {tt_number}')