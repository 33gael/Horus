from bs4 import BeautifulSoup
import asyncio
import httpx
from typing import Dict, Any

async def   site_checker(client_name: httpx.AsyncClient, site_name: str, site_data: Dict[str, Any], username: str):
    url = site_data["url"].format(username);