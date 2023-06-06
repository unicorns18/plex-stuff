"""
API keys and constant values.
"""
import os
from dotenv import load_dotenv


load_dotenv()

TRANSMISSION_CHECK = os.getenv("TRANSMISSION_CHECK", "False") == "True"
TRANSMISSION_PORT = int(os.getenv("TRANSMISSION_PORT", "9091"))
TRANSMISSION_HOST = os.getenv("TRANSMISSION_HOST", "localhost")
BASE_URL_ORIONOID = os.getenv("BASE_URL_ORIONOID", "https://api.orionoid.com")
BASE_URL = os.getenv("BASE_URL", "https://api.themoviedb.org/3")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
EMBY_API_KEY = os.getenv("EMBY_API_KEY")
X_PLEX_TOKEN = os.getenv("X_PLEX_TOKEN")
# DEFAULT_API_KEY = os.getenv("DEFAULT_API_KEY")
MDBLIST_API_KEY = os.getenv("MDBLIST_API_KEY")
TOKEN = os.getenv("TOKEN")
# EXCLUDED_EXTENSIONS = os.getenv(
#     "EXCLUDED_EXTENSIONS",
#     [".rar", ".iso", ".zip", ".7z", ".gz", ".bz2", ".xz"]
# )
EXCLUDED_EXTENSIONS = os.getenv(
    "EXCLUDED_EXTENSIONS", ".rar,.iso,.zip,.7z,.gz,.bz2,.xz"
).split(
    ","
)  # noqa: E501
EXCLUDED_EXTENSIONS = [x.strip() for x in EXCLUDED_EXTENSIONS]
EXCLUDED_EXTENSIONS = [x for x in EXCLUDED_EXTENSIONS if x]
EXCLUDED_EXTENSIONS = tuple(EXCLUDED_EXTENSIONS)
EXCLUDED_EXTENSIONS = EXCLUDED_EXTENSIONS or (
    ".rar",
    ".iso",
    ".zip",
    ".7z",
    ".gz",
    ".bz2",
    ".xz",
)  # noqa: E501
DEFAULT_API_KEY = "tXQQw2JPx8iKEyeeOoJE"
