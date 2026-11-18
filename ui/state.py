"""The one place that owns the data every page works with."""


class AppState:
    def __init__(self):
        self.all_rows = []       # everything loaded from the CSV (list of dicts)
        self.filtered = None     # None = no search/filter is active
        self.shown = []          # what the table is displaying right now
