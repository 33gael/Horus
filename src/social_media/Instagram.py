import httpx

IG_APP_ID = "936619743392459"

async def ft_instagram(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    try:
        response = await client_name.get(api_url, headers={"X-IG-App-ID": IG_APP_ID}, timeout=15.0)
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        if response.status_code == 404:
            return {"site": site_name, "Found": False, "url": url}
        if response.status_code in (401, 403, 429):
            return {"site": site_name, "Found": False, "error": f"Blocked by anti-bot ({response.status_code})"}
        return {"site": site_name, "Found": False, "error": f"API Error: {response.status_code}"}
    except httpx.RequestError as e:
        return {"site": site_name, "Found": False, "error": f"Error: {type(e).__name__}"}
