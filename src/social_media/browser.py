import asyncio
from contextlib import suppress
from urllib.parse import unquote, urlsplit

from playwright.async_api import Error, TimeoutError

from social_media.detection import inspect_profile, navigation_result, unknown
from social_media.utils import new_stealth_context


async def check_browser(browser, site, url, username=None):
    if browser is None:
        return unknown(site, url, "Browser unavailable")
    username = username or unquote(urlsplit(url).path.rstrip("/").split("/")[-1]).lstrip("@")
    context = None
    page = None
    try:
        context = await new_stealth_context(browser)
        page = await context.new_page()
        navigation = {}

        def track_response(response):
            if response.request.is_navigation_request() and response.frame == page.main_frame:
                navigation["status"] = response.status

        page.on("response", track_response)
        response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        if response is None:
            return unknown(site, url, "No HTTP response from browser")
        verdict = unknown(site, url, "Page content unavailable")
        for attempt in range(6):
            try:
                verdict = inspect_profile(site, url, page.url, navigation.get("status", response.status), await page.content(), username)
                pending_challenge = verdict.get("error") == "Blocked by an anti-bot challenge"
                if verdict["status"] != "unknown" and not pending_challenge:
                    return verdict
            except Error as exc:
                if "navigating" not in str(exc):
                    raise
            if attempt < 5:
                await asyncio.sleep(0.7)
        return verdict
    except TimeoutError:
        verdict = unknown(site, url, "Browser request timed out")
        return navigation_result(verdict, url, page.url) if page is not None else verdict
    except Error as exc:
        message = str(exc).splitlines()[0]
        if "ERR_CERT_" in message or "ERR_SSL_" in message:
            message = "TLS certificate verification failed; check the profile manually"
        else:
            message = f"Browser error: {message[:160]}"
        verdict = unknown(site, url, message)
        return navigation_result(verdict, url, page.url) if page is not None else verdict
    finally:
        if context is not None:
            with suppress(Error):
                await context.close()
