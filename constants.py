from dotenv import load_dotenv
import os

load_dotenv()

TRANSMISSION_CHECK = os.getenv("TRANSMISSION_CHECK", False)
TRANSMISSION_PORT = os.getenv("TRANSMISSION_PORT", 9091)
TRANSMISSION_HOST = os.getenv("TRANSMISSION_HOST", "localhost")
BASE_URL_ORIONOID = os.getenv("BASE_URL_ORIONOID", 'https://api.orionoid.com')
BASE_URL = os.getenv("BASE_URL", "https://api.themoviedb.org/3")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
EMBY_API_KEY = os.getenv("EMBY_API_KEY")
X_PLEX_TOKEN = os.getenv("X_PLEX_TOKEN")
DEFAULT_API_KEY = os.getenv("DEFAULT_API_KEY")
MDBLIST_API_KEY = os.getenv("MDBLIST_API_KEY")
TOKEN = os.getenv("TOKEN")
EXCLUDED_EXTENSIONS = os.getenv("EXCLUDED_EXTENSIONS", ['.rar', '.iso', '.zip', '.7z', '.gz', '.bz2', '.xz'])
# TRANSMISSION_CHECK          = False
# TRANSMISSION_PORT           = 9091
# TRANSMISSION_HOST           = "localhost"
# BASE_URL_ORIONOID           = 'https://api.orionoid.com'
# BASE_URL                    = "https://api.themoviedb.org/3"
# TMDB_API_KEY                = "cea9c08287d26a002386e865744fafc8"
# EMBY_API_KEY                = "84ef4a51a2ef47688167d87522c5ce36"
# X_PLEX_TOKEN                = "GAyx53DTk4nMLyr9Mts_"
# DEFAULT_API_KEY             = "tXQQw2JPx8iKEyeeOoJE"
# MDBLIST_API_KEY             = "uwk2jbhy7acivnyzpq44hh70y"
# TOKEN                       = "ZZBAYPMQTXGGVHPKZJO5Y4SQJO3NA3XE7WBJLN67DOA3TLLQ3A7VMP532XSIDGKRPNQPCHNEV5HUGTD4UEU5IE6FBP4N7VV3ZZBKM6LZRUZ2WM7KKDKIYFJLV6C26JHA"
# EXCLUDED_EXTENSIONS         = ['.rar', '.iso', '.zip', '.7z', '.gz', '.bz2', '.xz']