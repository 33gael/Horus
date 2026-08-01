from playwright.async_api import Browser
from social_media.utils import new_stealth_context

async def ft_steam(browser: Browser, site_name: str, url: str):
    context = await new_stealth_context(browser, ignore_https_errors=True)
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(1500)
        title = (await page.title()).lower()
        content = (await page.content()).lower()
        if len(content) < 5000:
            return {"site": site_name, "Found": False, "error": "Blocked by network/DNS filter"}
        if ":: error" in title or "could not be found" in content:
            return {"site": site_name, "Found": False, "url": url}
        return {"site": site_name, "Found": True, "url": url}

    except Exception as e:
        return {"site": site_name, "Found": False, "error": f"Error: {str(e)[:40]}"}
    finally:
        await context.close()
