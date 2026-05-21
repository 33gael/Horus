import httpx

async def ft_chess(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    headers = {
        "User-Agent": "Horus-OSINT-Script/1.0 (Mozilla/5.0 Windows NT 10.0; Win64; x64)"
    }
    api_url = f"https://api.chess.com/pub/player/{username}"
    try:
        response = await client_name.get(api_url, headers=headers, timeout=10.0, follow_redirects=True)
        
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        elif response.status_code == 404:
            return {"site": site_name, "Found": False, "url": url}
        else:
            return {"site": site_name, "Found": False, "error": f"API Error: {response.status_code}"}

    except httpx.RequestError as e:
        return {"site": site_name, "Found": False, "error": f"Error: {type(e).__name__}"}