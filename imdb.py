import redis
import requests
import requests_cache

redis_cache = redis.StrictRedis(host='localhost', port=6379, db=0)
requests_cache.install_cache('orionoid_cache', backend='redis', connection=redis_cache, expire_after=604800)

class TMDbSearcher:
    def __init__(self, api_key: str, api_base_url: str = "https://api.themoviedb.org/3", http_client=None):
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.http_client = http_client or requests
        self.imdb_api_base_url = "https://imdb-api.com"

    def search_and_get_details(self, title: str) -> dict:
        search_result = self.search(title)
        if search_result:
            movie_id = search_result['id']
            if movie_id is None:
                movie_id = self.search_alternate_api(title)
            if movie_id is not None:
                movie_details = self.get_movie_details(movie_id)
                return movie_details
        return None

    def search(self, title: str) -> dict:
        self._validate_title(title)
        url = self._build_url(title)
        response = self._fetch_data(url)

        if response is None:
            return None

        json_data = response.json()
        return self._handle_response(json_data)

    def _validate_title(self, title: str) -> None:
        if not isinstance(title, str):
            raise TypeError('Movie title must be a string')
        if not title:
            raise ValueError('No movie title provided')

    def _build_url(self, title: str) -> str:
        return f'{self.api_base_url}/search/movie?api_key={self.api_key}&query={title}'

    def _fetch_data(self, url: str) -> dict:
        try:
            response = self.http_client.get(url, timeout=60)
            response.raise_for_status()
            return response
        except self.http_client.exceptions.RequestException as err:
            print('Error:', err)
            return None

    def _handle_response(self, json_data: dict) -> dict:
        if not json_data['results']:
            print('No results found')
            return None
        else:
            return json_data['results'][0]

    def get_movie_details(self, movie_id: str) -> dict:
        url = f"{self.api_base_url}/movie/{movie_id}?api_key={self.api_key}"
        response = self._fetch_data(url)

        if response is None:
            return None

        return response.json()

    def search_alternate_api(self, title: str) -> str:
        url = f"{self.imdb_api_base_url}/en/API/SearchMovie/k_ghjyr73l/{title}"
        response = self._fetch_data(url)

        if response is None:
            return None

        json_data = response.json()
        if json_data['errorMessage']:
            print(f"IMDb API Error: {json_data['errorMessage']}")
            return None

        if json_data['results']:
            return json_data['results'][0]['id']
        else:
            return None

API_KEY = 'cea9c08287d26a002386e865744fafc8'

titles = ['North by Northwest', 'Evangelion: 3.0+1.0 Thrice Upon a Time', 'Oldboy', 'Aliens', 'Mad Max: Fury Road', 'Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train', 'Neon Genesis Evangelion: The End of Evangelion', 'The French Connection', 'Children of Men', 'RRR', 'Everything Everywhere All at Once', 'Heat', 'Kill Bill: Vol. 2', 'Riders of Justice', 'Scarface', 'Logan', 'Bacurau', 'The Killer', 'Blade Runner', 'Justice League Dark: Apokolips War', 'A Bittersweet Life', 'A Night to Remember', 'Scarface', 'Sin Nombre', 'Akira', 'Ghost in the Shell', 'Blade Runner 2049', 'Baby Driver', 'Drive', '1917', 'John Wick: Chapter 3 - Parabellum', 'Fallen Angels', 'Train to Busan', 'Pusher II', 'Speed', 'Braveheart', 'Die Hard', 'John Wick: Chapter 2', "Mortal Kombat Legends: Scorpion's Revenge", 'Assault on Precinct 13', 'Bāhubali: The Beginning', 'Headhunters', 'End of Watch', 'Sicario', 'The Revenant', 'Soorarai Pottru', 'Batman: The Long Halloween, Part Two', 'The Harder They Fall', 'Lock, Stock and Two Smoking Barrels', 'True Romance', 'Collateral', 'Léon: The Professional', 'Jackass Forever', 'A Taxi Driver', 'The Guns of Navarone', 'The Age of Shadows', 'The Last of the Mohicans', 'Ip Man', 'Old Henry', 'Prey', 'All Quiet on the Western Front', 'RoboCop', 'Ip Man 2', 'Nobody', 'The Witcher: Nightmare of the Wolf', 'El Camino: A Breaking Bad Movie', 'May God Save Us', 'Evangelion: 2.0 You Can (Not) Advance', 'In the Line of Fire', "'71", 'Crimson Tide', 'Kung Fury', 'Gladiator', "Zack Snyder's Justice League", 'The Blues Brothers', 'The Suicide Squad', 'Upgrade', 'Rurouni Kenshin Part III: The Legend Ends', 'Cowboy Bebop: The Movie', 'Layer Cake', 'Face/Off', 'Eye in the Sky', 'Total Recall', 'John Wick', 'The Last Duel', 'The Unbearable Weight of Massive Talent', 'Udta Punjab', 'Deadpool', 'Uri: The Surgical Strike', 'Pusher 3', '36th Precinct', 'Infernal Affairs II', 'Pusher', 'Tombstone', 'American Sniper', 'The Nice Guys', "Guy Ritchie's The Covenant", 'The Misfits', 'Beverly Hills Cop', 'Wrath of Man', 'The Northman', "The Wolf's Call", 'Deadpool 2', 'Game Night', 'The Night Comes for Us', 'Hotel Mumbai', 'Black Friday', 'El Infierno', 'The Admiral: Roaring Currents', 'Grosse Pointe Blank', 'The Last Samurai', 'Predator', 'Spy', 'Mosul', 'Ready or Not', 'The Gentlemen', 'Delhi Belly', 'Point Blank', 'The Connection', 'A Most Violent Year', 'The Negotiator', 'Falling Down', 'The Rock', 'Tropic Thunder', 'Patriots Day', 'Watchmen', 'Batman & Mr. Freeze: SubZero', 'Courage Under Fire', 'Mad Max', 'Memoir of a Murderer', 'Suicide Squad: Hell to Pay', 'OSS 117: Cairo, Nest of Spies', 'Bronson', 'We Were Soldiers', 'The Guest', 'Justice League Dark', 'Enemy of the State', 'Athena', 'Shershaah', 'Planet Terror', 'T-34', 'The Gangster, the Cop, the Devil', 'Avengement', 'Free to Play', 'Stewie Griffin: The Untold Story', 'Resident Evil: Damnation', 'Die Hard: With a Vengeance', 'Fury', 'Kingsman: The Secret Service', 'The Last Kingdom: Seven Kings Must Die', 'The Driver', 'The Patriot', 'Gantz:O', 'The Siege of Jadotville', 'Elite Squad', 'Pineapple Express', 'The Girl with All the Gifts', 'Allied', 'This Is the End', 'Rocketry: The Nambi Effect', 'Ferry', 'Law of Tehran', 'Danger Close: The Battle of Long Tan', 'The Art of Self-Defense', 'Bad Boys for Life', 'Dragged Across Concrete', 'The Inglorious Bastards', 'The Life Aquatic with Steve Zissou', 'The Grey', 'Enemy at the Gates', 'American Made', 'The Equalizer', 'Malik', 'Plane', 'Space Sweepers', 'The Stronghold', '28 Weeks Later', 'Unleashed', 'Boss Level', 'Major Grom: Plague Doctor', '#Alive', 'Batman: Gotham by Gaslight', 'Birds of Prey (and the Fantabulous Emancipation of One Harley Quinn)', 'Mayhem', 'Atomic Blonde', 'Avalon', 'Witching & Bitching', 'OSS 117: Lost in Rio', 'The Edge', 'Slow West', 'Turbo Kid', 'From Dusk Till Dawn', 'Ambulance', 'Copshop', 'Con Air', 'Wanted', 'Death Wish', 'Stretch', 'The Salvation', 'Boyka: Undisputed IV', 'RocknRolla', 'Overlord', 'Man on Fire', 'Blade', 'Kick-Ass', '300', 'Violent Night', 'Starship Troopers', 'Bullet Train', 'Accident Man', 'Crawl', 'Anthropoid', "Black '47", '21 Bridges', 'Admiral', 'Backdraft', "Shoot 'Em Up", 'Air Force One', 'Blade II', 'The Heat', 'Sita Ramam', 'Black and Blue', 'The Angel', 'Zombieland: Double Tap', 'Dead Snow 2: Red vs. Dead', 'We Own the Night', 'Wheelman', 'The Last Castle', 'Crank', 'The Kingdom', 'Sicario: Day of the Soldado', 'Fallen', 'Highlander', 'Those Who Wish Me Dead', 'Terminator: Dark Fate', 'Outlaw King', 'The Informer', 'The Program', 'Blackthorn', 'Forsaken', 'An Action Hero', 'Army of Thieves', 'Day Shift', 'The Punisher: Dirty Laundry', 'The Expendables 2', 'Confidence', 'The Protégé', 'AK vs AK', 'Safe House', 'The Foreigner', 'Code 8', 'Den of Thieves', 'Kingsman: The Golden Circle', 'The Great Raid', 'Jackass: The Movie', 'Filth', '13 Hours: The Secret Soldiers of Benghazi', "The Hitman's Bodyguard", 'Constantine', "Don't Breathe 2", '12 Strong', 'Aqua Teen Hunger Force Colon Movie Film for Theaters', 'Olympus Has Fallen', 'Operation Fortune: Ruse de Guerre', 'Time Trap', 'Holiday']
movie_searcher = TMDbSearcher(api_key=API_KEY, http_client=requests)
title_to_imdb_id = {}

for title in titles:
    result = movie_searcher.search_and_get_details(title)
    if result:
        imdb_id = result['imdb_id']
        if imdb_id is None:
            imdb_id = movie_searcher.search_alternate_api(title)
            print(f"Title: {title}, IMDb ID: {imdb_id}")
        title_to_imdb_id[title] = imdb_id

print(title_to_imdb_id)