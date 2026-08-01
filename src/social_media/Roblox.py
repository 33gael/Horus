import httpx

async def ft_roblox(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    api_url = "https://users.roblox.com/v1/usernames/users"
    try:
        response = await client_name.post(api_url, json={"usernames": [username], "excludeBannedUsers": False}, timeout=15.0)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                user_id = data[0].get("id")
                profile_url = f"https://www.roblox.com/users/{user_id}/profile" if user_id else url
                return {"site": site_name, "Found": True, "url": profile_url}
            return {"site": site_name, "Found": False, "url": url}
        if response.status_code == 429:
            return {"site": site_name, "Found": False, "error": "Blocked by anti-bot (429)"}
        return {"site": site_name, "Found": False, "error": f"API Error: {response.status_code}"}
    except (httpx.RequestError, ValueError) as e:
        return {"site": site_name, "Found": False, "error": f"Error: {type(e).__name__}"}
