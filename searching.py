import math
import time

from data_store import TYPE_OF
from sorting import Stats, make_key, merge_sort


def linear_search(keys, target, st):
    for i, k in enumerate(keys):
        st.comparisons += 1
        if k == target:
            return i
    return -1


def binary_search(keys, target, st, lo=0, hi=None):
    hi = len(keys) - 1 if hi is None else hi
    while lo <= hi:
        mid = (lo + hi) // 2
        st.comparisons += 1
        if keys[mid] == target:
            return mid
        st.comparisons += 1
        if keys[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def jump_search(keys, target, st):
    n = len(keys)
    if n == 0:
        return -1
    step = max(1, int(math.sqrt(n)))
    prev = 0
    while prev < n:
        block_end = min(prev + step, n)
        st.comparisons += 1
        if keys[block_end - 1] >= target:
            for i in range(prev, block_end):
                st.comparisons += 1
                if keys[i] == target:
                    return i
            return -1
        prev += step
    return -1


SEARCH_FUNCS = {
    "Linear Search": linear_search,
    "Binary Search": binary_search,
    "Jump Search": jump_search,
}


def search_equal(algo, rows, column_header, text):
    """Find every row whose column equals `text`.
    Returns (matching_rows, milliseconds, comparisons)."""
    kind = TYPE_OF[column_header]
    if kind == "int":
        try:
            target = int(text)
        except ValueError:
            raise ValueError("Please enter a whole number")
    else:
        target = text.strip().lower()
    if algo == "Interpolation Search" and kind != "int":
        raise ValueError("Interpolation Search needs a numeric column")

    key = make_key(column_header)
    pairs = [[key(r), r] for r in rows]
    if algo != "Linear Search":
        pairs = merge_sort(pairs, Stats())    
    keys = [p[0] for p in pairs]

    st = Stats()
    start = time.perf_counter()
    if algo == "Linear Search":
        hits = [i for i, k in enumerate(keys) if k == target]
        st.comparisons = len(keys)
    else:
        idx = SEARCH_FUNCS[algo](keys, target, st)
        hits = []
        if idx != -1:                           
            lo = hi = idx
            while lo > 0 and keys[lo - 1] == target:
                lo -= 1
            while hi < len(keys) - 1 and keys[hi + 1] == target:
                hi += 1
            hits = list(range(lo, hi + 1))
    ms = (time.perf_counter() - start) * 1000
    return [pairs[i][1] for i in hits], ms, st.comparisons
