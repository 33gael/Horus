from playwright.async_api import async_playwright

async def ft_steam(client_name, site_name: str, url: str):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--ignore-certificate-errors"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True
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
            await page.wait_for_timeout(2000)
            title = await page.title()
            await browser.close()
            if "Steam Community :: Error" in title:
                return {"site": site_name, "Found": False, "url": url}
            else:
                return {"site": site_name, "Found": True, "url": url}

        except Exception as e:
            await browser.close()
            return {"site": site_name, "Found": False, "error": f"Timeout/Error: {str(e)[:40]}"}