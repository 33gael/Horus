import httpx

from social_media.api import check_api
from social_media.browser import check_browser
from social_media.detection import inspect_profile, unknown


SOCIAL_SITES = {"Instagram", "TikTok", "X", "Facebook", "Pinterest", "Tumblr", "Linktree", "Last.fm", "Unsplash"}


async def check_social(client, browser, site, url, username):
    try:
        if site in {"Instagram", "TikTok", "X"}:
            primary = await check_api(client, site, url, username)
        else:
            response = await client.get(url)
            primary = inspect_profile(site, url, str(response.url), response.status_code, response.text, username)
    except httpx.RequestError as exc:
        primary = unknown(site, url, f"Network error: {type(exc).__name__}")
    if primary["status"] in {"found", "not_found"} or browser is None:
        return primary
    if "HTTP 429" in primary.get("error", ""):
        return primary
    fallback = await check_browser(browser, site, url, username)
    if fallback["status"] in {"found", "not_found", "blocked"}:
        return fallback
    return primary if primary["status"] == "blocked" else fallback
