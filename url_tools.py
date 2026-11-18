from urllib.parse import parse_qs, urlparse

# First path segments on github.com that are pages, not owners
RESERVED = {
    "orgs", "users", "topics", "trending", "collections", "features",
    "marketplace", "sponsors", "settings", "notifications", "explore",
    "issues", "pulls", "login", "about", "pricing", "enterprise", "apps",
}


def parse_github_url(url):
    """Return ("repo", "owner/name") or ("search", "<GitHub search query>")."""
    url = url.strip()
    if "://" not in url:
        url = "https://" + url            
    p = urlparse(url)
    if p.netloc.lower() not in ("github.com", "www.github.com"):
        raise ValueError("That is not a github.com URL")

    parts = [x for x in p.path.split("/") if x]
    if not parts:
        raise ValueError("The URL has no path")

    first = parts[0].lower()
    if first == "search":
        q = parse_qs(p.query).get("q", [""])[0]
        if not q:
            raise ValueError("The search URL has no q= value")
        return ("search", q)
    if first == "topics":
        if len(parts) < 2:
            raise ValueError("The topics URL has no topic name")
        return ("search", f"topic:{parts[1]}")
    if first in RESERVED:
        if first in ("orgs", "users") and len(parts) >= 2:
            return ("search", f"user:{parts[1]}")
        raise ValueError(f"'{parts[0]}' is a GitHub page, not a repository")

    if len(parts) == 1:
        return ("search", f"user:{parts[0]}")
    name = parts[1]
    if name.endswith(".git"):
        name = name[:-4]                   
    return ("repo", f"{parts[0]}/{name}")