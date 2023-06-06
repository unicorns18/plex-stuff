"""
Module which provides custom exceptions.
"""


class MatchNotFoundError(Exception):
    """
    Custom exception.
    """


class TorrentIOError(Exception):
    """
    Custom exception.
    """


class IMDBIdNotFoundError(Exception):
    """
    Custom exception.
    """


class RequestException(Exception):
    """
    Custom exception.
    """


class EmbyError(Exception):
    """
    Custom exception.
    """


class TransmissionError(Exception):
    """
    Transmission error.
    """


class TorrentAddError(Exception):
    """
    Torrent add error.
    """


class MetadataError(Exception):
    """
    Metadata error.
    """


class ExecutionError(Exception):
    """
    Execution error.
    """
