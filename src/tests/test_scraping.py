import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

import httpx

from Horus import site_checker, site_scanner
from social_media.browser import check_browser
from social_media.detection import inspect_profile


class PageDetectionTests(unittest.TestCase):
    def check(self, content, status=200, final_url=None, site="Pinterest", url="https://pinterest.com/alice"):
        return inspect_profile(site, url, final_url or url, status, content, "alice")

    def test_generic_success_is_unknown(self):
        self.assertEqual(self.check("<title>Pinterest</title>")["status"], "unknown")

    def test_http_errors_are_not_missing_accounts(self):
        for code in (301, 400, 500, 502, 503):
            with self.subTest(code=code):
                self.assertEqual(self.check("", status=code)["status"], "unknown")

    def test_blocked_statuses(self):
        for code in (401, 403, 429, 999):
            with self.subTest(code=code):
                self.assertEqual(self.check("", status=code)["status"], "blocked")

    def test_missing_statuses(self):
        for code in (404, 410):
            self.assertEqual(self.check("", status=code)["status"], "not_found")

    def test_challenge_is_not_a_profile(self):
        self.assertEqual(self.check("<title>Just a moment...</title>")["status"], "blocked")

    def test_login_redirect(self):
        self.assertEqual(self.check("", final_url="https://pinterest.com/login/?next=/alice")["status"], "blocked")

    def test_home_redirect(self):
        self.assertEqual(self.check("<title>alice</title>", final_url="https://pinterest.com/")["status"], "unknown")

    def test_profile_identity(self):
        html = '<title>Alice (@alice)</title><meta property="og:url" content="https://www.pinterest.com/alice/">'
        self.assertEqual(self.check(html)["status"], "found")

    def test_username_echo_alone_is_insufficient(self):
        self.assertEqual(self.check("<title>alice</title>")["status"], "unknown")

    def test_error_strings_in_scripts_are_ignored(self):
        html = '<script>const messages = "user not found"</script><title>Alice</title><meta property="profile:username" content="alice">'
        self.assertEqual(self.check(html)["status"], "found")

    def test_similar_username_does_not_match(self):
        html = '<title>Alicebob</title><meta property="og:url" content="https://pinterest.com/alice">'
        self.assertEqual(self.check(html)["status"], "unknown")

    def test_spotify_web_player_title_is_not_missing(self):
        html = '<title>Alice | Spotify – Web Player</title><meta property="og:type" content="profile"><meta property="og:url" content="https://open.spotify.com/user/alice">'
        self.assertEqual(self.check(html, site="Spotify", url="https://open.spotify.com/user/alice")["status"], "found")

    def test_spotify_display_name_can_differ_from_id(self):
        html = '<title>Different name</title><img data-testid="user-image"><h1 data-testid="entityTitle">Display name</h1>'
        self.assertEqual(self.check(html, site="Spotify", url="https://open.spotify.com/user/alice")["status"], "found")

    def test_svg_titles_do_not_change_page_title(self):
        from social_media.detection import ProfileHTML
        page = ProfileHTML('<title>Alice</title><svg><title>Logo</title></svg>')
        self.assertEqual(page.title, "Alice")

    def test_post_headings_do_not_mean_account_is_missing(self):
        html = '<h2>My account does not exist</h2><meta property="profile:username" content="alice">'
        self.assertEqual(self.check(html)["status"], "found")

    def test_snapchat_profile_redirect(self):
        html = '<title>@alice</title><meta property="og:url" content="https://www.snapchat.com/@alice">'
        self.assertEqual(self.check(html, site="Snapchat", url="https://snapchat.com/add/alice", final_url="https://www.snapchat.com/@alice")["status"], "found")

    def test_vk_domain_redirect_and_profile_data(self):
        html = '<div class="Profile ProfileBase"></div><script>{"domain":"alice"}</script>'
        self.assertEqual(self.check(html, site="VK", url="https://vk.com/alice", final_url="https://vk.ru/alice")["status"], "found")
        self.assertEqual(self.check(html.replace('"domain":"alice"', '"domain":"bob"'), site="VK", url="https://vk.com/alice", final_url="https://vk.ru/alice")["status"], "unknown")

    def test_artstation_client_side_not_found(self):
        self.assertEqual(self.check('<title>ArtStation - Oops! 404 Error</title>', site="ArtStation", url="https://artstation.com/alice", final_url="https://www.artstation.com/404")["status"], "not_found")

    def test_tiktok_embedded_profile(self):
        import json
        detail = {"statusCode": 0, "userInfo": {"user": {"id": "123", "uniqueId": "alice"}}}
        data = json.dumps({"__DEFAULT_SCOPE__": {"webapp.user-detail": detail}})
        html = f'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">{data}</script>'
        self.assertEqual(self.check(html, site="TikTok", url="https://tiktok.com/@alice")["status"], "found")
        self.assertEqual(self.check(html.replace('"alice"', '"bob"'), site="TikTok", url="https://tiktok.com/@alice")["status"], "unknown")

    def test_tiktok_embedded_missing_profile(self):
        html = '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">{"__DEFAULT_SCOPE__":{"webapp.user-detail":{"statusCode":10221}}}</script>'
        self.assertEqual(self.check(html, site="TikTok", url="https://tiktok.com/@alice")["status"], "not_found")

    def test_tiktok_bad_embedded_data(self):
        for data in ("{invalid", "null", '[]', '{"__DEFAULT_SCOPE__":{"webapp.user-detail":null}}'):
            html = f'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">{data}</script>'
            self.assertEqual(self.check(html, site="TikTok", url="https://tiktok.com/@alice")["status"], "unknown")

    def test_vsco_gallery_redirect(self):
        html = '<meta property="og:title" content="Alice (@alice)"><meta property="og:url" content="https://vsco.co/alice/gallery">'
        self.assertEqual(self.check(html, site="VSCO", url="https://vsco.co/alice", final_url="https://vsco.co/alice/gallery")["status"], "found")

    def test_goodreads_redirect_requires_matching_username(self):
        html = '<meta property="profile:username" content="alice">'
        final_url = "https://www.goodreads.com/user/show/123-name"
        self.assertEqual(self.check(html, site="Goodreads", url="https://goodreads.com/alice", final_url=final_url)["status"], "found")
        self.assertEqual(self.check(html.replace("alice", "bob"), site="Goodreads", url="https://goodreads.com/alice", final_url=final_url)["status"], "unknown")


class APITests(unittest.IsolatedAsyncioTestCase):
    async def check(self, site, payload=None, code=200, text=None):
        def respond(request):
            if text is not None:
                return httpx.Response(code, text=text)
            return httpx.Response(code, json=payload)
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            return await site_checker(client, None, site, "https://example.com/{username}", "alice")

    async def test_matching_api_profiles(self):
        fixtures = {
            "Github": {"login": "Alice", "id": 1},
            "GitLab": [{"username": "alice", "id": 1}],
            "Mastodon": {"acct": "alice", "id": "1"},
            "Chess.com": {"username": "alice", "player_id": 1},
            "Mixcloud": {"username": "alice", "key": "/alice/"},
            "Dev.to": {"username": "alice", "id": 1},
            "DockerHub": {"orgname": "alice", "id": "1"},
            "HackerRank": {"model": {"username": "alice", "id": 1}},
            "Instagram": {"data": {"user": {"username": "alice", "id": "1"}}},
            "X": {"user": {"screen_name": "alice", "id": "1"}},
            "TikTok": {"type": "rich", "author_url": "https://www.tiktok.com/@alice", "html": "<blockquote></blockquote>"},
            "Roblox": {"data": [{"name": "alice", "id": 42}]},
            "Wikipedia": {"query": {"users": [{"name": "Alice", "userid": 1}]}},
        }
        for site, payload in fixtures.items():
            with self.subTest(site=site):
                self.assertEqual((await self.check(site, payload))["status"], "found")

    async def test_api_html_does_not_count_as_profile(self):
        for site in ("Github", "Instagram", "X", "Roblox", "HackerRank", "TikTok"):
            with self.subTest(site=site):
                self.assertEqual((await self.check(site, text="<title>Log in</title>"))["status"], "unknown")

    async def test_wrong_account_is_not_found(self):
        self.assertEqual((await self.check("Github", {"login": "bob", "id": 1}))["status"], "unknown")

    async def test_bad_shapes_do_not_crash(self):
        for payload in (None, [], "hello", {"data": None}, {"data": "text"}, {"data": [None]}):
            for site in ("Instagram", "Roblox", "Wikipedia", "X"):
                with self.subTest(site=site, payload=payload):
                    self.assertEqual((await self.check(site, payload))["status"], "unknown")

    async def test_twitch_only_accepts_numeric_id(self):
        self.assertEqual((await self.check("Twitch", text="12345"))["status"], "found")
        self.assertEqual((await self.check("Twitch", text="Service unavailable"))["status"], "unknown")
        self.assertEqual((await self.check("Twitch", text="User not found: alice"))["status"], "not_found")

    async def test_tiktok_bad_request_is_not_missing(self):
        self.assertEqual((await self.check("TikTok", {"message": "Something went wrong"}, code=400))["status"], "unknown")

    async def test_wikipedia_account_without_user_page(self):
        data = {"query": {"users": [{"name": "Alice", "userid": 42}]}}
        self.assertEqual((await self.check("Wikipedia", data))["status"], "found")
        self.assertEqual((await self.check("Wikipedia", {"query": {"users": [{"name": "Alice", "missing": ""}]}}))["status"], "not_found")

    async def test_roblox_returns_numeric_profile_url(self):
        verdict = await self.check("Roblox", {"data": [{"name": "alice", "id": 42}]})
        self.assertEqual(verdict["url"], "https://www.roblox.com/users/42/profile")

    async def test_network_failure_is_unknown(self):
        client = AsyncMock()
        client.get.side_effect = httpx.ConnectError("offline")
        verdict = await site_checker(client, None, "Github", "https://github.com/{username}", "alice")
        self.assertEqual(verdict["status"], "unknown")

    async def test_cancel_is_not_swallowed(self):
        client = AsyncMock()
        client.get.side_effect = asyncio.CancelledError
        with self.assertRaises(asyncio.CancelledError):
            await site_checker(client, None, "Github", "https://github.com/{username}", "alice")

    async def test_scanner_does_not_start_browser_for_http_only(self):
        with patch("Horus.async_playwright") as browser, patch("Horus.site_checker", new_callable=AsyncMock) as checker:
            checker.return_value = {"site": "Github", "Found": True, "status": "found"}
            results = await site_scanner("alice", {"Github": "https://github.com/{username}"})
            self.assertEqual(len(results), 1)
            browser.assert_not_called()

    async def test_invalid_username_is_rejected_before_network(self):
        for username in ("../admin", "alice?x=1", "", "-alice", "a" * 101):
            with self.assertRaises(ValueError):
                await site_scanner(username, {})

    async def test_progress_callback_runs_after_each_site(self):
        callback = Mock()
        with patch("Horus.site_checker", new_callable=AsyncMock, return_value={"status": "not_found"}):
            await site_scanner("alice", {"Github": "https://github.com/{username}", "GitLab": "https://gitlab.com/{username}"}, callback)
        self.assertEqual(callback.call_count, 2)

    async def test_browser_cleanup_when_page_creation_fails(self):
        from playwright.async_api import Error
        context = AsyncMock()
        context.new_page.side_effect = Error("page unavailable")
        with patch("social_media.browser.new_stealth_context", AsyncMock(return_value=context)):
            verdict = await check_browser(object(), "Steam", "https://steamcommunity.com/id/alice")
        context.close.assert_awaited_once()
        self.assertEqual(verdict["status"], "unknown")

    async def test_browser_cleanup_on_cancellation(self):
        context = AsyncMock()
        context.new_page.side_effect = asyncio.CancelledError
        with patch("social_media.browser.new_stealth_context", AsyncMock(return_value=context)):
            with self.assertRaises(asyncio.CancelledError):
                await check_browser(object(), "Steam", "https://steamcommunity.com/id/alice")
        context.close.assert_awaited_once()


class SocialFallbackTests(unittest.IsolatedAsyncioTestCase):
    async def run_check(self, primary, fallback=None, site="Instagram", browser=True):
        from social_media.social import check_social
        browser_check = AsyncMock(return_value=fallback)
        api_check = AsyncMock(return_value=primary)
        with patch("social_media.social.check_api", api_check), patch("social_media.social.check_browser", browser_check):
            verdict = await check_social(AsyncMock(), object() if browser else None, site, "https://example.com/alice", "alice")
        return verdict, browser_check

    async def test_blocked_api_uses_public_profile(self):
        primary = {"status": "blocked", "Found": False, "error": "Access blocked (HTTP 401)"}
        fallback = {"status": "found", "Found": True}
        verdict, browser = await self.run_check(primary, fallback)
        self.assertEqual(verdict, fallback)
        browser.assert_awaited_once()

    async def test_unknown_api_uses_public_profile(self):
        fallback = {"status": "not_found", "Found": False}
        verdict, browser = await self.run_check({"status": "unknown"}, fallback, site="TikTok")
        self.assertEqual(verdict, fallback)
        browser.assert_awaited_once()

    async def test_definitive_result_does_not_repeat_request(self):
        for status in ("found", "not_found"):
            verdict, browser = await self.run_check({"status": status})
            self.assertEqual(verdict["status"], status)
            browser.assert_not_awaited()

    async def test_rate_limit_is_not_retried(self):
        primary = {"status": "blocked", "error": "Access blocked (HTTP 429)"}
        verdict, browser = await self.run_check(primary)
        self.assertEqual(verdict, primary)
        browser.assert_not_awaited()

    async def test_block_reason_survives_inconclusive_browser(self):
        primary = {"status": "blocked", "error": "Access blocked (HTTP 401)"}
        verdict, browser = await self.run_check(primary, {"status": "unknown"})
        self.assertEqual(verdict, primary)

    async def test_missing_browser_preserves_primary(self):
        primary = {"status": "blocked", "error": "Access blocked (HTTP 401)"}
        verdict, browser = await self.run_check(primary, browser=False)
        self.assertEqual(verdict, primary)
        browser.assert_not_awaited()

    async def test_pinterest_html_challenge_uses_browser(self):
        from social_media.social import check_social
        client = AsyncMock()
        client.get.return_value = httpx.Response(403, request=httpx.Request("GET", "https://pinterest.com/alice"))
        fallback = {"status": "found", "Found": True}
        with patch("social_media.social.check_browser", AsyncMock(return_value=fallback)) as browser:
            verdict = await check_social(client, object(), "Pinterest", "https://pinterest.com/alice", "alice")
        self.assertEqual(verdict, fallback)
        browser.assert_awaited_once()

    async def test_network_failure_uses_browser(self):
        from social_media.social import check_social
        with patch("social_media.social.check_api", AsyncMock(side_effect=httpx.ConnectError("offline"))), patch("social_media.social.check_browser", AsyncMock(return_value={"status": "found"})):
            verdict = await check_social(AsyncMock(), object(), "X", "https://x.com/alice", "alice")
        self.assertEqual(verdict["status"], "found")

    async def test_social_only_scan_initializes_fallback_browser(self):
        from unittest.mock import MagicMock
        manager = MagicMock()
        manager.__aenter__ = AsyncMock(return_value=object())
        manager.__aexit__ = AsyncMock(return_value=False)
        browser = AsyncMock()
        with patch("Horus.async_playwright", return_value=manager), patch("Horus.launch_browser", AsyncMock(return_value=browser)), patch("Horus.get_browser_ua", AsyncMock(return_value="Horus test")), patch("Horus.check_social", AsyncMock(return_value={"status": "found"})) as checker:
            verdicts = await site_scanner("alice", {"Instagram": "https://instagram.com/{username}"})
        self.assertEqual(verdicts, [{"status": "found"}])
        self.assertIs(checker.await_args.args[1], browser)
        browser.close.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
