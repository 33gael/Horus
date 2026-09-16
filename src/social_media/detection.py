import json
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit


def result(site, url, status, error=None):
    data = {"site": site, "url": url, "Found": status == "found", "status": status}
    if error:
        data["error"] = error
    return data


def unknown(site, url, error="Profile could not be verified"):
    return result(site, url, "unknown", error)


def http_result(site, url, status):
    if status in (404, 410):
        return result(site, url, "not_found")
    if status in (401, 403, 429, 999):
        return result(site, url, "blocked", f"Access blocked (HTTP {status})")
    if status != 200:
        return unknown(site, url, f"Unexpected HTTP status {status}")
    return None


class ProfileHTML(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.title = ""
        self.title_closed = False
        self.headings = []
        self.visible = []
        self.tag = None
        self.hidden = 0
        self.script_id = None
        self.scripts = {}
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style"):
            self.hidden += 1
        if tag == "script" and attrs.get("id") == "__UNIVERSAL_DATA_FOR_REHYDRATION__":
            self.script_id = attrs["id"]
            self.scripts[self.script_id] = ""
        if tag == "h1" or (tag == "title" and not self.title_closed):
            self.tag = tag
        if tag == "meta":
            self.meta[attrs.get("property", attrs.get("name", "")).lower()] = attrs.get("content", "")

    def handle_endtag(self, tag):
        if tag == "title" and self.tag == "title":
            self.title_closed = True
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
        if tag == "script":
            self.script_id = None
        if tag == self.tag:
            self.tag = None

    def handle_data(self, text):
        if self.script_id is not None:
            self.scripts[self.script_id] += text
        if self.hidden:
            return
        self.visible.append(text)
        if self.tag == "title":
            self.title += text
        elif self.tag == "h1":
            self.headings.append(text)


def same_profile(actual, expected):
    actual, expected = urlsplit(actual), urlsplit(expected)
    aliases = {"twitter.com": "x.com", "threads.net": "threads.com", "vk.com": "vk.ru"}
    def host(value):
        name = (value.hostname or "").removeprefix("www.")
        return aliases.get(name, name)
    return host(actual) == host(expected) and unquote(actual.path).rstrip("/").casefold() == unquote(expected.path).rstrip("/").casefold()


def navigation_result(verdict, requested_url, final_url):
    try:
        parsed = urlsplit(final_url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or any(ord(char) < 32 for char in final_url):
            return verdict
        destination = parsed._replace(query="", fragment="").geturl()
    except ValueError:
        return verdict
    if destination.rstrip("/") != requested_url.rstrip("/"):
        verdict["final_url"] = destination
        if verdict["status"] == "found":
            verdict["requested_url"] = requested_url
            verdict["url"] = destination
    return verdict


def inspect_profile(site, url, final_url, status, content, username):
    verdict = detect_profile(site, url, final_url, status, content, username)
    return navigation_result(verdict, url, final_url)


def detect_profile(site, url, final_url, status, content, username):
    verdict = http_result(site, url, status)
    if verdict and verdict["status"] != "unknown":
        return verdict
    page = ProfileHTML(content)
    title = page.title.strip().casefold()
    heading = " ".join(page.headings).casefold()
    visible = " ".join(page.visible).casefold()
    path = urlsplit(final_url).path.casefold()
    host = urlsplit(final_url).hostname or ""
    if path in ("/challenge.html", "/.within.website", "/.within.website/x/cmd/anubis/api/pass-challenge"):
        return result(site, url, "blocked", "Blocked by an anti-bot challenge")
    if any(word in title + " " + heading for word in (
        "just a moment", "attention required", "access denied", "security check",
        "verify you are human", "robot or human", "captcha", "pardon our interruption", "client challenge",
    )) or "blocked by network security" in visible:
        return result(site, url, "blocked", "Blocked by an anti-bot challenge")
    if verdict:
        return verdict
    if re.search(r"/(?:login|log-in|signin|sign-in|authwall|checkpoint|consent)(?:/|$)", path) or host.startswith(("login.", "consent.")):
        return result(site, url, "blocked", "Login or consent required")
    if any(word in title + " " + heading for word in (
        "page not found", "profile not found", "user not found", "account not found", "channel not found",
        "could not be found", "doesn't exist", "does not exist", "isn't available",
    )):
        return result(site, url, "not_found")
    if site == "ArtStation" and path == "/404" and "404" in title:
        return result(site, url, "not_found")
    if site == "Steam" and "the specified profile could not be found" in visible:
        return result(site, url, "not_found")
    if site == "Reddit" and "nobody on reddit goes by that name" in visible:
        return result(site, url, "not_found")
    if site == "Xbox" and "gamertag not found" in visible:
        return result(site, url, "not_found")
    if title in ("log in", "sign in", "login", "facebook – log in or sign up"):
        return result(site, url, "blocked", "Login required")
    expected_url = url
    if site == "VSCO":
        expected_url = url.rstrip("/") + "/gallery"
    elif site == "Snapchat":
        expected_url = f"https://www.snapchat.com/@{username}"
    elif site == "Patreon" and re.fullmatch(r"/(?:c|cw)/" + re.escape(username) + r"/?", urlsplit(final_url).path, re.I):
        expected_url = urlsplit(url)._replace(path=urlsplit(final_url).path, query="", fragment="").geturl()
    elif site == "Behance" and urlsplit(final_url).path.rstrip("/").casefold() == f"/{username}/moodboards".casefold():
        expected_url = url.rstrip("/") + "/moodboards"
    elif site == "Pixabay" and re.fullmatch(r"/users/" + re.escape(username) + r"-\d+/?", urlsplit(final_url).path, re.I):
        expected_url = urlsplit(url)._replace(path=urlsplit(final_url).path, query="", fragment="").geturl()
    elif site == "Goodreads" and re.fullmatch(r"/user/show/\d+[^/]*", urlsplit(final_url).path) and page.meta.get("profile:username", "").casefold() == username.casefold():
        expected_url = urlsplit(url)._replace(path=urlsplit(final_url).path, query="", fragment="").geturl()
    if not same_profile(final_url, expected_url):
        return unknown(site, url, "Redirected away from the requested profile")
    if site == "TikTok":
        try:
            data = json.loads(page.scripts.get("__UNIVERSAL_DATA_FOR_REHYDRATION__", "{}"))
            detail = data["__DEFAULT_SCOPE__"]["webapp.user-detail"]
            if detail.get("statusCode") == 10221:
                return result(site, url, "not_found")
            user = detail.get("userInfo", {}).get("user", {})
            if detail.get("statusCode") == 0 and user.get("id") and str(user.get("uniqueId", "")).casefold() == username.casefold():
                return result(site, url, "found")
        except (ValueError, KeyError, TypeError, AttributeError):
            pass
    if site == "Spotify" and re.search(r'data-testid=["\']user-image["\']', content) and re.search(r'data-testid=["\']entityTitle["\']', content):
        return result(site, url, "found")
    if site == "VK" and "ProfileBase" in content and re.search(r'"domain"\s*:\s*"' + re.escape(username) + r'"', content, re.I):
        return result(site, url, "found")
    escaped = re.escape(username.casefold())
    identity = re.search(rf"(?<![\w.-])@?{escaped}(?![\w.-])", title + " " + heading + " " + page.meta.get("og:title", "").casefold())
    if site == "Xbox":
        identity = any(re.sub(r"[\s-]", "", text).casefold() == re.sub(r"[\s-]", "", username).casefold() for text in page.headings)
    meta_url = page.meta.get("og:url", "")
    profile_type = page.meta.get("og:type", "").casefold() in ("profile", "profilepage")
    profile_user = page.meta.get("profile:username", "").casefold() == username.casefold()
    markers = {
        "Steam": r'profile_header_centered_persona|actual_persona_name',
        "Reddit": r'<shreddit-profile|data-testid=["\']profile',
        "YouTube": r'"channelMetadataRenderer"\s*:',
        "Pinterest": r'"isPartner"\s*:|"follower_count"\s*:',
        "Spotify": r'data-testid=["\']user-widget|spotify:user:',
        "Xbox": r'gamerscore',
        "PlayStation": r'profile-bar|trophy-box',
        "LinkedIn": r'"@type"\s*:\s*"Person"',
        "Kick": r'og:image[^>]+files\.kick\.com/images/user/',
        "Behance": r'og:image[^>]+behance\.net/',
        "Wattpad": r'class=["\'][^"\']*profile|"username"\s*:',
        "Pixabay": r'class=["\'][^"\']*userInfo--',
    }
    marker = markers.get(site)
    profile_evidence = bool(marker and re.search(marker, content, re.I))
    if profile_user or (profile_type and same_profile(meta_url, expected_url)) or (identity and (profile_evidence or same_profile(meta_url, expected_url))):
        return result(site, url, "found")
    return unknown(site, url)
