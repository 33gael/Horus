import httpx

async def ft_twitter(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    api_url = f"https://api.fxtwitter.com/{username}"
    try:
        response = await client_name.get(api_url, follow_redirects=False, timeout=15.0)
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        if response.status_code in (301, 302, 404):
            return {"site": site_name, "Found": False, "url": url}
        if response.status_code == 429:
            return {"site": site_name, "Found": False, "error": "Blocked by anti-bot (429)"}
        return {"site": site_name, "Found": False, "error": f"API Error: {response.status_code}"}
    except httpx.RequestError as e:
        return {"site": site_name, "Found": False, "error": f"Error: {type(e).__name__}"}
