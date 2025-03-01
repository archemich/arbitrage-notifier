def _combine_lists(i, original: list, ret: list):
    if i >= len(original):
        return ret
    for el in original[i+1:]:
        ret.append((original[i],el))
    _combine_lists(i+1, original[i:], ret)

def combine_lists(original: list):
    ret = []
    _combine_lists(0, original, ret)
    return ret