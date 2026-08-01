import httpx

async def ft_twitch(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    api_url = f"https://decapi.me/twitch/id/{username}"
    try:
        response = await client_name.get(api_url, timeout=15.0)
        body = response.text.strip().lower()
        if "user not found" in body:
            return {"site": site_name, "Found": False, "url": url}
        if response.status_code == 200 and body:
            return {"site": site_name, "Found": True, "url": url}
        return {"site": site_name, "Found": False, "error": f"API Error: {response.status_code}"}
    except httpx.RequestError as e:
        return {"site": site_name, "Found": False, "error": f"Error: {type(e).__name__}"}
