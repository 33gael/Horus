import httpx

async def ft_mixcloud(client_name: httpx.AsyncClient, site_name: str, url: str):
    try:
        response = await client_name.get(url, timeout=15.0)
        content = response.text.lower()
        if response.status_code == 404 or "page not found" in content:
            return {"site": site_name, "Found": False, "url": url}
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        return {"site": site_name, "Found": False, "error": f"Error: {response.status_code}"}
    except httpx.RequestError as e:
        return {"site": site_name, "Found": False, "error": f"Error: {type(e).__name__}"}
