"""Background worker so long jobs (sorting, benchmarking, URL scraping) never freeze the window."""

from PyQt5.QtCore import QThread, pyqtSignal


class Worker(QThread):
    """Runs fn(*args) in another thread.
    Connect .done to receive the return value, .failed to receive an error message.
    Keep a reference (self.worker = Worker(...)) or Qt may delete it while it runs."""

    done = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, fn, *args):
        super().__init__()
        self.fn, self.args = fn, args

    def run(self):
        try:
            self.done.emit(self.fn(*self.args))
        except Exception as error:
            self.failed.emit(str(error))
