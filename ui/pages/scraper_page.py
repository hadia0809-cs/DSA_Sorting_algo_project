"""Page 2: start / pause / resume / stop, progress and the URL scraper."""

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from data_store import clean_row
from scraper import GitHubScraper
from ui.constants import TARGET_COUNT
from ui.widgets import StatCard, field_label, make_card, page_header, scrolling
from ui.workers import Worker


class ScraperPage(QWidget):
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
            "Scraper", "Collect repositories from the GitHub Search API."))

        # Stat cards
        stats = QHBoxLayout()
        stats.setSpacing(16)
        self.stat_collected = StatCard("Collected", "0")
        self.stat_target = StatCard("Target", f"{TARGET_COUNT:,}")
        self.stat_percent = StatCard("Complete", "0%")
        for s in (self.stat_collected, self.stat_target, self.stat_percent):
            stats.addWidget(s, 1)
        lay.addLayout(stats)

        # Controls + progress
        ctrl, c_lay = make_card("Collection", "Pause and resume at any time; progress is saved to CSV.")
        status_row = QHBoxLayout()
        status_row.addWidget(field_label("Status"))
        self.status_pill = QLabel("Idle")
        self.status_pill.setObjectName("statusPill")
        status_row.addWidget(self.status_pill)
        status_row.addStretch()
        c_lay.addLayout(status_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, TARGET_COUNT)
        self.progress.setValue(0)
        self.progress.setFormat("%v / %m")
        c_lay.addWidget(self.progress)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.start_btn = QPushButton("▶   Start")
        self.start_btn.setObjectName("primary")
        self.pause_btn = QPushButton("⏸   Pause")
        self.resume_btn = QPushButton("⏯   Resume")
        self.stop_btn = QPushButton("⏹   Stop")
        self.stop_btn.setObjectName("danger")
        self.start_btn.clicked.connect(self.on_start)
        self.pause_btn.clicked.connect(self.on_pause)
        self.resume_btn.clicked.connect(self.on_resume)
        self.stop_btn.clicked.connect(self.on_stop)
        for b in (self.pause_btn, self.resume_btn, self.stop_btn):
            b.setEnabled(False)  # nothing is running yet
        for b in (self.start_btn, self.pause_btn, self.resume_btn, self.stop_btn):
            btn_row.addWidget(b)
        btn_row.addStretch()
        c_lay.addLayout(btn_row)
        lay.addWidget(ctrl)

        # URL scraping (bonus)
        url_card, u_lay = make_card(
            "Scrape from a URL ",
            "Paste a GitHub repository, topic or search URL.")
        url_row = QHBoxLayout()
        url_row.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://github.com/…")
        self.url_btn = QPushButton("Scrape URL")
        self.url_btn.setObjectName("primary")
        self.url_btn.clicked.connect(self.on_scrape_url)
        url_row.addWidget(self.url_input, 1)
        url_row.addWidget(self.url_btn)
        u_lay.addLayout(url_row)
        lay.addWidget(url_card)

        # Log
        log_card, l_lay = make_card("Activity log")
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Scraper messages will appear here…")
        self.log.setMinimumHeight(160)
        l_lay.addWidget(self.log)
        lay.addWidget(log_card)
        lay.addStretch()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scrolling(body))

        self.scraper = GitHubScraper()
        self._paused = False
        self._was_running = False
        self.timer = QTimer(self)
        self.timer.setInterval(500)            # look at the scraper twice a second
        self.timer.timeout.connect(self._tick)
        self.timer.start()

    def _is_running(self):
        t = self.scraper.thread
        return t is not None and t.is_alive()

    def on_start(self):
        self._paused = False
        self.scraper.start()
        self.log.appendPlainText("Collection started.")

    def on_pause(self):
        self._paused = True
        self.scraper.pause()

    def on_resume(self):
        self._paused = False
        self.scraper.resume()

    def on_stop(self):
        self.scraper.stop()

    def _tick(self):
        s = self.scraper
        running = self._is_running()
        count = len(s.repositories)

        self.progress.setValue(min(count, TARGET_COUNT))
        self.stat_collected.set_value(f"{count:,}")
        self.stat_percent.set_value(f"{min(100, count * 100 // TARGET_COUNT)}%")
        while not s.messages.empty():
            self.log.appendPlainText(s.messages.get())

        if running:
            self.status_pill.setText("Paused" if self._paused else "Running")
        else:
            self.status_pill.setText("Idle")
        self.start_btn.setEnabled(not running)
        self.pause_btn.setEnabled(running and not self._paused)
        self.resume_btn.setEnabled(running and self._paused)
        self.stop_btn.setEnabled(running)

        if self._was_running and not running:      # it just finished or was stopped
            self._paused = False
            self.app.set_data([clean_row(r) for r in s.repositories.values()])
        self._was_running = running

    def on_scrape_url(self):
        url = self.url_input.text().strip()
        if not url:
            return
        if self._is_running() and not self._paused:
            QMessageBox.information(self, "Scraper busy",
                                    "Pause or stop the scraper first.")
            return
        self.url_btn.setEnabled(False)
        self.worker = Worker(self.scraper.add_from_url, url)
        self.worker.done.connect(self._url_done)
        self.worker.failed.connect(self._url_failed)
        self.worker.start()

    def _url_done(self, added):
        self.url_btn.setEnabled(True)
        self.log.appendPlainText(f"URL scraped: {added} new repositories.")
        self.app.set_data([clean_row(r) for r in self.scraper.repositories.values()])

    def _url_failed(self, message):
        self.url_btn.setEnabled(True)
        QMessageBox.warning(self, "Could not scrape that URL", message)
