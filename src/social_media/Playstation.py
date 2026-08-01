from playwright.async_api import Browser
from social_media.utils import new_stealth_context

async def ft_playstation(browser: Browser, site_name: str, url: str):
    context = await new_stealth_context(browser, ignore_https_errors=True)
    page = await context.new_page()
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(8000)
        title = (await page.title()).lower()
        content = (await page.content()).lower()
        status = response.status if response else 200

        if len(content) < 5000:
            return {"site": site_name, "Found": False, "error": "Blocked by network/DNS filter"}
        if status == 403 or "attention required" in title or "just a moment" in title:
            return {"site": site_name, "Found": False, "error": "Blocked by Cloudflare"}
        if status == 404 or "not found" in title or "could not be found" in content:
            return {"site": site_name, "Found": False, "url": url}
        return {"site": site_name, "Found": True, "url": url}

    except Exception as e:
        return {"site": site_name, "Found": False, "error": f"Error: {str(e)[:40]}"}
    finally:
        await context.close()
