import asyncio
import httpx
from typing import Dict
from playwright.async_api import async_playwright

from social_media.utils import HEADERS, launch_browser
from social_media.Twitter import ft_twitter
from social_media.Tiktok import ft_tiktok
from social_media.Instagram import ft_instagram
from social_media.Steam import ft_steam
from social_media.Hackerrank import ft_hackerrank
from social_media.YouTube import ft_youtube
from social_media.Twitch import ft_twitch
from social_media.Reddit import ft_reddit
from social_media.Facebook import ft_facebook
from social_media.Threads import ft_threads
from social_media.Linkedin import ft_linkedin
from social_media.Mixcloud import ft_mixcloud
from social_media.Xbox import ft_xbox
from social_media.Playstation import ft_playstation
from social_media.Roblox import ft_roblox
from social_media.Chess import ft_chess
from social_media.Pinterest import ft_pinterest
from social_media.Spotify import ft_spotify

BROWSER_SITES = {"Steam", "Reddit", "Facebook", "Threads", "Xbox", "PlayStation", "Spotify"}

async def site_checker(client_name: httpx.AsyncClient, browser, site_name: str, site_data: str, username: str):
    url = site_data.replace("{username}", username)

    if site_name in BROWSER_SITES and browser is None:
        return {"site": site_name, "Found": False, "error": "browser unavailable"}

    try:
        if site_name == "Instagram":
            return await ft_instagram(client_name, site_name, url, username)
        if site_name == "X":
            return await ft_twitter(client_name, site_name, url, username)
        if site_name == "TikTok":
            return await ft_tiktok(client_name, site_name, url, username)
        if site_name == "Steam":
            return await ft_steam(browser, site_name, url)
        if site_name == "HackerRank":
            return await ft_hackerrank(client_name, site_name, url, username)
        if site_name == "YouTube":
            return await ft_youtube(client_name, site_name, url, username)
        if site_name == "Twitch":
            return await ft_twitch(client_name, site_name, url, username)
        if site_name == "Reddit":
            return await ft_reddit(browser, site_name, url)
        if site_name == "Facebook":
            return await ft_facebook(browser, site_name, url)
        if site_name == "Threads":
            return await ft_threads(browser, site_name, url, username)
        if site_name == "LinkedIn":
            return await ft_linkedin(client_name, site_name, url, username)
        if site_name == "Mixcloud":
            return await ft_mixcloud(client_name, site_name, url)
        if site_name == "Xbox":
            return await ft_xbox(browser, site_name, url)
        if site_name == "PlayStation":
            return await ft_playstation(browser, site_name, url)
        if site_name == "Roblox":
            return await ft_roblox(client_name, site_name, url, username)
        if site_name == "Chess.com":
            return await ft_chess(client_name, site_name, url, username)
        if site_name == "Pinterest":
            return await ft_pinterest(client_name, site_name, url, username)
        if site_name == "Spotify":
            return await ft_spotify(browser, site_name, url)

        extra_headers = {}
        if site_name.startswith("Wikipedia"):
            extra_headers["User-Agent"] = "Horus-OSINT-Scanner/1.0 (https://github.com/33gael/Horus; username research tool)"

        response = await client_name.get(url, headers=extra_headers, timeout=15.0)
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        if response.status_code in (404, 410):
            return {"site": site_name, "Found": False, "url": url}
        if response.status_code in (401, 403, 429):
            return {"site": site_name, "Found": False, "error": f"Blocked by anti-bot ({response.status_code})"}
        return {"site": site_name, "Found": False, "url": url}

    except httpx.RequestError:
        return {"site": site_name, "Found": False, "error": "timeout or dns error"}

async def site_scanner(username: str, sites_dict: Dict[str, str]):
    print(f"[*] - Searching an account with the Username : '{username}' on {len(sites_dict)} sites")
    async with async_playwright() as pw:
        browser = await launch_browser(pw)
        try:
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=15.0) as client:
                tasks = []
                for site_name, site_data in sites_dict.items():
                    task = site_checker(client, browser, site_name, site_data, username)
                    tasks.append(task)
                results = await asyncio.gather(*tasks)
        finally:
            if browser is not None:
                await browser.close()
    return results
