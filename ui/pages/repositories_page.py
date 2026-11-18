"""Page 1: the repositories table with a quick search bar."""

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from data_store import FIELD_OF, HEADERS
from ui.constants import COLUMNS
from ui.table_model import RepoTableModel
from ui.widgets import combo, make_card, page_header, style_table


class RepositoriesPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app          # the MainWindow
        self.setObjectName("page")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 24)
        lay.setSpacing(18)

        lay.addWidget(page_header(
            "Repositories", "Browse everything you have collected."))

        # Toolbar
        bar, bar_lay = make_card()
        bar_lay.setContentsMargins(16, 12, 16, 12)
        row = QHBoxLayout()
        row.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Search repositories…")
        self.search_column = combo(["All columns"] + COLUMNS)
        self.search_column.setMinimumWidth(150)
        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("primary")
        self.search_btn.clicked.connect(self.on_search)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.on_clear)

        filters_btn = QPushButton("Filters")
        filters_btn.clicked.connect(lambda: self.app.go_to(3))
        sort_btn = QPushButton("Sort")
        sort_btn.clicked.connect(lambda: self.app.go_to(2))

        row.addWidget(self.search_box, 1)
        row.addWidget(self.search_column)
        row.addWidget(self.search_btn)
        row.addWidget(self.clear_btn)
        row.addSpacing(12)
        row.addWidget(filters_btn)
        row.addWidget(sort_btn)
        bar_lay.addLayout(row)
        lay.addWidget(bar)

        # Table
        table_card = QFrame()
        table_card.setObjectName("card")
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(1, 1, 1, 1)
        self.model = RepoTableModel()          # empty for now
        self.table = QTableView()
        self.table.setModel(self.model)
        style_table(self.table)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(lambda i: self.app.sort_page.sort_by_header(i))  # click a header to sort
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        for i, w in enumerate([90, 170, 250, 340, 120, 90, 90, 120, 130, 130, 300]):
            self.table.setColumnWidth(i, w)
        t_lay.addWidget(self.table)
        lay.addWidget(table_card, 1)

        # Footer
        self.footer = QLabel("Showing 0 of 0 repositories  ·  Scope: full dataset")
        self.footer.setObjectName("muted")
        lay.addWidget(self.footer)

    def on_search(self):
        text = self.search_box.text().strip().lower()
        if not text:
            self.on_clear()
            return
        chosen = self.search_column.currentText()
        headers = HEADERS if chosen == "All columns" else [chosen]
        fields = [FIELD_OF[h] for h in headers]
        matches = [r for r in self.app.state.all_rows
                   if any(text in str(r[f]).lower() for f in fields)]
        self.app.state.filtered = matches
        self.app.show_rows(matches, f"{len(matches):,} match(es) for '{text}'")

    def on_clear(self):
        self.search_box.clear()
        self.app.clear_filters()
