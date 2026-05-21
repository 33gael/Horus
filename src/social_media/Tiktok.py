import httpx

async def ft_tiktok(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    api_url = f"https://www.tiktok.com/oembed?url=https://www.tiktok.com/@{username}"
    
    try:
        response = await client_name.get(api_url, headers=headers, timeout=10.0, follow_redirects=True)
        
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        elif response.status_code == 404:
            return {"site": site_name, "Found": False, "url": url}
    except httpx.RequestError as e:
        return {"site": site_name, "Found": False, "error": f"Timeout/Error: {type(e).__name__}"}
