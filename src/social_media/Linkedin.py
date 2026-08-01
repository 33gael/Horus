import httpx

async def ft_linkedin(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    try:
        response = await client_name.get(url, timeout=15.0)
        content = response.text.lower()
        if response.status_code == 404 or "profile not found" in content or "page not found" in content:
            return {"site": site_name, "Found": False, "url": url}
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        if response.status_code in (999, 403, 429):
            return {"site": site_name, "Found": False, "error": "Blocked by LinkedIn authwall"}
        return {"site": site_name, "Found": False, "error": f"Error: {response.status_code}"}
    except httpx.RequestError as e:
        return {"site": site_name, "Found": False, "error": f"Error: {type(e).__name__}"}
