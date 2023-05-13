from orionoid import search_best_qualities
from mdblist import get_movie_streams

ids = get_movie_streams()

QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
FILENAME_PREFIX = "result"
for title, imdb_id in ids.items():
    print("Searching for title: {}".format(title))
    search_best_qualities(title=imdb_id, title_type="movie",
                          qualities_sets=QUALITIES_SETS, filename_prefix=FILENAME_PREFIX)
    print("Done for title: {}".format(title))

print("All done!")
