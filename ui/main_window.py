"""The main window: sidebar navigation + the five pages."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from data_store import load_csv
from ui.pages.benchmark_page import BenchmarkPage
from ui.pages.repositories_page import RepositoriesPage
from ui.pages.scraper_page import ScraperPage
from ui.pages.search_page import SearchPage
from ui.pages.sort_page import SortPage
from ui.state import AppState


class MainWindow(QMainWindow):
    NAV = [
        ("📚   Repositories", 0),
        ("🌐   Scraper", 1),
        ("⇅   Sort", 2),
        ("🔍   Search", 3),
        ("📊   Benchmark", 4),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bloom | GitHub Repository Explorer")
        self.resize(1360, 820)
        self.setMinimumSize(1080, 640)

        root = QWidget()
        self.setCentralWidget(root)
        row = QHBoxLayout(root)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self.state = AppState()

        # Pages
        self.pages = QStackedWidget()
        self.repositories_page = RepositoriesPage(self)
        self.scraper_page = ScraperPage(self)
        self.sort_page = SortPage(self)
        self.search_page = SearchPage(self)
        self.benchmark_page = BenchmarkPage(self)
        for p in (self.repositories_page, self.scraper_page, self.sort_page,
                  self.search_page, self.benchmark_page):
            self.pages.addWidget(p)

        row.addWidget(self._build_sidebar())
        row.addWidget(self.pages, 1)
        self.go_to(0)
        self.set_data(load_csv())          # show whatever is in repositories.csv

    def _build_sidebar(self):
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(240)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(18, 26, 18, 20)
        lay.setSpacing(6)

        brand = QLabel("🌸 Bloom")
        brand.setObjectName("brand")
        sub = QLabel("GitHub Repository Explorer")
        sub.setObjectName("brandSub")
        lay.addWidget(brand)
        lay.addWidget(sub)
        lay.addSpacing(24)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = []
        for text, index in self.NAV:
            btn = QPushButton(text)
            btn.setObjectName("nav")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _checked, i=index: self.go_to(i))
            self.nav_group.addButton(btn)
            self.nav_buttons.append(btn)
            lay.addWidget(btn)

        lay.addStretch()
        self.dataset_label = QLabel("0 repositories loaded")
        self.dataset_label.setObjectName("sideFooter")
        lay.addWidget(self.dataset_label)
        return side


    def set_data(self, rows):
        """Replace the whole dataset (after loading the CSV or scraping)."""
        self.state.all_rows = rows
        self.state.filtered = None
        self.show_rows(rows)

    def show_rows(self, rows, message=""):
        """The ONLY method that changes what the table shows."""
        self.state.shown = rows
        page = self.repositories_page
        page.model.set_rows(rows)
        total = len(self.state.all_rows)
        scope = "filtered" if self.state.filtered is not None else "full dataset"
        text = f"Showing {len(rows):,} of {total:,} repositories  ·  Scope: {scope}"
        page.footer.setText(text + (f"  ·  {message}" if message else ""))
        self.dataset_label.setText(f"{total:,} repositories loaded")

    def rows_for_scope(self, filtered_only):
        if filtered_only and self.state.filtered is not None:
            return self.state.filtered
        return self.state.all_rows

    def apply_sorted(self, rows, filtered_only, message=""):
        if filtered_only and self.state.filtered is not None:
            self.state.filtered = rows
        else:
            self.state.all_rows = rows
            self.state.filtered = None
        self.show_rows(rows, message)

    def clear_filters(self):
        self.state.filtered = None
        self.show_rows(self.state.all_rows)

    def closeEvent(self, event):
        self.scraper_page.scraper.close()
        super().closeEvent(event)

    def go_to(self, index):
        self.pages.setCurrentIndex(index)
        self.nav_buttons[index].setChecked(True)
