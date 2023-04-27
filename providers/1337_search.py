import json
from py1337x import py1337x

cookie = "PooqfRuK0BPs_5lfYjwSryxmcqeK.DLIB.ZwduzyuNE-1682412889-0-AZ7YP9Xdu3c8ZK7nbkZJL96rGN6/baJsHYxC/1TUweNWGQ1ym8BLb9KPNFU0rG3p40C8pNDyJjAGoqQCpzYdRp0uvn5Ik1FMDr4ELvPdBbPT"

torrents = py1337x(proxy='1337x.to', cookie=cookie, cache='py1337xCache', cacheTime=86400, backend='sqlite')

for i in range(5):
    search = torrents.search(query="Doctor Strange", category="Movies", sortBy="size", page=i)

with open('data.json', 'w', encoding="utf-8") as file:
    json.dump(search, file, ensure_ascii=False, indent=4)
