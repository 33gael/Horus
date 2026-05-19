import asyncio
import httpx
from typing import Dict, Any
from playwright.async_api import async_playwright

async def ft_twitter(site_name: str, url: str):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(2000)
            
            title = await page.title()
            current_url = page.url
            
            await browser.close()
            
            if "login" in current_url or "Log in" in title or "Connexion" in title:
                return {"site": site_name, "Found": False, "error": "Blocked by login wall/Captcha"}
            elif title == "Profile / X" or title == "X" or "Account suspended" in title:
                return {"site": site_name, "Found": False, "url": url}
            else:
                return {"site": site_name, "Found": True, "url": url}
                
        except Exception as e:
            await browser.close()
            return {"site": site_name, "Found": False, "error": f"Timeout/Error: {str(e)[:40]}"}

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

async def ft_tiktok(site_name: str, url: str):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080}
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)
        
        page = await context.new_page()
        
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3500)
            
            content = await page.content()
            title = await page.title()
            current_url = page.url
            
            await browser.close()
            
            if "Verify to continue" in title or "captcha" in current_url.lower():
                return {"site": site_name, "Found": False, "error": "Blocked by TikTok Captcha"}
                
            if 'data-e2e="user-title"' in content or 'data-e2e="user-subtitle"' in content:
                return {"site": site_name, "Found": True, "url": url}
                
            if "Couldn't find this account" in content or "Compte introuvable" in content:
                return {"site": site_name, "Found": False, "url": url}
                
            if response and response.status == 404:
                return {"site": site_name, "Found": False, "url": url}
                
            return {"site": site_name, "Found": False, "error": "Blocked or empty page"}
                
        except Exception as e:
            await browser.close()
            return {"site": site_name, "Found": False, "error": f"Timeout/Error: {str(e)[:40]}"}

async def site_checker(client_name: httpx.AsyncClient, site_name: str, site_data: str, username: str):
    url = site_data.replace("{username}", username)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if site_name == "Instagram":
            return await ft_instagram(client_name, site_name, url, username)
        if site_name == "X":
            return await ft_twitter(site_name, url)
        if site_name == "Tiktok":
            return await ft_tiktok(site_name, url)
        response = await client_name.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        if response.status_code == 200:
            return {"site": site_name, "Found": True, "url": url}
        else:
            return {"site": site_name, "Found": False, "url": url}
    except httpx.RequestError:
        return {"site": site_name, "Found": False, "error": "timeout or dns error"}

async def site_scanner(username: str, sites_dict: Dict[str, str]):
    print(f"[*] - Searching an account with the Username : '{username}' on {len(sites_dict)} sites")
    async with httpx.AsyncClient() as client:
        tasks = []
        for site_name, site_data in sites_dict.items():
            task = site_checker(client, site_name, site_data, username)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
    return results