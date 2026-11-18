"""Page 3: single-column sort, metrics and multi-level sort."""

from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from data_store import HEADERS
from sorting import QUADRATIC, multi_level_sort, run_sort, supports
from ui.constants import COLUMNS, SLOW_SORT_ROWS, SORT_ALGORITHMS
from ui.widgets import SortLevelRow, StatCard, combo, field_label, make_card, page_header, scrolling
from ui.workers import Worker


class SortPage(QWidget):
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
            "Sort", "Choose a column and an algorithm, then compare the cost."))

        columns = QHBoxLayout()
        columns.setSpacing(18)

        # --- left: single column
        single, s_lay = make_card("Sort one column")
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(12)
        grid.setColumnStretch(1, 1)

        self.sort_column = combo(COLUMNS)
        self.sort_algo = combo(SORT_ALGORITHMS.keys())
        self.sort_algo.currentTextChanged.connect(self._update_algo_info)
        self.sort_order = combo(["Ascending", "Descending"])
        self.sort_scope = combo(["Full dataset", "Filtered results only"])
        self.algo_info = QLabel("")
        self.algo_info.setObjectName("muted")
        self.algo_info.setWordWrap(True)

        rows = [
            ("Column", self.sort_column),
            ("Algorithm", self.sort_algo),
            ("", self.algo_info),
            ("Order", self.sort_order),
            ("Scope", self.sort_scope),
        ]
        for r, (name, widget) in enumerate(rows):
            grid.addWidget(field_label(name), r, 0)
            grid.addWidget(widget, r, 1)
        s_lay.addLayout(grid)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.sort_btn = QPushButton("Sort")
        self.sort_btn.setObjectName("primary")
        self.sort_btn.clicked.connect(self.on_sort)
        btns.addWidget(self.sort_btn)
        self.bench_btn = QPushButton("📊  Benchmark this column")
        self.bench_btn.clicked.connect(self.on_bench)
        btns.addWidget(self.bench_btn)
        btns.addStretch()
        s_lay.addLayout(btns)
        columns.addWidget(single, 3)

        # --- right: metrics
        metrics = QVBoxLayout()
        metrics.setSpacing(12)
        self.metric_time = StatCard("Time (ms)")
        self.metric_comparisons = StatCard("Comparisons")
        self.metric_swaps = StatCard("Swaps")
        for m in (self.metric_time, self.metric_comparisons, self.metric_swaps):
            metrics.addWidget(m)
        metrics.addStretch()
        columns.addLayout(metrics, 2)
        lay.addLayout(columns)

        # --- multi-level sort
        multi, m_lay = make_card(
            "Multi-level sort", "Sort by several columns; later levels break ties.")
        self.level_container = QVBoxLayout()
        self.level_container.setSpacing(8)
        m_lay.addLayout(self.level_container)
        self.level_rows = []
        self._add_level()

        row = QHBoxLayout()
        row.setSpacing(10)
        add_btn = QPushButton("＋  Add level")
        add_btn.clicked.connect(self._add_level)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.on_reset_multi)
        self.multi_btn = QPushButton("Apply multi-sort")
        self.multi_btn.setObjectName("primary")
        self.multi_btn.clicked.connect(self.on_multi_sort)
        row.addWidget(add_btn)
        row.addStretch()
        row.addWidget(reset_btn)
        row.addWidget(self.multi_btn)
        m_lay.addLayout(row)
        lay.addWidget(multi)
        lay.addStretch()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scrolling(body))
        self._update_algo_info()

    def on_bench(self):
        self.app.benchmark_page.column.setCurrentText(self.sort_column.currentText())
        self.app.go_to(4)
        self.app.benchmark_page.on_run()

    def _update_algo_info(self, *_):
        complexity, stable = SORT_ALGORITHMS[self.sort_algo.currentText()]
        self.algo_info.setText(f"Time complexity: {complexity}   ·   {stable}")

    def _add_level(self):
        row = SortLevelRow(self._remove_level, len(self.level_rows))
        self.level_rows.append(row)
        self.level_container.addWidget(row)

    def _remove_level(self, row):
        if len(self.level_rows) == 1:
            return
        self.level_rows.remove(row)
        self.level_container.removeWidget(row)
        row.deleteLater()
        for i, r in enumerate(self.level_rows):
            r.tag.setText("Sort by" if i == 0 else "Then by")

    def on_sort(self):
        algo = self.sort_algo.currentText()
        column = self.sort_column.currentText()
        descending = self.sort_order.currentText() == "Descending"
        filtered_only = self.sort_scope.currentIndex() == 1
        rows = self.app.rows_for_scope(filtered_only)

        if not rows:
            QMessageBox.information(self, "No data", "There is nothing to sort yet.")
            return
        if not supports(algo, column):
            QMessageBox.warning(self, "Not possible",
                                f"{algo} only works on number/date columns.")
            return
        if algo in QUADRATIC and len(rows) > SLOW_SORT_ROWS:
            answer = QMessageBox.question(
                self, "This may be slow",
                f"{algo} is O(n^2) and you are sorting {len(rows):,} rows.\n"
                "It can take a while. Continue?")
            if answer != QMessageBox.Yes:
                return
        self._start_worker(run_sort, (algo, rows, column, descending), filtered_only)

    def on_multi_sort(self):
        levels = [(r.column.currentText(), r.order.currentText() == "Descending")
                  for r in self.level_rows]
        filtered_only = self.sort_scope.currentIndex() == 1
        rows = self.app.rows_for_scope(filtered_only)
        if rows:
            self._start_worker(multi_level_sort, (rows, levels), filtered_only)

    def on_reset_multi(self):
        while len(self.level_rows) > 1:
            self._remove_level(self.level_rows[-1])

    def _start_worker(self, fn, args, filtered_only):
        self.sort_btn.setEnabled(False)
        self.multi_btn.setEnabled(False)
        self.sort_btn.setText("Sorting...")
        self.worker = Worker(fn, *args)      # keep a reference or Qt deletes it
        self.worker.done.connect(lambda res: self._sort_done(res, filtered_only))
        self.worker.failed.connect(self._sort_failed)
        self.worker.start()

    def _sort_done(self, result, filtered_only):
        rows, ms, comparisons, swaps = result
        self.metric_time.set_value(f"{ms:,.2f}")
        self.metric_comparisons.set_value(f"{comparisons:,}")
        self.metric_swaps.set_value(f"{swaps:,}")
        self.app.apply_sorted(rows, filtered_only, f"sorted in {ms:,.2f} ms")
        self._sort_finished()

    def _sort_failed(self, message):
        QMessageBox.warning(self, "Sort failed", message)
        self._sort_finished()

    def _sort_finished(self):
        self.sort_btn.setEnabled(True)
        self.multi_btn.setEnabled(True)
        self.sort_btn.setText("Sort")

    def sort_by_header(self, index):
        """Called when the user clicks a column header in the table."""
        header = HEADERS[index]
        if self.sort_column.currentText() == header:      # same column: flip order
            flipped = "Descending" if self.sort_order.currentText() == "Ascending" else "Ascending"
            self.sort_order.setCurrentText(flipped)
        else:
            self.sort_column.setCurrentText(header)
            self.sort_order.setCurrentText("Ascending")
        self.on_sort()
