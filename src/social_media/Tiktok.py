from playwright.async_api import async_playwright

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
            return {"site": site_name, "Found": False, "error": "Blocked or empty page, please retry"}

        except Exception as e:
            await browser.close()
            return {"site": site_name, "Found": False, "error": f"Timeout/Error: {str(e)[:40]}"}
