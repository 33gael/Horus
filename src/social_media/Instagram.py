import httpx
from playwright.async_api import async_playwright

async def ft_instagram(client_name: httpx.AsyncClient, site_name: str, url: str, username: str):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    api_url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

    ig_headers = headers.copy()
    ig_headers["x-ig-app-id"] = "936619743392459"

    response = await client_name.get(api_url, headers=ig_headers, timeout=10.0, follow_redirects=True)
    if response.status_code == 404:
        return {"site": site_name, "Found": False, "url": url}
    elif response.status_code == 200:
        try:
            data = response.json()
            if "data" in data and data["data"]["user"] is not None:
                return {"site": site_name, "Found": True, "url": url}
            else:
                return {"site": site_name, "Found": False, "error": "Account deactivated"}
        except Exception:
            return {"site": site_name, "Found": False, "error": "Please try again"}
    else:
        return {"site": site_name, "Found": False, "error": f"API error {response.status_code}"}
