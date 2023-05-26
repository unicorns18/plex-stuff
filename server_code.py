from functools import wraps
import os
import re
import time
from alldebrid import APIError
from flask import Flask, request, jsonify
from flask_cors import CORS
from matching_algorithms import jaccard_similarity

from orionoid import search_best_qualities
from uploader import debrid_persistence_checks, extract_title_from_magnets_dn, process_magnet

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB

CORS(app)

API_KEY = "suitloveshisapikeyswtfmomentweirdchamp"

def api_key_required(f):
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
    imdb_id = request.args.get('imdb_id')

    if not imdb_id or not re.match(r'tt\d{7}', imdb_id):
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
    
    return jsonify(res), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='1337', debug=True)