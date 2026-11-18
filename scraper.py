import csv
import os
import queue  # NEW
import threading
import time

import requests

from url_tools import parse_github_url  

# ---------------- SETTINGS ----------------

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(PROJECT_FOLDER, "repositories.csv")

TARGET_COUNT = 15000                           
CHECKPOINT_EVERY = 100

TOKEN = os.environ.get("GITHUB_TOKEN")

FIELDS = [
    "id",
    "name",
    "full_name",
    "description",
    "language",
    "stars",
    "forks",
    "open_issues",
    "created_at",
    "updated_at",
    "html_url",
]

LANGUAGES = [
    "python", "javascript", "java", "c++", "c#", "typescript", "go", "rust",
    "php", "ruby", "kotlin", "swift", "c", "dart", "scala",
]
STAR_BANDS = [
    "stars:>20000", "stars:10000..20000", "stars:5000..9999",
    "stars:2000..4999", "stars:1000..1999", "stars:500..999",
]
QUERIES = [f"language:{lang} {band}" for lang in LANGUAGES for band in STAR_BANDS]


class GitHubScraper:

    def __init__(self):
        self.repositories = {}
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.stop_event = threading.Event()
        self.is_running = False

        self.thread = None                     
        self.messages = queue.Queue()        

        self.session = requests.Session()
        self._load_existing_data()

    # ---------------- LOGGING ----------------

    def _log(self, text):
        print(text)
        self.messages.put(str(text).strip())

    # ---------------- LOAD EXISTING DATA ----------------

    def _load_existing_data(self):
        if not os.path.exists(OUTPUT_FILE):
            return

        try:
            with open(
                OUTPUT_FILE, "r", newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)

                for row in reader:
                    repo_id = row.get("id")

                    if repo_id:
                        self.repositories[str(repo_id)] = row

            print("Existing repositories loaded:", len(self.repositories))

        except (OSError, csv.Error) as error:
            print("Could not load existing CSV:", error)

    # ---------------- SAVE DATA ----------------

    def _save_data(self):
        temporary_file = OUTPUT_FILE + ".tmp"

        try:
            with open(
                temporary_file, "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(list(self.repositories.values()))

            os.replace(temporary_file, OUTPUT_FILE)

            self._log(f"Checkpoint saved: {len(self.repositories)}")   

        except OSError as error:
            self._log(f"Could not save CSV: {error}")             

    # ---------------- CONTROLS ----------------

    def start(self):
        """Start collection in a background thread."""
        if self.is_running:
            self._log("Collection is already running.")
            return

        self.stop_event.clear()
        self.pause_event.set()

        self.thread = threading.Thread(     
            target=self.collect,
            daemon=True
        )
        self.thread.start()

    def pause(self):
        self.pause_event.clear()
        self._log("Pause requested.")

    def resume(self):
        self.pause_event.set()
        self._log("Resume requested.")

    def stop(self):
        self.stop_event.set()
        self.pause_event.set()
        self._log("Stop requested.")

    def _wait_if_paused(self):
        while not self.pause_event.is_set():
            if self.stop_event.is_set():
                return False
            time.sleep(0.2)

        return not self.stop_event.is_set()

    # ---------------- RATE LIMIT HANDLING ----------------

    def _wait_for_rate_limit(self, response):
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            wait_seconds = int(retry_after) + 2

        elif remaining == "0" and reset:
            wait_seconds = max(
                1, int(reset) - int(time.time()) + 2
            )

        else:
            wait_seconds = 60

        self._log(                                                   
            "GitHub rate limit reached. "
            f"Waiting approximately {wait_seconds} seconds."
        )

        deadline = time.monotonic() + wait_seconds

        while time.monotonic() < deadline:
            if self.stop_event.is_set():
                return False

            if not self._wait_if_paused():
                return False

            time.sleep(min(1, max(0, deadline - time.monotonic())))

        return True

    # ---------------- FETCH ONE PAGE ----------------

    def _fetch_page(self, query, page):
        url = "https://api.github.com/search/repositories"

        params = {
            "q": query,
            "per_page": 100,
            "page": page,
            "sort": "stars",
            "order": "desc",
        }

        headers = {"Accept": "application/vnd.github+json"}         
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"

        while not self.stop_event.is_set():
            if not self._wait_if_paused():
                return None

            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30,
                )

            except requests.RequestException as error:
                self._log(f"Connection error: {error}. Retrying in 10 seconds.")
                time.sleep(10)
                continue

            if response.status_code == 200:
                return response.json()

            if response.status_code in (403, 429):
                if not self._wait_for_rate_limit(response):
                    return None
                continue

            if response.status_code >= 500:
                self._log("GitHub server error. Retrying in 10 seconds.")
                time.sleep(10)
                continue

            self._log(
                f"GitHub request failed: {response.status_code} "
                f"{response.text[:300]}"
            )
            return None

        return None

    # ---------------- ONE API ITEM -> ONE CSV ROW ----------------

    def _row_from_item(self, repo):
        return {
            "id": str(repo["id"]),
            "name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "html_url": repo.get("html_url"),
        }

    # ---------------- SCRAPE FROM A URL ----------------

    def add_from_url(self, url):
        """Scrape one repo, topic, user or search URL. Returns how many were new."""
        kind, value = parse_github_url(url)

        if kind == "repo":
            headers = {"Accept": "application/vnd.github+json"}
            if TOKEN:
                headers["Authorization"] = f"Bearer {TOKEN}"
            response = self.session.get(
                f"https://api.github.com/repos/{value}",
                headers=headers,
                timeout=30,
            )
            if response.status_code != 200:
                raise RuntimeError(f"GitHub answered {response.status_code}")
            items = [response.json()]
        else:
            data = self._fetch_page(value, 1)       # first 100 results
            items = data.get("items", []) if data else []

        added = 0
        for repo in items:
            repo_id = str(repo["id"])
            if repo_id not in self.repositories:
                self.repositories[repo_id] = self._row_from_item(repo)
                added += 1

        self._save_data()
        return added

    # ---------------- COLLECT REPOSITORIES ----------------

    def collect(self):
        if self.is_running:
            return

        self.is_running = True
        new_since_save = 0

        try:
            if len(self.repositories) >= TARGET_COUNT:
                self._log("Target already reached.")               
                return

            for query in QUERIES:

                if len(self.repositories) >= TARGET_COUNT:
                    break

                self._log(f"Searching: {query}")                   

                for page in range(1, 11):

                    if self.stop_event.is_set():
                        break

                    if not self._wait_if_paused():
                        break

                    data = self._fetch_page(query, page)

                    if data is None:
                        if self.stop_event.is_set():
                            break

                        self._log("Could not complete this request.") 
                        self._save_data()
                        return

                    items = data.get("items", [])

                    if not items:
                        break

                    for repo in items:
                        if self.stop_event.is_set():
                            break

                        if len(self.repositories) >= TARGET_COUNT:
                            break

                        repo_id = str(repo["id"])

                        if repo_id in self.repositories:
                            continue

                        self.repositories[repo_id] = self._row_from_item(repo)  

                        new_since_save += 1

                        print(
                            f"\rCollected: {len(self.repositories)}"
                            f"/{TARGET_COUNT}",
                            end="",
                            flush=True
                        )

                        if new_since_save >= CHECKPOINT_EVERY:
                            self._save_data()
                            new_since_save = 0

                    if len(items) < 100:
                        break

                    time.sleep(2)

                if self.stop_event.is_set():
                    break

            self._save_data()

            self._log("Collection stopped or completed.")             
            self._log(f"Unique repositories: {len(self.repositories)}")
            print("Saved to:", OUTPUT_FILE)

        finally:
            self.is_running = False

    def close(self):
        self.stop()
        self.session.close()


if __name__ == "__main__":
    scraper = GitHubScraper()

    try:
        scraper.start()

        while scraper.is_running or (
            scraper.thread is not None and scraper.thread.is_alive()
        ):
            time.sleep(0.5)

    except KeyboardInterrupt:
        scraper.stop()
        scraper._save_data()
        print("\nInterrupted. Progress saved.")

    finally:
        scraper.session.close()
