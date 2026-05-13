from bs4 import BeautifulSoup
import asyncio
import httpx
from typing import Dict, Any

async def site_checker(client_name: httpx.AsyncClient, site_name: str, site_data: Dict[str, Any], username: str):
	url = site_data["url"].format(username)
	try:
		reponse = await client_name.get(url, timeout = 10.0)
		if reponse.status_code == 200 :
			return {"site": site_name, "Found": True, "url": url}
		else :
			return {"site": site_name, "Found": False, "url": url}
	except httpx.RequestError:
		return {"site": site_name, "Found": False, "error": "timeout or dns error :("}

async def site_scanner(username: str, sites_dict: Dict[str, Any]):
    print(f"[*] - Searching an account with the Username : '{username}' on {len(sites_dict)} sites")
    async with httpx.AsyncClient as client:
        