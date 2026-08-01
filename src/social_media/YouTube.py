import httpx

async def ft_youtube(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    channel_url = f"https://www.youtube.com/@{username}"
    try:
        response = await client_name.get(channel_url, headers={"Cookie": "SOCS=CAI"}, timeout=15.0)
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        if response.status_code == 404:
            return {"site": site_name, "Found": False, "url": url}
        if response.status_code in (403, 429):
            return {"site": site_name, "Found": False, "error": f"Blocked by anti-bot ({response.status_code})"}
        return {"site": site_name, "Found": False, "error": f"Error: {response.status_code}"}
    except httpx.RequestError as e:
        return {"site": site_name, "Found": False, "error": f"Error: {type(e).__name__}"}
