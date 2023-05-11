from urllib.request import urlopen
import requests

listname = "r-rated-action-films"
headers = {
  'Content-Type': 'application/json',
  'trakt-api-version': '2',
  'trakt-api-key': '3f6bad0655f06b961a185e888a633bcb3702ecdd9e68e44167106420ed62a349'
}
list_id = "r-rated-action-films"
url = f"https://api.trakt.tv/lists/{list_id}/items/movie"
response = requests.get(url, headers=headers).json()
titles = []

for item in response:
    title = item['movie']['title']
    imdb_id = item['movie']['ids']['imdb']
    print(title, imdb_id)
    titles.append(title)

# print(titles)