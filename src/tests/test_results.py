import io
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from rich.console import Console

from main import print_result
from social_media.browser import check_browser
from social_media.detection import inspect_profile, navigation_result, unknown


class NavigationTests(unittest.TestCase):
    def test_verified_redirect_uses_final_profile(self):
        requested = "https://pixabay.com/users/alice"
        final = "https://pixabay.com/users/alice-123/"
        html = '<h1>Alice</h1><div class="userInfo--abc"></div>'
        verdict = inspect_profile("Pixabay", requested, final, 200, html, "alice")
        self.assertEqual(verdict["status"], "found")
        self.assertEqual(verdict["url"], final)
        self.assertEqual(verdict["requested_url"], requested)

    def test_home_redirect_remains_unverified(self):
        requested = "https://ko-fi.com/alice"
        verdict = inspect_profile("Ko-fi", requested, "https://ko-fi.com/", 200, "<title>Ko-fi</title>", "alice")
        self.assertEqual(verdict["status"], "unknown")
        self.assertEqual(verdict["url"], requested)
        self.assertEqual(verdict["final_url"], "https://ko-fi.com/")

    def test_login_redirect_excludes_query_and_fragment(self):
        verdict = inspect_profile("LinkedIn", "https://linkedin.com/in/alice", "https://linkedin.com/login?tracking=123#extra", 200, "", "alice")
        self.assertEqual(verdict["status"], "blocked")
        self.assertEqual(verdict["final_url"], "https://linkedin.com/login")

    def test_challenge_redirect_is_blocked(self):
        for destination in ("https://vk.ru/challenge.html", "https://unsplash.com/.within.website?redir=/@alice"):
            verdict = inspect_profile("VK", "https://vk.com/alice", destination, 200, "", "alice")
            self.assertEqual(verdict["status"], "blocked")
            self.assertIn("final_url", verdict)

    def test_unexpected_status_can_contain_challenge(self):
        verdict = inspect_profile("Last.fm", "https://last.fm/user/alice", "https://last.fm/user/alice", 600, "<title>Client Challenge</title>", "alice")
        self.assertEqual(verdict["status"], "blocked")

    def test_invalid_redirect_links_are_not_recorded(self):
        for destination in ("javascript:alert(1)", "file:///tmp/page", "https://user:password@example.com/", "https://example.com/\x1b", "https://["):
            verdict = navigation_result(unknown("Test", "https://example.com/alice"), "https://example.com/alice", destination)
            self.assertNotIn("final_url", verdict)

    def test_canonical_patterns_do_not_accept_other_domains(self):
        cases = (("Pixabay", "/users/alice-123/"), ("Patreon", "/cw/alice"), ("Goodreads", "/user/show/123-alice"))
        for site, path in cases:
            html = '<meta property="profile:username" content="alice"><h1>Alice</h1><div class="userInfo--abc"></div>'
            verdict = inspect_profile(site, "https://example.com/alice", "https://unrelated.example" + path, 200, html, "alice")
            self.assertEqual(verdict["status"], "unknown")


class ResultDisplayTests(unittest.TestCase):
    def render(self, verdict, terminal=False):
        stream = io.StringIO()
        console = Console(file=stream, width=240, force_terminal=terminal, color_system="standard" if terminal else None)
        print_result(console, verdict)
        return stream.getvalue()

    def test_blocked_result_has_no_link(self):
        verdict = {"site": "Reddit", "Found": False, "status": "blocked", "error": "Access denied", "url": "https://reddit.com/user/alice"}
        output = self.render(verdict, terminal=True)
        self.assertNotIn("Check manually", output)
        self.assertNotIn("\x1b]8;", output)
        self.assertNotIn("https://reddit.com/user/alice", output)

    def test_error_redirect_has_no_link(self):
        verdict = {"site": "Ko-fi", "Found": False, "status": "unknown", "url": "https://ko-fi.com/alice", "final_url": "https://ko-fi.com/"}
        output = self.render(verdict)
        self.assertNotIn("Check manually", output)
        self.assertNotIn("Redirected to", output)
        self.assertNotIn("https://", output)

    def test_verified_profile_link_is_not_duplicated(self):
        verdict = {"site": "Pixabay", "Found": True, "status": "found", "url": "https://pixabay.com/users/alice-123/", "final_url": "https://pixabay.com/users/alice-123/"}
        output = self.render(verdict)
        self.assertEqual(output.count(verdict["url"]), 1)
        self.assertNotIn("Check manually", output)
        self.assertEqual(output, "[+] - Username found in Pixabay : https://pixabay.com/users/alice-123/\n")

    def test_facebook_and_linkedin_keep_original_link(self):
        for site, url in (("Facebook", "https://facebook.com/alice"), ("LinkedIn", "https://linkedin.com/in/alice")):
            output = self.render({"site": site, "Found": True, "status": "found", "requested_url": url, "url": "https://example.com/destination", "final_url": "https://example.com/destination"})
            self.assertEqual(output, f"[+] - Username found in {site} : {url}\n")

    def test_unverified_facebook_is_not_a_hit(self):
        output = self.render({"site": "Facebook", "Found": False, "status": "unknown", "url": "https://facebook.com/alice", "final_url": "https://facebook.com/login"})
        self.assertIn("Unable to verify Facebook", output)
        self.assertNotIn("https://facebook.com/alice", output)
        self.assertNotIn("Username found", output)
        self.assertNotIn("/login", output)

    def test_missing_profile_is_not_presented_as_found(self):
        verdict = {"site": "Test", "Found": False, "status": "not_found", "url": "https://example.com/alice"}
        output = self.render(verdict)
        self.assertIn("Username not found", output)
        self.assertNotIn("Profile:", output)

    def test_error_markup_is_rendered_literally(self):
        output = self.render({"site": "Test", "status": "unknown", "error": "[red]failure[/red]"})
        self.assertIn("[red]failure[/red]", output)

    def test_unsafe_links_are_not_rendered(self):
        output = self.render({"site": "Test", "status": "unknown", "url": "javascript:alert(1)", "final_url": "https://user:password@example.com/"})
        self.assertNotIn("javascript:", output)
        self.assertNotIn("password", output)


class BrowserNavigationTests(unittest.IsolatedAsyncioTestCase):
    async def test_document_status_is_updated_after_navigation(self):
        page = MagicMock()
        page.url = "https://last.fm/user/alice"
        first_response = MagicMock(status=600)
        page.goto = AsyncMock(return_value=first_response)
        page.content = AsyncMock(side_effect=['<title>Client Challenge</title>', '<title>Alice</title><meta property="profile:username" content="alice">'])
        context = AsyncMock()
        context.new_page.return_value = page

        async def navigate(delay):
            response = MagicMock(status=200)
            response.request.is_navigation_request.return_value = True
            response.frame = page.main_frame
            page.on.call_args.args[1](response)

        with patch("social_media.browser.new_stealth_context", AsyncMock(return_value=context)), patch("social_media.browser.asyncio.sleep", side_effect=navigate):
            verdict = await check_browser(object(), "Last.fm", page.url, "alice")
        self.assertEqual(verdict["status"], "found")
        context.close.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
