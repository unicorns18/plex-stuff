from collections import Counter


def jaccard_similarity(x, y):
    x_counter = Counter(x)
    y_counter = Counter(y)
    intersection_cardinality = sum((x_counter & y_counter).values())
    union_cardinality = sum((x_counter | y_counter).values())
    return intersection_cardinality / float(union_cardinality)
