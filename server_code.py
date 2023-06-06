# pylint: disable=C0103,C0301
"""
Code for the backend of the application.
"""
from functools import wraps
import os
import re
import time
from alldebrid import APIError, AllDebrid
from flask import Flask, request, jsonify
from flask_cors import CORS
from emby import get_libraries, get_user_ids, validate_emby_apikey
from exceptions import EmbyError
from matching_algorithms import jaccard_similarity

from orionoid import search_best_qualities
from uploader import (
    debrid_persistence_checks,
    extract_title_from_magnets_dn,
    process_magnet,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

CORS(app)

API_KEY = "suitloveshisapikeyswtfmomentweirdchamp"
max_retries = 3
delay_between_retries = 5  # seconds


def api_key_required(func):
    """
    Decorator function to check if the API key in the request headers is valid.

    :param f: The function to be decorated.
    :return: The decorated function, which will check the API key before executing.  # noqa: E501
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "apikey" in request.headers and request.headers["apikey"] == API_KEY:
            return func(*args, **kwargs)
        return jsonify({"error": "Missing or invalid API key."}), 401

    return decorated_function


@app.route("/upload_to_debrid", methods=["POST"])
@api_key_required
def upload_to_debrid():
    """
    Endpoint to upload a magnet link to Debrid. The magnet link should be provided in the body of the POST request.

    :return: A JSON response indicating success or failure of the upload operation.  # noqa: E501
    """
    magnet = request.get_json()["magnet"]

    if not magnet:
        print("Debug: Missing or invalid magnet parameter.")
        return jsonify({"error": "Missing or invalid magnet parameter."}), 400

    for attempt in range(max_retries):
        print(f"Debug: Attempt {attempt + 1} of {max_retries}")
        try:
            _, status_code = process_magnet(magnet)

            if status_code == 200:
                title = extract_title_from_magnets_dn(magnet)
                print(f"Debug: Title extracted - {title}")
                persistence_check = debrid_persistence_checks(title=title)

                if persistence_check["status"] == "error":
                    if (
                        attempt < max_retries - 1
                    ):  # If we haven't reached max retries yet, we sleep and then retry
                        time.sleep(delay_between_retries)
                        continue
                    return (
                        jsonify(
                            {
                                "error": "Max retries reached during process_magnet phase. DM unicorns pls."
                            }
                        ),
                        500,
                    )

                title_words = set(title.lower().split())
                best_link = None
                max_similarity = 0
                for link in persistence_check["data"]["links"]:
                    filename = os.path.splitext(link["filename"])[0].lower()
                    filename_words = set(re.split(r"\W+", filename))
                    similarity = jaccard_similarity(
                        title_words, filename_words
                    )  # noqa: E501
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_link = link
                    if max_similarity == 1:  # Early exit
                        break

                if best_link:  # If a best link is found
                    return (
                        jsonify(
                            {
                                "success": f'Magnet processed successfully. Best match: {best_link["filename"]} with Jaccard similarity: {max_similarity}'  # noqa: E501
                            }
                        ),
                        200,
                    )
                return (
                    jsonify(
                        {
                            "error": "No link found with Jaccard similarity >= 0"  # noqa: E501
                        }  # noqa: E501
                    ),
                    404,
                )

        except (ValueError, APIError) as exc:
            print(f"Debug: Exception caught - {exc}")
            if (
                attempt < max_retries - 1
            ):  # If we haven't reached max retries yet, we sleep and then retry
                time.sleep(delay_between_retries)
                continue
            # else:
            return (
                jsonify(
                    {
                        "error": "Something went wrong during the process_magnet phase. DM unicorns pls."  # noqa: E501
                    }
                ),
                500,
            )

    return (
        jsonify(
            {
                "error": "All attempts failed during the process_magnet phase. DM unicorns pls."  # noqa: E501
            }
        ),
        500,
    )


def validate_request_params(params):
    """
    Validates request parameters by checking their types. This function doesn't validate values of the parameters.

    :param params: A dictionary containing request parameters.

    :return: A tuple where the first element is a boolean indicating the validity of the parameters, and the second element
             is either an empty dictionary (if all parameters are valid), or a dictionary containing an error message (if at least
             one parameter is invalid).
    """
    valid_params = {
        "imdb_id": str,
        "qualities_sets": list,
        "season": int,
        "max_results": int,
        "sort_order": str,
        "min_seeds": int,
        "filter_uncached": bool,
        "sort_by_quality": bool,
    }

    for param, type_ in valid_params.items():
        value = params.get(param)

        if value and not isinstance(value, type_):
            return False, {
                "error": f"Invalid {param} format. Expected {type_.__name__}."
            }

    return True, {}


@app.route("/search_id", methods=["POST"])
@api_key_required
def search_id():
    """
    Endpoint to search for a movie or show by its IMDb ID. The IMDb ID and various search parameters should be provided in the body of the POST request.

    :return: A JSON response containing search results, or an error message if the search failed.
    """
    try:
        valid, response = validate_request_params(request.json)

        if not valid:
            return jsonify(response), 400

        res = search_best_qualities(
            title=request.json["imdb_id"],
            qualities_sets=request.json["qualities_sets"],
            season=request.json["season"],
            max_results=request.json["max_results"],
            sort_order=request.json["sort_order"],
            min_seeds=request.json["min_seeds"],
            filter_uncached=request.json["filter_uncached"],
            sort_by_quality=request.json["sort_by_quality"],
        )

        if not res:
            return jsonify({"error": "No results found."}), 404

        return jsonify({"status": "success", "data": res}), 200

    except ValueError as exc:
        print(f"Debug: Exception caught - {exc}")
        return (
            jsonify(
                {
                    "error": "Maybe invalid input values..? Huh, maybe check how the requests JSON is passed :)."
                }
            ),
            500,
        )
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Debug: Exception caught - {exc}")
        return (
            jsonify(
                {
                    "error": "Something went wrong during the search_best_qualities phase. DM unicorns pls."
                }
            ),
            500,
        )


@app.route("/ping", methods=["GET"])
def ping():
    """
    Endpoint to check if the server is running.

    :return: A JSON response indicating that the server is running.
    """
    return jsonify({"success": "pong"}), 200


@app.route("/emby_library_items", methods=["GET"])
@api_key_required
def emby_library_items():
    """
    Endpoint to get the items in the Emby library. The Emby API key should be provided as a query parameter.  # noqa: E501

    :return: A JSON response containing the library items, or an error message if the operation failed.  # noqa: E501
    """
    apikey = request.get_json()
    apikey = apikey.get("emby_apikey")
    print(apikey)
    if not apikey:
        return (
            jsonify({"error": "Missing or invalid emby_apikey parameter."}),
            400,
        )  # noqa: E501

    if not validate_emby_apikey(apikey):
        return jsonify({"error": "Invalid Emby API key."}), 401

    try:
        user_ids = get_user_ids(apikey)
    except EmbyError as exc:
        if str(exc) == "No users found.":
            return jsonify({"error": str(exc)}), 404
        return jsonify({"error": str(exc)}), 401

    all_items = []
    for user_id in user_ids:
        try:
            libraries = get_libraries(apikey, user_id)
        except EmbyError as exc:
            if str(exc) == "No library items found.":
                return jsonify({"error": str(exc)}), 404

        items = []
        for item in libraries["Items"]:
            items.append(
                {
                    "id": item["Id"],
                    "name": item["Name"],
                    "type": item["Type"],
                }
            )
        all_items.extend(items)

    return jsonify({"status": "success", "data": all_items}), 200


@app.route("/get_magnet_states", methods=["GET"])
@api_key_required
def get_magnet_states():
    """
    Endpoint to get the status of a magnet upload.

    :return: A JSON response containing the status of the magnet upload, or an error message if the operation failed.  # noqa: E501
    """
    alldebrid_api = AllDebrid(apikey="EA9ofGVIsr2X01Mwjr9t")

    magnet_upload = alldebrid_api.upload_magnets(
        magnets=[
            "magnet:?xt=urn:btih:EE23A73FD36A8B17F0A13814A56EF853DC0B3573&dn=%5BBitsearch.to%5D%20%D0%A0%D0%B8%D0%BA%20%D0%B8%20%D0%9C%D0%BE%D1%80%D1%82%D0%B8.Rick%20and%20Morty.S01.2160p.Ultramarinad&tr=udp%3A%2F%2Ftracker.bitsearch.to%3A1337%2Fannounce"  # noqa: E501
        ]
    )

    if magnet_upload.get("status") != "success":
        return (
            jsonify(
                {
                    "error": "Something went wrong during the upload_magnets phase. DM unicorns pls."  # noqa: E501
                }
            ),
            500,
        )

    magnet_id = magnet_upload["data"]["magnets"][0]["id"]
    resp = alldebrid_api.get_magnet_status(magnet_id=magnet_id, counter=1)

    if resp.get("status") != "success":
        return (
            jsonify(
                {
                    "error": f"Something went wrong while getting magnet status for ID {magnet_id}. DM unicorns pls."  # noqa: E501
                }
            ),
            500,
        )

    return jsonify({"status": "success", "data": resp["data"]["magnets"]}), 200


@app.route("/restart_magnet", methods=["POST"])
@api_key_required
def restart_magnet():
    """
    Endpoint to restart a magnet upload.
    The magnet ID should be provided in the body of the POST request.

    :return: A JSON response indicating success or failure of the restart operation.  # noqa: E501
    """
    alldebrid_api = AllDebrid(apikey="EA9ofGVIsr2X01Mwjr9t")
    magnet_id = request.get_json()
    magnet_id = magnet_id.get("magnet_id")

    if not magnet_id:
        return (
            jsonify({"error": "Missing or invalid magnet_id parameter."}),
            400,
        )  # noqa: E501

    try:
        resp = alldebrid_api.restart_magnet(magnet_id=magnet_id)
    except APIError:
        return (
            jsonify(
                {
                    "status": "success",
                    "data": "Magnet is processing or completed",
                }  # noqa: E501
            ),
            200,
        )

    return jsonify({"status": "success", "data": resp["data"]["message"]}), 200
