# pylint: disable=C0114,C0116,C0301
import time
import requests

session = requests.Session()

DEFAULT_API_KEY = "tXQQw2JPx8iKEyeeOoJE"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
INSTANT_AVAILABILITY_URL = "https://api.alldebrid.com/v4/magnet/instant"

def check_instant_availability(magnet_uri):
    assert magnet_uri, "Magnet URI (or hash) is required. Please provide a magnet URI or hash."

    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
    }

    if magnet_uri:
        params = {
            "apikey": DEFAULT_API_KEY,
            "magnets[]": magnet_uri,
            "agent": "python",
        }
        response = session.get(INSTANT_AVAILABILITY_URL,
                               headers=headers, params=params)
    else:
        data = {
            "apikey": DEFAULT_API_KEY,
            "agent": "python",
        }
        response = session.post(INSTANT_AVAILABILITY_URL,
                                headers=headers, data=data)

    if response.status_code == 200:
        response_json = response.json()
        return response_json
    else:
        raise ValueError(
            f"Request failed with error code {response.status_code}")
def upload_magnet(magnet_uri):
    url = "https://api.alldebrid.com/v4/magnet/upload"

    headers = {
        "User-Agent": "myAppName",
    }

    if magnet_uri:
        params = {
            "apikey": "tXQQw2JPx8iKEyeeOoJE",
            "magnets[]": magnet_uri,
            "agent": "myAppName",
        }
        response = session.get(url, headers=headers, params=params)
    else:
        data = {
            "apikey": "tXQQw2JPx8iKEyeeOoJE",
            "agent": "myAppName",
        }
        response = session.post(url, headers=headers, data=data)

    if response.status_code == 200:
        response_json = response.json()
        return response_json
    else:
        raise ValueError(F"Request failed with error code {response.status_code}")
def get_magnet_status(apikey, magnet_id, status=None, counter=None):
    base_url = 'https://api.alldebrid.com/v4/magnet/status'
    agent = 'myAppName'
    headers = {'User-Agent': agent}
    params = {'apikey': apikey, 'id': magnet_id, 'agent': agent}

    if status:
        params['status'] = status
    if session:
        params['session'] = session
    if counter:
        params['counter'] = counter

    response = session.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
def unlock_link(link, password=None):
    apikey = "tXQQw2JPx8iKEyeeOoJE"
    agent = "myAppName"
    url = f"https://api.alldebrid.com/v4/link/unlock?agent={agent}&apikey={apikey}&link={link}"
    if password:
        url += f"&password={password}"
    response = session.get(url)
    data = response.json()
    if "error" in data:
        raise ValueError(data["error"])
    elif "delayed" in data:
        delay_id = data["delayed"]
        delay_url = f"https://api.alldebrid.com/v4/link/waiting?agent={agent}&apikey={apikey}&id={delay_id}"
        delay_response = session.get(delay_url)
        delay_data = delay_response.json()
        if "error" in delay_data:
            raise ValueError(delay_data["error"])
        elif "link" in delay_data:
            data = delay_data
    # print(data)
    return data
def save_links(links):
    """
    Saves the given links to the Alldebrid user account.

    Args:
        links (list): A list of links to be saved.

    Returns:
        dict: A dictionary containing the response data from the API.
    """
    apikey = "tXQQw2JPx8iKEyeeOoJE"
    agent = "myAppName"
    url = f"https://api.alldebrid.com/v4/user/links/save?apikey={apikey}&agent={agent}"
    data = {"links": links}
    response = session.get(url, params=data)
    return response.json()
def main(apikey="tXQQw2JPx8iKEyeeOoJE", magnet="b23d0ba3f725f60e7953234f7357f10235ae4272"):
    rate_limit = 1/12
    uploaded_magnet = upload_magnet(magnet_uri=magnet)
    magnet_id = uploaded_magnet["data"]["magnets"][0]["id"]
    magnet_status = get_magnet_status(apikey=apikey, magnet_id=magnet_id)
    while magnet_status["data"]["magnets"]["status"] != "Ready":
        magnet_status = get_magnet_status(apikey=apikey, magnet_id=magnet_id)
        time.sleep(rate_limit)
    torrent_files = magnet_status["data"]["magnets"]["links"]
    torrent_links = []
    for torrent_file in torrent_files:
        torrent_links.append(torrent_file["link"])

    if len(torrent_links) > 0:
        saved_links = []

        for link in torrent_links:
            unlock_link(link=link)
            time.sleep(rate_limit)
            saved_links.append(link)

        links_saved = save_links(links=saved_links)

        return links_saved["status"] == "success"
    else:
        return False

if __name__ == "__main__":
    main()
