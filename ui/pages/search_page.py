"""Page 4: column search and composite AND / OR / NOT filters."""

import time

from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from filters import apply_filters
from searching import search_equal
from ui.constants import ALL_OPERATORS, COLUMNS, SEARCH_ALGORITHMS
from ui.widgets import FilterRow, combo, field_label, make_card, page_header, scrolling


class SearchPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app          # the MainWindow: gives access to go_to() and later the shared data
        self.setObjectName("page")
        body = QWidget()
        body.setObjectName("content")
        lay = QVBoxLayout(body)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(18)

        lay.addWidget(page_header(
            "Search", "Find repositories with one condition or combine several."))

        # --- quick search
        quick, q_lay = make_card(
            "Search a column", "Pick the column, the matching rule and the search algorithm.")
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        self.search_column = combo(COLUMNS)
        self.search_algo = combo(SEARCH_ALGORITHMS)
        self.search_operator = combo(ALL_OPERATORS)
        self.search_value = QLineEdit()
        self.search_value.setPlaceholderText("Search value")

        grid.addWidget(field_label("Column"), 0, 0)
        grid.addWidget(self.search_column, 0, 1)
        grid.addWidget(field_label("Algorithm"), 0, 2)
        grid.addWidget(self.search_algo, 0, 3)
        grid.addWidget(field_label("Match"), 1, 0)
        grid.addWidget(self.search_operator, 1, 1)
        grid.addWidget(field_label("Value"), 1, 2)
        grid.addWidget(self.search_value, 1, 3)
        q_lay.addLayout(grid)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("primary")
        self.search_btn.clicked.connect(self.on_search)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.on_clear)
        btns.addStretch()
        btns.addWidget(clear_btn)
        btns.addWidget(self.search_btn)
        q_lay.addLayout(btns)
        lay.addWidget(quick)

        # --- composite filters
        comp, c_lay = make_card(
            "Composite filters", "Chain conditions with AND, OR and NOT.")
        self.filter_container = QVBoxLayout()
        self.filter_container.setSpacing(8)
        c_lay.addLayout(self.filter_container)
        self.filter_rows = []
        self._add_filter()

        row = QHBoxLayout()
        row.setSpacing(10)
        add_btn = QPushButton("＋  Add condition")
        add_btn.clicked.connect(self._add_filter)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.on_reset_filters)
        self.apply_btn = QPushButton("Apply filters")
        self.apply_btn.setObjectName("primary")
        self.apply_btn.clicked.connect(self.on_apply_filters)
        row.addWidget(add_btn)
        row.addStretch()
        row.addWidget(reset_btn)
        row.addWidget(self.apply_btn)
        c_lay.addLayout(row)
        lay.addWidget(comp)
        lay.addStretch()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scrolling(body))

    def _add_filter(self):
        row = FilterRow(self._remove_filter, first=not self.filter_rows)
        self.filter_rows.append(row)
        self.filter_container.addWidget(row)

    def _remove_filter(self, row):
        if len(self.filter_rows) == 1:
            return
        self.filter_rows.remove(row)
        self.filter_container.removeWidget(row)
        row.deleteLater()
        self.filter_rows[0].logic.setEnabled(False)

    def on_search(self):
        column = self.search_column.currentText()
        algo = self.search_algo.currentText()
        op = self.search_operator.currentText()
        text = self.search_value.text().strip()
        rows = self.app.state.all_rows
        if not text:
            return
        try:
            if op in ("equals", "="):
                matches, ms, comparisons = search_equal(algo, rows, column, text)
            else:        # contains / starts with / > ... only make sense linearly
                algo = "Linear Search"
                self.search_algo.setCurrentText(algo)
                start = time.perf_counter()
                matches = apply_filters(rows, [("AND", column, op, text)])
                ms = (time.perf_counter() - start) * 1000
                comparisons = len(rows)
        except ValueError as error:
            QMessageBox.warning(self, "Cannot search", str(error))
            return
        self.app.state.filtered = matches
        self.app.show_rows(
            matches, f"{algo}: {len(matches):,} found in {ms:.2f} ms, "
                     f"{comparisons:,} comparisons")

    def on_clear(self):
        self.search_value.clear()
        self.app.clear_filters()

    def on_apply_filters(self):
        conditions = [(r.logic.currentText(), r.column.currentText(),
                       r.operator.currentText(), r.value.text())
                      for r in self.filter_rows]
        try:
            matches = apply_filters(self.app.state.all_rows, conditions)
        except ValueError as error:
            QMessageBox.warning(self, "Check your filters", str(error))
            return
        self.app.state.filtered = matches
        self.app.show_rows(matches, f"{len(matches):,} rows match the filters")

    def on_reset_filters(self):
        for r in self.filter_rows:
            r.value.clear()
        self.app.clear_filters()
