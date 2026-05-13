import asyncio
import httpx
from typing import Dict, Any

async def site_checker(client_name: httpx.AsyncClient, site_name: str, site_data: str, username: str):
    url = site_data.replace("{username}", username)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
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
