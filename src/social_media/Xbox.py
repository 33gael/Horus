from playwright.async_api import Browser
from social_media.utils import new_stealth_context

async def ft_xbox(browser: Browser, site_name: str, url: str):
    context = await new_stealth_context(browser)
    page = await context.new_page()
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(2000)
        content = (await page.content()).lower()
        title = (await page.title()).lower()
        status = response.status if response else 200

        if status == 404 or "not found" in title or "gamertag not found" in content:
            return {"site": site_name, "Found": False, "url": url}
        return {"site": site_name, "Found": True, "url": url}

    except Exception as e:
        return {"site": site_name, "Found": False, "error": f"Error: {str(e)[:40]}"}
    finally:
        await context.close()
