import asyncio
import re
from contextlib import AsyncExitStack, suppress
from urllib.parse import quote

import httpx
from playwright.async_api import Error, async_playwright

from social_media.api import API_SITES, check_api
from social_media.browser import check_browser
from social_media.detection import inspect_profile, unknown
from social_media.social import SOCIAL_SITES, check_social
from social_media.utils import HEADERS, get_browser_ua, launch_browser

BROWSER_SITES = {"Steam", "Reddit", "Facebook", "Threads", "Xbox", "PlayStation", "Spotify", "ArtStation", "VK"}


async def site_checker(client_name, browser, site_name, site_data, username):
    url = site_data.replace("{username}", quote(username, safe=""))
    try:
        async with asyncio.timeout(45 if site_name in SOCIAL_SITES else 35):
            if site_name in SOCIAL_SITES:
                return await check_social(client_name, browser, site_name, url, username)
            if site_name in API_SITES:
                return await check_api(client_name, site_name, url, username)
            if site_name in BROWSER_SITES:
                return await check_browser(browser, site_name, url, username)
            headers = {"Cookie": "SOCS=CAI"} if site_name == "YouTube" else {}
            params = {"ucbcb": "1"} if site_name == "YouTube" else None
            response = await client_name.get(url, headers=headers, params=params)
            return inspect_profile(site_name, url, str(response.url), response.status_code, response.text, username)
    except (TimeoutError, httpx.TimeoutException):
        return unknown(site_name, url, "Request timed out")
    except httpx.RequestError as exc:
        return unknown(site_name, url, f"Network error: {type(exc).__name__}")
    except Exception as exc:
        return unknown(site_name, url, f"Check failed: {type(exc).__name__}")


async def site_scanner(username, sites_dict, progress_callback=None):
    if not isinstance(username, str) or not re.fullmatch(r"[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,99}", username):
        raise ValueError("Invalid username")
    async with AsyncExitStack() as stack:
        browser = None
        if (BROWSER_SITES | SOCIAL_SITES).intersection(sites_dict):
            with suppress(Error):
                pw = await stack.enter_async_context(async_playwright())
                browser = await launch_browser(pw)
        headers = dict(HEADERS)
        if browser is not None:
            headers["User-Agent"] = await get_browser_ua(browser)
        client = await stack.enter_async_context(httpx.AsyncClient(
            headers=headers, follow_redirects=True, timeout=15.0,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        ))
        http_slots, browser_slots = asyncio.Semaphore(8), asyncio.Semaphore(3)

        async def check(site, template):
            slots = browser_slots if site in BROWSER_SITES | SOCIAL_SITES else http_slots
            async with slots:
                try:
                    return await site_checker(client, browser, site, template, username)
                finally:
                    if progress_callback is not None:
                        progress_callback()

        try:
            return await asyncio.gather(*(check(site, template) for site, template in sites_dict.items()))
        finally:
            if browser is not None:
                with suppress(Error):
                    await browser.close()
