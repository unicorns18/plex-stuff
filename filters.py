#pylint: disable=C0114
import re

visual_qualities = {
    'Dolby Vision': 10,
    'DoVi': 10,
    'HDR10+': 10,
    'HDR10': 9,
    '4320p': 6,
    '8K': 6,
    '5K': 5,
    '2160p': 5,
    '4K': 5,
    'UHD': 5,
    'UHDTV': 5,
    '1440p': 4,
    '1080i': 4,
    '1080p': 4,
    'BDRip': 4,
    'BRRip': 4,
    'Blu-Ray': 4,
    'BluRay': 4,
    'Remux': 4,
    'HDTV': 3,
    'IMAX': 3,
    'Web-DL': 3,
    'WebDL': 3,
    'Web-Rip': 3,
    'WebRip': 3,
    '720p': 2,
    'Director\'s Cut': 2,
    'DVD': 1,
    'DVDRip': 1,
    'CAM': 1,
    'TS': 1,
    'SD': 1,
    'BDRmx': 4,
    'BDScr': 4,
    'HDTS': 3,
    'DVDMx': 1,
    'DVDScr': 1,
    'PDVD': 1,
    'PPV': 1,
    'R5': 1,
    'SCR': 1,
    'TK': 1,
    'TVRip': 3,
    'VCD': 1,
    'VHS': 1,
    'VHSRip': 1,
    'DCPRip': 3,
    'WebCap': 3,
    'Webrip': 3,
    'WP': 3
}
audio_qualities = {
    'Atmos': 9,
    'DTS:X': 9,
    'DTS-HD Master Audio': 9,
    'DTS-HD': 9,
    'Dolby Digital': 8,
    'Dolby Digital Plus': 8,
    'Dolby Atmos': 10,
    'Dolby TrueHD': 10,
    'DTS': 7,
    'FLAC': 8,
    'AAC': 6,
    'AC3': 6,
    'PCM': 8,
    '7.1': 7,
    '5.1': 5,
    '2.1': 4,
    'AVC': 3,
    'Stereo': 2,
    '2.0': 2,
    'Mono': 1,
    'HEVC': 3,
    'MP3': 1,
}

def score_title(title: str) -> int:
    """
    Calculate the score of given title.

    Parameters
    ----------
    title: str
        Title of the video.

    Returns
    -------
    int
        Score of title.
    """
    score = 0
    title_words = re.sub(r'[^a-zA-Z0-9 ]', ' ', title.lower()).split()
    for quality, points in visual_qualities.items():
        if quality.lower() in title_words:
            score += points
    for quality, points in audio_qualities.items():
        if quality.lower() in title_words:
            score += points
    return score

def clean_title(title: str) -> str:
    """
    Clean the title from unwanted characters.

    Parameters
    ----------
    title: str
        Title of the video.

    Returns
    -------
    str
        Cleaned title.
    """
    try:
        title = title.encode('ascii', 'ignore').decode('ascii')
        title = re.sub(r'(\||\/)', '', title)
        title = re.sub(r'\.{2,}', '.', title)
        if title[0] == '.':
            title = title[1:]
        return title
    except (AttributeError, TypeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid title: {title}") from exc
