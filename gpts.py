import json
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode

import requests
from filters import clean_title

TOKEN = "ZZBAYPMQTXGGVHPKZJO5Y4SQJO3NA3XE7WBJLN67DOA3TLLQ3A7VMP532XSIDGKRPNQPCHNEV5HUGTD4UEU5IE6FBP4N7VV3ZZBKM6LZRUZ2WM7KKDKIYFJLV6C26JHA"
TMDB_API_KEY = "cea9c08287d26a002386e865744fafc8"
CLIENT_ID = "GVFTUUBKFCK67DC8AR9EF2QHCP8GDCME"
API_HOST = "https://api.orionoid.com"

session = requests.Session()

class OrionSearch:
    """
    Search the Orion Search Engine.

    Parameters
    ----------
    token: str
        Orion Search Engine Token.
    default_opts: list
        Default Options for Orion Search Engine.

    Attributes
    ----------
    token: str
    default_opts: list
    session: requests.Session

    Methods
    -------
    search(self, query: str, altquery: str) -> Optional[Dict]:
        Search the Orion Search Engine.

    normalize_queries(self, query: str, altquery: str) -> tuple:
        Normalize the Queries.

    determine_type(self, altquery: str) -> str:
        Determine the Type of Query.

    build_opts(self, default_opts: list) -> list:
        Build the Options for Query.

    extract_season_episode(self, altquery: str, type_: str) -> tuple:
        Extract the Season and Episode from the Query.

    add_season_episode(self, opts: list, season_number: int, episode_number: int) -> list:
        Add Season and Episode to Options.

    build_url(self, token: str, query: str, type_: str, opts: list) -> str:
        Build the URL for Query.

    response_is_successful(self, response: Dict) -> bool:
        Check the Response is Successful.

    response_has_data(self, response: Dict) -> bool:
        Check the Response has Data.

    extract_match_type_total_retrieved(self, response: Dict, query: str, type_: str) -> tuple:
        Extract the Match, Type, Total, Retrieved from the Response.

    extract_scraped_releases(self, response: Dict) -> Dict:
        Extract the Scraped Releases from the Response.
    """
    def __init__(self, token: str, default_opts=None):
        self.token = token
        self.default_opts = default_opts or [
            ["sortvalue", "best"],
            ["streamtype", "torrent"],
            ["limitcount", "100"],
            ["filename", "true"]
        ]
        self.session = requests.Session()

    def search(self, query: str, altquery: str) -> Optional[Dict]:
        """
        Search the Orion Search Engine.

        Parameters
        ----------
        query: str
            Query for Orion Search Engine.
        altquery: str
            Alternative Query for Orion Search Engine.

        Returns
        -------
        dict
            Scraped Releases.
        """
        query, altquery = self.normalize_queries(query, altquery)
        type_ = self.determine_type(altquery)
        opts = self.build_opts(self.default_opts)
        season_number, episode_number = self.extract_season_episode(altquery, type_)
        opts = self.add_season_episode(opts, season_number, episode_number)
        url = self.build_url(self.token, query, type_, opts)
        response = self.session.get(url).json()

        if not self.response_is_successful(response):
            print("Error: Did not receive a successful response from the server.")
            return None

        if not self.response_has_data(response):
            print("data not found in response")
            return None

        print("data found in response, streams found in data, continuing...")
        match, total, retrieved = self.extract_match_type_total_retrieved(response, query, type_)
        scraped_releases = self.extract_scraped_releases(response)

        return scraped_releases
    
    def normalize_queries(self, query: str, altquery: str) -> Tuple[str, str]:
        """
        Normalize the Queries.

        Parameters
        ----------
        query: str
            Query for Orion Search Engine.
        altquery: str
            Alternative Query for Orion Search Engine.

        Returns
        -------
        tuple
            Normalized Queries.
        """
        if altquery == "(.*)":
            altquery = query
        return query, altquery

    def determine_type(self, altquery: str) -> str:
        """
        Determine the Type of Query.

        Parameters
        ----------
        altquery: str
            Alternative Query for Orion Search Engine.

        Returns
        -------
        str
            Type of Query.
        """
        return "show" if re.search(r'(S[0-9]|complete|S\?[0-9])', altquery, re.I) else "movie"

    def build_opts(self, default_opts) -> str:
        """
        Build the Options for Query.

        Parameters
        ----------
        default_opts: list
            Default Options for Orion Search Engine.

        Returns
        -------
        list
            Options for Query.
        """
        return '&'.join(['='.join(opt) for opt in default_opts])

    def extract_season_episode(self, altquery: str, type_: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract the Season and Episode from the Query.

        Parameters
        ----------
        altquery: str
            Alternative Query for Orion Search Engine.
        type_: str
            Type of Query.

        Returns
        -------
        tuple
            Season and Episode.
        """
        if type_ == "show":
            season_number = re.search(r'(?<=S)([0-9]+)', altquery, re.I)
            episode_number = re.search(r'(?<=E)([0-9]+)', altquery, re.I)
            return (season_number.group() if season_number else None, episode_number.group() if episode_number else None)
        return None, None

    def add_season_episode(self, opts: str, season_number: Optional[str], episode_number: Optional[str]) -> str:
        """
        Add Season and Episode to Options.

        Parameters
        ----------
        opts: list
            Options for Query.
        season_number: int
            Season Number.
        episode_number: int
            Episode Number.

        Returns
        -------
        list
            Options for Query.
        """
        if season_number is not None and int(season_number) != 0:
            opts += '&numberseason=' + str(int(season_number))
            if episode_number is not None and int(episode_number) != 0:
                opts += '&numberepisode=' + str(int(episode_number))
        return opts

    def build_url(self, token: str, query: str, type_: str, opts: str) -> str:
        """
        Build the URL for Query.

        Parameters
        ----------
        token: str
            Orion Search Engine Token.
        query: str
            Query for Orion Search Engine.
        type_: str
            Type of Query.
        opts: list
            Options for Query.

        Returns
        -------
        str
            URL for Query.
        """
        if re.search(r'(tt[0-9]+)', query, re.I):
            idimdb = query[2:]
            query_params = urlencode({'token': token, 'mode': 'stream', 'action': 'retrieve', 'type': type_, 'idimdb': idimdb})
        else:
            query_params = urlencode({'token': token, 'mode': 'stream', 'action': 'retrieve', 'type': type_, 'query': query})
        return f'https://api.orionoid.com?{query_params}&{opts}'

    def response_is_successful(self, response: dict) -> bool:
        """
        Check the Response is Successful.

        Parameters
        ----------
        response: dict
            Response from Orion Search Engine.

        Returns
        -------
        bool
            Check the Response is Successful.
        """
        return response['result']['status'] == 'success'

    def response_has_data(self, response: dict) -> bool:
        """
        Check the Response has Data.

        Parameters
        ----------
        response: dict
            Response from Orion Search Engine.

        Returns
        -------
        bool
            Check the Response has Data.
        """
        return "data" in response and "streams" in response["data"]

    def extract_match_type_total_retrieved(self, response: dict, query: str, type_: str) -> Tuple[str, int, int]:
        """
        Extract the Match, Type, Total, Retrieved from the Response.

        Parameters
        ----------
        response: dict
            Response from Orion Search Engine.
        query: str
            Query for Orion Search Engine.
        type_: str
            Type of Query.

        Returns
        -------
        tuple
            Match, Type, Total, Retrieved.
        """
        match = "None"
        total = 0
        retrieved = 0

        if "data" in response:
            if "movie" in response["data"]:
                match = response["data"]["movie"]["meta"]["title"] + ' ' + str(response["data"]["movie"]["meta"]["year"])
            elif "show" in response["data"]:
                match = response["data"]["sh    ow"]["meta"]["title"] + ' ' + str(response["data"]["show"]["meta"]["year"])

            total = response["data"]["count"]["total"]
            retrieved = response["data"]["count"]["retrieved"]

            print(f"Match: '{query}' to {type_} '{match}' - found {total} releases (total), retrieved {retrieved}")

        return match, total, retrieved

    def extract_scraped_releases(self, response: dict) -> List[Dict]:
        """
        Extract the Scraped Releases from the Response.

        Parameters
        ----------
        response: dict
            Response from Orion Search Engine.

        Returns
        -------
        dict
            Scraped Releases.
        """
        scraped_releases = []

        for res in response["data"]["streams"]:
            title = clean_title(res['file']['name'].split('\n')[0].replace(' ', '.'))
            size = (float(res["file"]["size"]) / 1000000000 if "size" in res["file"] else 0)
            links = res["links"]
            seeds = res["stream"]["seeds"] if "stream" in res and "seeds" in res["stream"] else 0
            source = res["stream"]["source"] if "stream" in res and "source" in res["stream"] else ""
            quality = res["video"]["quality"] if "video" in res and "quality" in res["video"] else ""

            scraped_releases.append({
                "title": title,
                "size": size,
                "links": links,
                "seeds": seeds,
                "source": source,
                "quality": quality
            })

        return scraped_releases
    
    def search_best_qualities(self, title: str, qualities_sets: List[List[str]], filename_prefix: str):
        for qualities in qualities_sets:
            default_opts = [
                ["sortvalue", "best"],
                ["streamtype", "torrent"],
                ["limitcount", "100"],
                ["filename", "true"],
                ["videoquality", ','.join(qualities)],
            ]
            self.default_opts = default_opts
            result = self.search(query=title, altquery="(.*)")
            with open(f'results/{filename_prefix}_{"_".join(qualities)}_orionoid.json', 'w') as f:
                json.dump(result, f, indent=4, sort_keys=True)
            print(f"Done scraping {title} with qualities {qualities}")

    def search_best_qualities_tv_show(self, title: str, qualities_sets: List[List[str]], filename_prefix: str):
        query = title
        altquery = "(.*)"
        _, altquery = self.normalize_queries(query, altquery)
        type_ = self.determine_type(altquery)

        if type_ == "show":
            season_data = self.get_season_data(title)
            if season_data:
                total_seasons = season_data["total_seasons"]
                for season in range(1, total_seasons + 1):
                    altquery_season = f"{title} S{season:02d}"
                    for qualities in qualities_sets:
                        default_opts = [
                            ["sortvalue", "best"],
                            ["streamtype", "torrent"],
                            ["limitcount", "100"],
                            ["filename", "true"],
                            ["videoquality", ','.join(qualities)],
                        ]
                        self.default_opts = default_opts
                        result = self.search(query=title, altquery=altquery_season)
                        with open(f'{filename_prefix}_{"_".join(qualities)}_S{season:02d}_orionoid.json', 'w') as f:
                            json.dump(result, f, indent=4, sort_keys=True)
            else:
                print(f"No season data found for '{title}'")

        elif type_ == "movie":
            self.search_best_qualities(title, qualities_sets, filename_prefix)

    def get_season_data(self, title: str) -> Optional[Dict]:
        search_params = { "api_key": TMDB_API_KEY, "query": title }
        search_url = f"https://api.themoviedb.org/3/search/tv?{urlencode(search_params)}"
        response = requests.get(search_url, timeout=60)

        if response.status_code == 200:
            search_data = response.json()

            if search_data["results"]:
                tv_show = search_data["results"][0]
                tv_show_id = tv_show["id"]
                tv_show_url = f"https://api.themoviedb.org/3/tv/{tv_show_id}?api_key={TMDB_API_KEY}"
                tv_show_response = requests.get(tv_show_url, timeout=60)

                if tv_show_response.status_code == 200:
                    tv_show_data = tv_show_response.json()
                    return {"total_seasons": tv_show_data["number_of_seasons"]}
        return None
    
orion_search = OrionSearch(token=TOKEN)
res = orion_search.get_season_data("Breaking Bad")
print(res)
exit(0)

qualities_sets = [["hd1080", "hd720"], ["hd4k"]]
filename_prefix = "result"
title = "Shawshank Redemption"
orion_search = OrionSearch(token=TOKEN)
orion_search.search_best_qualities(title, qualities_sets, filename_prefix)
print("Done scraping Orionoid")