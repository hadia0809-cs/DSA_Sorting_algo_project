"""Page 5: run every sorting algorithm and compare them."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sorting import benchmark
from ui.constants import BENCH_LIMIT, COLUMNS
from ui.widgets import combo, field_label, make_card, page_header, style_table
from ui.workers import Worker


class BenchmarkPage(QWidget):
    HEADERS = ["Algorithm", "Time Complexity", "Stable", "Time (ms)", "Comparisons", "Swaps"]

    def __init__(self, app):
        super().__init__()
        self.app = app          # the MainWindow: gives access to go_to() and later the shared data
        self.setObjectName("page")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 24)
        lay.setSpacing(18)

        lay.addWidget(page_header(
            "Benchmark", "Run every sorting algorithm on one column and compare them."))

        ctrl, c_lay = make_card()
        c_lay.setContentsMargins(20, 16, 20, 16)
        row = QHBoxLayout()
        row.setSpacing(12)
        self.column = combo(COLUMNS)
        self.scope = combo(["Full dataset", "Filtered results only"])
        self.run_btn = QPushButton("📊   Run benchmark")
        self.run_btn.setObjectName("primary")
        self.run_btn.clicked.connect(self.on_run)
        row.addWidget(field_label("Column"))
        row.addWidget(self.column, 1)
        row.addWidget(field_label("Scope"))
        row.addWidget(self.scope, 1)
        self.all_rows_box = QCheckBox("Use every row (slow)")
        row.addWidget(self.all_rows_box)
        row.addWidget(self.run_btn)
        c_lay.addLayout(row)
        lay.addWidget(ctrl)

        table_card = QFrame()
        table_card.setObjectName("card")
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(1, 1, 1, 1)
        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        style_table(self.table, 44)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t_lay.addWidget(self.table)
        lay.addWidget(table_card, 1)

        self.note = QLabel("Run a benchmark to see results here.")
        self.note.setObjectName("muted")
        lay.addWidget(self.note)

    def on_run(self):
        column = self.column.currentText()
        rows = self.app.rows_for_scope(self.scope.currentIndex() == 1)
        if not rows:
            QMessageBox.information(self, "No data", "There is nothing to benchmark.")
            return
        limited = not self.all_rows_box.isChecked() and len(rows) > BENCH_LIMIT
        sample = rows[:BENCH_LIMIT] if limited else rows
        self.run_btn.setEnabled(False)
        self.run_btn.setText("Running...")
        self.worker = Worker(benchmark, sample, column)
        self.worker.done.connect(lambda res: self._show(res, column, len(sample), limited))
        self.worker.failed.connect(self._failed)
        self.worker.start()

    def _show(self, results, column, count, limited):
        fastest = min((r["ms"] for r in results if r["ms"] is not None), default=None)
        self.table.setRowCount(len(results))
        for i, r in enumerate(results):
            na = r["ms"] is None
            cells = [r["algorithm"], r["complexity"], r["stable"],
                     "n/a" if na else f"{r['ms']:,.2f}",
                     "n/a" if na else f"{r['comparisons']:,}",
                     "n/a" if na else f"{r['swaps']:,}"]
            for j, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if j >= 3:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if r["ms"] is not None and r["ms"] == fastest:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.table.setItem(i, j, item)
        note = f"Column: {column}  ·  {count:,} rows"
        if limited:
            note += f" (first {BENCH_LIMIT:,}; tick the box to use all rows)"
        self.note.setText(note + "  ·  fastest algorithm in bold")
        self._done()

    def _failed(self, message):
        QMessageBox.warning(self, "Benchmark failed", message)
        self._done()

    def _done(self):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("📊   Run benchmark")
