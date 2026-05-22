import httpx

async def ft_instagram(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    mirrors = [
        f"https://www.picuki.com/profile/{username}",
        f"https://imginn.com/{username}/",
        f"https://dumpor.com/v/{username}"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    last_error = ""

    for mirror in mirrors:
        try:
            response = await client_name.get(mirror, headers=headers, timeout=10.0, follow_redirects=True)
            if response.status_code in [403, 429]:
                last_error = f"Blocked ({response.status_code}) by {mirror.split('/')[2]}"
                continue
            content = response.text.lower()
            if response.status_code == 404 or "not found" in content or "doesn't exist" in content:
                return {"site": site_name, "Found": False, "url": url}
            elif response.status_code == 200:
                return {"site": site_name, "Found": True, "url": url}

        except httpx.RequestError as e:
            last_error = f"{type(e).__name__} sur {mirror.split('/')[2]}"
            continue
    return {"site": site_name, "Found": False, "error": f"Blocked, error: {last_error}"}