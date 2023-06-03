from functools import wraps
import os
import re
import time
from alldebrid import APIError, AllDebrid
from flask import Flask, request, jsonify
from flask_cors import CORS
from emby import get_library_ids
from matching_algorithms import jaccard_similarity

from orionoid import search_best_qualities
from uploader import debrid_persistence_checks, extract_title_from_magnets_dn, process_magnet

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB

CORS(app)

API_KEY = "suitloveshisapikeyswtfmomentweirdchamp"

def api_key_required(f):
    """
    Decorator function to check if the API key in the request headers is valid.

    :param f: The function to be decorated.
    :return: The decorated function, which will check the API key before executing.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'apikey' in request.headers and request.headers['apikey'] == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({'error': 'Missing or invalid API key.'}), 401
    return decorated_function

@app.route("/upload_to_debrid", methods=['POST'])
@api_key_required
def upload_to_debrid():
    """
    Endpoint to upload a magnet link to Debrid. The magnet link should be provided in the body of the POST request.

    :return: A JSON response indicating success or failure of the upload operation.
    """
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
                
                title_words = set(title.lower().split())
                best_link = None
                max_similarity = 0
                for link in persistence_check['data']['links']:
                    filename = os.path.splitext(link['filename'])[0].lower()
                    filename_words = set(re.split(r'\W+', filename))
                    similarity = jaccard_similarity(title_words, filename_words)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_link = link
                    if max_similarity == 1:  # Early exit
                        break
               
                if best_link:  # If a best link is found
                    return jsonify({'success': f'Magnet processed successfully. Best match: {best_link["filename"]} with Jaccard similarity: {max_similarity}'}), 200
                else:  
                    return jsonify({'error': 'No link found with Jaccard similarity >= 0'}), 404

        except (ValueError, APIError) as exc:
            print(f"Debug: Exception caught - {exc}")
            return jsonify({'error': 'Something went wrong during the process_magnet phase. DM unicorns pls.'}), 500

    return jsonify({'error': 'All attempts failed during the process_magnet phase. DM unicorns pls.'}), 500

@app.route("/search_id", methods=["POST"])
@api_key_required
def search_id():
    """
    Endpoint to search for a movie or show by its IMDb ID. The IMDb ID and various search parameters should be provided in the body of the POST request.

    :return: A JSON response containing search results, or an error message if the search failed.
    """
    imdb_id = request.args.get('imdb_id')

    if not imdb_id:# or not re.match(r'tt\d{7}', imdb_id):
        return jsonify({'error': 'Invalid IMDb ID format.'}), 400

    qualities_sets = request.json.get('qualities_sets')
    if not qualities_sets or not all(isinstance(i, list) and all(isinstance(s, str) for s in i) for i in qualities_sets):
        return jsonify({'error': 'Invalid qualities_sets format. Expected list of lists of strs. (Example: QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]])'}), 400
    
    season = request.json.get('season')
    if season and not isinstance(season, int):
        return jsonify({'error': 'Invalid season format. Expected int.'}), 400
    
    max_results = request.json.get('max_results')
    if max_results and not isinstance(max_results, int):
        return jsonify({'error': 'Invalid max_results format. Expected int.'}), 400
    
    sort_order = request.json.get('sort_order')
    if sort_order and not isinstance(sort_order, str) and sort_order not in ['best', 'etc']:
        return jsonify({'error': 'Invalid sort_order format. Expected str. (Potential values: best, shuffle, timeadded, timeupdated, popularity, filesize, streamseeds, streamage, videoquality, audiochannels)'}), 400
    
    min_seeds = request.json.get('min_seeds')
    if min_seeds and (not isinstance(min_seeds, int) or min_seeds < 0):
        return jsonify({'error': 'Invalid min_seeds format. Expected non-negative integer.'}), 400
    
    filter_uncached = request.json.get('filter_uncached')
    if filter_uncached and not isinstance(filter_uncached, bool):
        return jsonify({'error': 'Invalid filter_uncached format. Expected bool.'}), 400
    
    sort_by_quality = request.json.get('sort_by_quality')
    if sort_by_quality and not isinstance(sort_by_quality, bool):
        return jsonify({'error': 'Invalid sort_by_quality format. Expected bool.'}), 400

    try:
        res = search_best_qualities(
            title=imdb_id,
            qualities_sets=qualities_sets,
            season=season,
            max_results=max_results,
            sort_order=sort_order,
            min_seeds=min_seeds,
            filter_uncached=filter_uncached,
            sort_by_quality=sort_by_quality
        )
    except ValueError as exc:
        print(f"Debug: Exception caught - {exc}")
        return jsonify({'error': 'Maybe invalid input values..? Huh, maybe check how the requests JSON is passed :).'}), 500
    except Exception as exc:
        print(f"Debug: Exception caught - {exc}")
        return jsonify({'error': 'Something went wrong during the search_best_qualities phase. DM unicorns pls.'}), 500

    if not res:
        return jsonify({'error': 'No results found.'}), 404
    
    return jsonify({'status': "success", 'data': res}), 200

@app.route('/ping', methods=['GET'])
def ping():
    """
    Endpoint to check if the server is running.

    :return: A JSON response indicating that the server is running.
    """
    return jsonify({'success': 'pong'}), 200

@app.route('/emby_library_items', methods=['GET'])
@api_key_required
def emby_library_items():
    """
    Endpoint to get the items in the Emby library. The Emby API key should be provided as a query parameter.

    :return: A JSON response containing the library items, or an error message if the operation failed.
    """
    apikey = request.get_json()
    apikey = apikey.get('emby_apikey')
    if not apikey:
        return jsonify({'error': 'Missing or invalid emby_apikey parameter.'}), 400
    
    ids = get_library_ids(apikey)
    if not ids:
        return jsonify({'error': 'No library items found.'}), 404
    
    # TODO: Implement getting items in library IDs

    return jsonify({'status': 'success', 'data': ids}), 200

@app.route('/get_magnet_states', methods=['GET'])
@api_key_required
def get_magnet_states():
    """
    Endpoint to get the status of a magnet upload.

    :return: A JSON response containing the status of the magnet upload, or an error message if the operation failed.
    """
    ad = AllDebrid(apikey="EA9ofGVIsr2X01Mwjr9t")

    magnet_upload = ad.upload_magnets(magnets=["magnet:?xt=urn:btih:EE23A73FD36A8B17F0A13814A56EF853DC0B3573&dn=%5BBitsearch.to%5D%20%D0%A0%D0%B8%D0%BA%20%D0%B8%20%D0%9C%D0%BE%D1%80%D1%82%D0%B8.Rick%20and%20Morty.S01.2160p.Ultramarinad&tr=udp%3A%2F%2Ftracker.bitsearch.to%3A1337%2Fannounce"])

    if magnet_upload.get("status") != "success":
        return jsonify({'error': 'Something went wrong during the upload_magnets phase. DM unicorns pls.'}), 500

    magnet_id = magnet_upload["data"]["magnets"][0]["id"]
    resp = ad.get_magnet_status(magnet_id=magnet_id, counter=1)

    if resp.get("status") != "success":
        return jsonify({'error': f'Something went wrong while getting magnet status for ID {magnet_id}. DM unicorns pls.'}), 500

    return jsonify({'status': 'success', 'data': resp['data']['magnets']}), 200
@app.route('/restart_magnet', methods=['POST'])
@api_key_required
def restart_magnet():
    """
    Endpoint to restart a magnet upload. The magnet ID should be provided in the body of the POST request.

    :return: A JSON response indicating success or failure of the restart operation.
    """
    ad = AllDebrid(apikey="EA9ofGVIsr2X01Mwjr9t")
    magnet_id = request.get_json()
    magnet_id = magnet_id.get('magnet_id')

    if not magnet_id:
        return jsonify({'error': 'Missing or invalid magnet_id parameter.'}), 400
    
    try:
        resp = ad.restart_magnet(magnet_id=magnet_id)
    except APIError:
        return jsonify({'status': 'success', 'data': f'Magnet is processing or completed'}), 200

    return jsonify({'status': 'success', 'data': resp['data']['message']}), 200
