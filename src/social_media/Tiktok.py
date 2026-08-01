import httpx

async def ft_tiktok(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    api_url = f"https://www.tiktok.com/oembed?url=https://www.tiktok.com/@{username}"
    try:
        response = await client_name.get(api_url, timeout=15.0, follow_redirects=True)
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        elif response.status_code == 400:
            return {"site": site_name, "Found": False, "url": url}
        elif response.status_code == 404:
            return {"site": site_name, "Found": False, "url": url}
        else:
            return {"site": site_name, "Found": False, "error": f"API Error: {response.status_code}"}
    except httpx.RequestError as e:
        return {"site": site_name, "Found": False, "error": f"Error: {type(e).__name__}"}
