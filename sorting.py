import random
import time

from data_store import FIELD_OF, TYPE_OF


class Stats:
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0


def swap(a, i, j, st):
    a[i], a[j] = a[j], a[i]
    st.swaps += 1


def key_range(a, limit):
    smallest = min(p[0] for p in a)
    biggest = max(p[0] for p in a)
    if biggest - smallest > limit:
        raise ValueError("Key range is too large for this sort")
    return smallest, biggest


# =====================  COMPARISON SORTS  =====================

def bubble_sort(a, st):
    n = len(a)

    for i in range(n - 1):
        swapped = False

        for j in range(n - 1 - i):
            st.comparisons += 1

            if a[j][0] > a[j + 1][0]:
                swap(a, j, j + 1, st)
                swapped = True

        if not swapped:
            break

    return a


def selection_sort(a, st):
    for i in range(len(a) - 1):
        smallest = i
        for j in range(i + 1, len(a)):
            st.comparisons += 1
            if a[j][0] < a[smallest][0]:
                smallest = j
        if smallest != i:
            swap(a, i, smallest, st)
    return a


def insertion_sort(a, st):
    for i in range(1, len(a)):
        item = a[i]
        j = i - 1
        while j >= 0:
            st.comparisons += 1
            if a[j][0] <= item[0]:
                break
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = item
    return a


def shell_sort(a, st):
    gap = 1
    while gap < len(a) // 3:       
        gap = gap * 3 + 1
    while gap > 0:
        for i in range(gap, len(a)):
            item = a[i]
            j = i
            while j >= gap:
                st.comparisons += 1
                if a[j - gap][0] <= item[0]:
                    break
                a[j] = a[j - gap]
                st.swaps += 1
                j -= gap
            a[j] = item
        gap //= 3
    return a


def merge(left, right, st, descending=False):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        st.comparisons += 1
        if descending:
            right_first = right[j][0] > left[i][0]
        else:
            right_first = right[j][0] < left[i][0]
        if right_first:
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
        st.swaps += 1
    leftovers = left[i:] + right[j:]
    st.swaps += len(leftovers)
    return merged + leftovers


def merge_sort(a, st, descending=False):
    if len(a) <= 1:
        return a
    middle = len(a) // 2
    left = merge_sort(a[:middle], st, descending)
    right = merge_sort(a[middle:], st, descending)
    return merge(left, right, st, descending)


def hybrid_merge_sort(a, st):
    if len(a) <= 16:
        return insertion_sort(a, st)
    middle = len(a) // 2
    left = hybrid_merge_sort(a[:middle], st)
    right = hybrid_merge_sort(a[middle:], st)
    return merge(left, right, st)


def quick_sort(a, st, low=0, high=None):
    if high is None:
        high = len(a) - 1
    if low >= high:
        return a

    pivot = a[random.randint(low, high)][0]
    smaller, i, bigger = low, low, high
    while i <= bigger:
        st.comparisons += 1
        if a[i][0] < pivot:
            swap(a, smaller, i, st)
            smaller += 1
            i += 1
        else:
            st.comparisons += 1
            if a[i][0] > pivot:
                swap(a, i, bigger, st)
                bigger -= 1
            else:
                i += 1

    quick_sort(a, st, low, smaller - 1)
    quick_sort(a, st, bigger + 1, high)
    return a


# =====================  NON-COMPARISON SORTS  =====================

def counting_sort(a, st):
    if not a:
        return a
    smallest, biggest = key_range(a, 5_000_000)

    counts = [0] * (biggest - smallest + 1)
    for p in a:
        counts[p[0] - smallest] += 1
    for i in range(1, len(counts)):
        counts[i] += counts[i - 1]

    result = [None] * len(a)
    for p in reversed(a):             
        counts[p[0] - smallest] -= 1
        result[counts[p[0] - smallest]] = p
        st.swaps += 1
    return result


def radix_sort(a, st):
    if not a:
        return a
    smallest = min(p[0] for p in a)
    biggest = max(p[0] for p in a) - smallest
    place = 1
    while biggest // place > 0:
        buckets = [[] for _ in range(10)]
        for p in a:
            buckets[((p[0] - smallest) // place) % 10].append(p)
            st.swaps += 1
        a = [p for bucket in buckets for p in bucket]
        place *= 10
    return a


def bucket_sort(a, st):
    if not a:
        return a

    smallest = min(p[0] for p in a)
    biggest = max(p[0] for p in a)

    size = len(a)
    bucket_count = 100

    buckets = [[] for _ in range(bucket_count)]

    for p in a:
        index = (p[0] - smallest) * bucket_count // (biggest - smallest + 1)
        index = min(index, bucket_count - 1)

        buckets[index].append(p)

    result = []

    for bucket in buckets:
        result += insertion_sort(bucket, st)

    return result


def pigeonhole_sort(a, st):
    if not a:
        return a
    smallest, biggest = key_range(a, 1_000_000)  

    holes = [[] for _ in range(biggest - smallest + 1)]
    for p in a:
        holes[p[0] - smallest].append(p)
        st.swaps += 1
    return [p for hole in holes for p in hole]


def msd_radix_sort(a, st):
    if not a:
        return a
    smallest = min(p[0] for p in a)
    biggest = max(p[0] for p in a) - smallest
    place = 1
    while biggest // (place * 10) > 0:
        place *= 10

    def sort_group(group, place):
        if len(group) <= 1 or place == 0:
            return group
        buckets = [[] for _ in range(10)]
        for p in group:
            buckets[((p[0] - smallest) // place) % 10].append(p)
            st.swaps += 1
        result = []
        for bucket in buckets:
            result += sort_group(bucket, place // 10)
        return result

    return sort_group(a, place)


# =====================  ALGORITHM TABLE  =====================

ALGORITHMS = {
    # comparison
    "Bubble Sort":       (bubble_sort,       "O(n^2)",                       "Stable"),
    "Selection Sort":    (selection_sort,    "O(n^2)",                       "Not stable"),
    "Insertion Sort":    (insertion_sort,    "O(n^2)",                       "Stable"),
    "Shell Sort":        (shell_sort,        "O(n^1.5) approx",              "Not stable"),
    "Merge Sort":        (merge_sort,        "O(n log n)",                   "Stable"),
    "Hybrid Merge Sort": (hybrid_merge_sort, "O(n log n)",                   "Stable"),
    "Quick Sort":        (quick_sort,        "O(n log n) avg, O(n^2) worst", "Not stable"),
    # non-comparison
    "Counting Sort":     (counting_sort,     "O(n + k)",                     "Stable"),
    "Radix Sort":        (radix_sort,        "O(d(n + k))",                  "Stable"),
    "Bucket Sort":       (bucket_sort,       "O(n + k) avg, O(n^2) worst",   "Stable"),
    "Pigeonhole Sort":   (pigeonhole_sort,   "O(n + range)",                 "Stable"),
    "MSD Radix Sort":    (msd_radix_sort,    "O(d(n + k))",                  "Stable"),
}
ALGORITHM_INFO = {name: (info, stable) for name, (_, info, stable) in ALGORITHMS.items()}
QUADRATIC = {"Bubble Sort", "Selection Sort", "Insertion Sort"}   # slow on 15k rows
NUMBERS_ONLY = {"Counting Sort", "Bucket Sort", "Pigeonhole Sort"}
RADIX_SORTS = {"Radix Sort", "MSD Radix Sort"}


def supports(algo, column):
    kind = TYPE_OF[column]
    if algo in NUMBERS_ONLY:
        return kind == "int"
    if algo in RADIX_SORTS:
        return kind in ("int", "date")
    return True


def make_key(column, algo=""):
    field, kind = FIELD_OF[column], TYPE_OF[column]
    if kind == "int":
        return lambda row: row[field]
    if kind == "date" and algo in RADIX_SORTS:
        return lambda row: int("".join(c for c in row[field] if c.isdigit()) or 0)
    if kind == "date":
        return lambda row: row[field]
    return lambda row: row[field].lower()


def run_sort(algo, rows, column, descending=False):
    if not supports(algo, column):
        raise ValueError(f"{algo} cannot sort the '{column}' column")

    key = make_key(column, algo)
    pairs = [[key(row), row] for row in rows]
    stats = Stats()

    start = time.perf_counter()
    pairs = ALGORITHMS[algo][0](pairs, stats)
    ms = (time.perf_counter() - start) * 1000

    if descending:
        pairs.reverse()
    return [row for _, row in pairs], ms, stats.comparisons, stats.swaps


def multi_level_sort(rows, levels):
    stats = Stats()
    start = time.perf_counter()
    for column, descending in reversed(levels):
        key = make_key(column)
        pairs = [[key(row), row] for row in rows]
        rows = [row for _, row in merge_sort(pairs, stats, descending)]
    ms = (time.perf_counter() - start) * 1000
    return rows, ms, stats.comparisons, stats.swaps


def benchmark(rows, column, descending=False, skip_slow=False):
    results = []
    for name, (_, complexity, stable) in ALGORITHMS.items():
        entry = {"algorithm": name, "complexity": complexity, "stable": stable}
        if skip_slow and name in QUADRATIC:
            entry.update(ms=None, comparisons=None, swaps=None)
        else:
            try:
                _, ms, comparisons, swaps = run_sort(name, rows, column, descending)
                entry.update(ms=ms, comparisons=comparisons, swaps=swaps)
            except ValueError:      # this algorithm cannot sort this column
                entry.update(ms=None, comparisons=None, swaps=None)
        results.append(entry)
    return results