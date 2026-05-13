import asyncio
import httpx
from typing import Dict, Any

async def site_checker(client_name: httpx.AsyncClient, site_name: str, site_data: str, username: str):
	url = site_data.replace("{username}", username)
	try:
		reponse = await client_name.get(url, timeout = 10.0)
		if reponse.status_code == 200 :
			return {"site": site_name, "Found": True, "url": url}
		else :
			return {"site": site_name, "Found": False, "url": url}
	except httpx.RequestError:
		return {"site": site_name, "Found": False, "error": "timeout or dns error :("}

async def site_scanner(username: str, sites_dict: Dict[str, str]):
	print(f"[*] - Searching an account with the Username : '{username}' on {len(sites_dict)} sites")
	async with httpx.AsyncClient() as client:
		tasks = []
		for site_name, site_data in sites_dict.items():
			task = site_checker(client, site_name, site_data, username)
			tasks.append(task)
		results = await asyncio.gather(*tasks)
	return results
