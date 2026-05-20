import httpx
from bs4 import BeautifulSoup

async def ft_steam(client_name: httpx.AsyncClient , site_name: str, url: str):
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}
    
    response = await client_name.get(url, headers=HEADERS, timeout=10.0, follow_redirects=True)
    scrapper = BeautifulSoup(response.text, "html.parser")
    title = scrapper.find("title")
    if title is not None and "Steam Community :: Error" in title.text:
        return {"site": site_name, "Found": False, "url": url}