import asyncio
import httpx
from typing import Dict

from social_media.Twitter import ft_twitter
from social_media.Tiktok import ft_tiktok
from social_media.Instagram import ft_instagram
from social_media.Steam import ft_steam
from social_media.Hackerrank import ft_hackerrank
from social_media.YouTube import ft_youtube
from social_media.Twitch import ft_twitch
from social_media.Reddit import ft_reddit

async def site_checker(client_name: httpx.AsyncClient, site_name: str, site_data: str, username: str):
    url = site_data.replace("{username}", username)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        if site_name == "Instagram":
            return await ft_instagram(client_name, site_name, url, username)
        if site_name == "X":
            return await ft_twitter(site_name, url)
        if site_name == "TikTok":
            return await ft_tiktok(client_name, site_name, url, username)
        if site_name == "Steam":
            return await ft_steam(client_name, site_name, url)
        if site_name == "HackerRank":
            return await ft_hackerrank(client_name, site_name, url, username)
        if site_name == "YouTube":
            return await ft_youtube(client_name, site_name, url)
        if site_name == "Twitch":
            return await ft_twitch(client_name, site_name, url)
        if site_name == "Reddit":
            return await ft_reddit(client_name, site_name, url)

        response = await client_name.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        else:
            return {"site": site_name, "Found": False, "url": url}

    except httpx.RequestError:
        return {"site": site_name, "Found": False, "error": "timeout or dns error"}

async def site_scanner(username: str, sites_dict: Dict[str, str]):
    print(f"[*] - Searching an account with the Username : '{username}' on {len(sites_dict)} sites")
    async with httpx.AsyncClient() as client:
        tasks = []
        for site_name, site_data in sites_dict.items():
            task = site_checker(client, site_name, site_data, username)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
    return results