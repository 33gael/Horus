from playwright.async_api import Browser
from social_media.utils import new_stealth_context

async def ft_reddit(browser: Browser, site_name: str, url: str):
    context = await new_stealth_context(browser)
    page = await context.new_page()
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_timeout(2000)
        content = ""
        for _ in range(3):
            try:
                content = (await page.content()).lower()
                break
            except Exception:
                await page.wait_for_timeout(1000)
        if not content:
            return {"site": site_name, "Found": False, "error": "Error: page content unavailable"}
        status = response.status if response else 200

        if status == 403 or "blocked by network security" in content:
            return {"site": site_name, "Found": False, "error": "Blocked by anti-bot (403)"}
        if status == 404 or "nobody on reddit goes by that name" in content:
            return {"site": site_name, "Found": False, "url": url}
        return {"site": site_name, "Found": True, "url": url}

    except Exception as e:
        return {"site": site_name, "Found": False, "error": f"Error: {str(e)[:40]}"}
    finally:
        await context.close()
