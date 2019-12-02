def get_jaccard_similarity(first_set, second_set):
    if len(first_set) == 0 or len(second_set) == 0:
        return 0
    return len(first_set.intersection(second_set)) / len(first_set.union(second_set))


def get_common_tropes_similarity(first_set, second_set, length_synthetic_set=30):
    if len(first_set) == 0 or len(second_set) == 0:
        return 0
    return len(first_set.intersection(second_set)) / length_synthetic_set
