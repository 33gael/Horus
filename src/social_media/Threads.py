from playwright.async_api import Browser
from social_media.utils import new_stealth_context

async def ft_threads(browser: Browser, site_name: str, url: str, username: str):
    context = await new_stealth_context(browser)
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_timeout(2500)
        title = (await page.title()).lower()
        final_url = page.url.lower()

        if f"(@{username.lower()})" in title:
            return {"site": site_name, "Found": True, "url": url}
        if "log in" in title or "login" in final_url:
            return {"site": site_name, "Found": False, "url": url}
        return {"site": site_name, "Found": False, "url": url}

    except Exception as e:
        return {"site": site_name, "Found": False, "error": f"Error: {str(e)[:40]}"}
    finally:
        await context.close()
