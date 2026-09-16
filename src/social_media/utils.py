from contextlib import suppress

from playwright.async_api import Browser, BrowserContext, Error

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": BROWSER_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
}

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
window.chrome = { runtime: {} };
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
if (window.navigator.permissions && window.navigator.permissions.query) {
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters)
    );
}
"""

_LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--no-first-run",
    "--disable-infobars",
    "--mute-audio",
]

async def launch_browser(pw) -> Browser | None:
    try:
        return await pw.chromium.launch(channel="chromium", headless=True, args=_LAUNCH_ARGS)
    except Exception:
        try:
            return await pw.chromium.launch(headless=True, args=_LAUNCH_ARGS)
        except Exception:
            return None

async def get_browser_ua(browser: Browser) -> str:
    cached = getattr(browser, "_horus_ua", None)
    if cached:
        return cached
    ua = BROWSER_UA
    context = None
    try:
        context = await browser.new_context()
        page = await context.new_page()
        ua = (await page.evaluate("navigator.userAgent")).replace("HeadlessChrome", "Chrome")
    except Error:
        pass
    finally:
        if context is not None:
            with suppress(Error):
                await context.close()
    browser._horus_ua = ua
    return ua

async def new_stealth_context(browser: Browser, ignore_https_errors: bool = False) -> BrowserContext:
    context = await browser.new_context(
        user_agent=await get_browser_ua(browser),
        locale="en-US",
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=ignore_https_errors,
    )
    try:
        await context.add_init_script(STEALTH_JS)
    except BaseException:
        with suppress(Error):
            await context.close()
        raise
    return context
