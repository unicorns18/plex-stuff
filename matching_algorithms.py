"""
This module contains the implementation of the Jaccard similarity coefficient.
"""
from collections import Counter
from typing import List


def jaccard_similarity(
    list_one: List[str], list_two: List[str]
) -> float:
    """
    Jaccard similarity coefficient is a statistic used for,
    comparing the similarity and diversity of sample sets.

    :param list_one: list of strings
    :param list_two: list of strings
    :return: float
    """
    counter_one = Counter(list_one)
    counter_two = Counter(list_two)
    intersection_cardinality = sum((counter_one & counter_two).values())
    union_cardinality = sum((counter_one | counter_two).values())
    return intersection_cardinality / float(union_cardinality)
