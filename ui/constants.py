"""Display constants for the GUI. Everything comes from the logic modules,
so there is exactly one source of truth for column names, algorithms and operators."""

from data_store import HEADERS
from filters import NUM_OPS, TEXT_OPS
from scraper import TARGET_COUNT  # progress bar and scraper always agree
from searching import SEARCH_FUNCS
from sorting import ALGORITHM_INFO

COLUMNS = HEADERS
SORT_ALGORITHMS = ALGORITHM_INFO                 # name -> (complexity, "Stable"/"Not stable")
SEARCH_ALGORITHMS = list(SEARCH_FUNCS)

TEXT_OPERATORS = list(TEXT_OPS)
NUMBER_OPERATORS = list(NUM_OPS)
ALL_OPERATORS = TEXT_OPERATORS + NUMBER_OPERATORS

BENCH_LIMIT = 5000       # rows used by the benchmark unless "Use every row" is ticked
SLOW_SORT_ROWS = 8000    # ask before running an O(n^2) sort on more rows than this
