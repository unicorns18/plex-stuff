import os

import requests

debug = os.getenv('DEBUG', 0)
test = os.getenv('TEST', 0)

if debug is None and test is None:
    print("Both DEBUG and TEST environment variables need to be set or used when running this.")
    exit(1)

try:
    debug = int(debug)
except ValueError:
    print("DEBUG and TEST environment variables need to be integers.")
    exit(1)

if not 0 <= debug <= 4:
    print("DEBUG needs to be an integer between 1-4")
    exit(1)

if debug == 1:
    print("Debug level: Low verbosity")
elif debug == 2:
    print("Debug level: Medium verbosity")
elif debug == 3:
    print("Debug level: High verbosity")
elif debug == 4:
    print("Debug level: Maximum verbosity")

def check_ping_endpoint(debug):
    """
    Function to check if the server is running and print debug information.

    :param debug: Debug verbosity level.
    """
    # Call /ping endpoint
    url = "http://127.0.0.1:1337/ping"
    response = requests.get(url)

    if debug >= 3:
        print(f"Debug: Response code: {response.status_code}")
        print(f"Debug: Response body: {response.json()}")
    elif debug >= 2:
        print(f"Debug: Response code: {response.status_code}")
    elif debug >= 1:
        print(f"Debug: Response code: {response.status_code}")
    else:
        pass

    # Check if the server is running
    if response.status_code == 200 and response.json() == {'success': 'pong'}:
        print("Server is running")
    else:
        print("Server is not running or response is not as expected")


if test == "PING" or test == "1":
    check_ping_endpoint(debug)
    exit(0)
else:
    print("Test not implemented")
    exit(1)
