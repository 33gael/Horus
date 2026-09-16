from urllib.parse import quote, urlsplit

from social_media.detection import http_result, result, same_profile, unknown


API_SITES = {
    "Github", "GitLab", "Dev.to", "Mastodon", "DockerHub", "Chess.com",
    "Mixcloud", "HackerRank", "Instagram", "X", "TikTok", "Twitch", "Roblox",
    "Wikipedia", "Wikipedia (FR)",
}


async def check_api(client, site, url, username):
    name = quote(username, safe="")
    endpoints = {
        "Github": f"https://api.github.com/users/{name}",
        "GitLab": "https://gitlab.com/api/v4/users",
        "Dev.to": "https://dev.to/api/users/by_username",
        "Mastodon": "https://mastodon.social/api/v1/accounts/lookup",
        "DockerHub": f"https://hub.docker.com/v2/users/{name}/",
        "Chess.com": f"https://api.chess.com/pub/player/{name}",
        "Mixcloud": f"https://api.mixcloud.com/{name}/",
        "HackerRank": f"https://www.hackerrank.com/rest/contests/master/hackers/{name}/profile",
        "Instagram": "https://www.instagram.com/api/v1/users/web_profile_info/",
        "X": f"https://api.fxtwitter.com/{name}",
        "TikTok": "https://www.tiktok.com/oembed",
        "Twitch": f"https://decapi.me/twitch/id/{name}",
        "Roblox": "https://users.roblox.com/v1/usernames/users",
    }
    params = {
        "GitLab": {"username": username},
        "Dev.to": {"url": username},
        "Mastodon": {"acct": username},
        "Instagram": {"username": username},
        "TikTok": {"url": f"https://www.tiktok.com/@{name}"},
    }.get(site, {})
    headers = {"Accept": "application/json"}
    if site == "Instagram":
        headers["X-IG-App-ID"] = "936619743392459"
    if site.startswith("Wikipedia"):
        endpoint = f"https://{urlsplit(url).hostname}/w/api.php"
        params = {"action": "query", "list": "users", "ususers": username, "format": "json"}
        headers["User-Agent"] = "Horus/1.0 (https://github.com/33gael/Horus; public username lookup)"
    else:
        endpoint = endpoints[site]
    if site == "Roblox":
        response = await client.post(endpoint, json={"usernames": [username], "excludeBannedUsers": False}, headers=headers)
    else:
        response = await client.get(endpoint, params=params, headers=headers)
    verdict = http_result(site, url, response.status_code)
    if verdict:
        return verdict
    if site == "Twitch":
        value = response.text.strip()
        if value.isascii() and value.isdigit() and int(value) > 0:
            return result(site, url, "found")
        if value.casefold() in ("user not found", f'user "{username}" not found'.casefold(), f"user not found: {username}".casefold()):
            return result(site, url, "not_found")
        return unknown(site, url, "Unexpected response from Twitch lookup")
    try:
        data = response.json()
    except ValueError:
        return unknown(site, url, "Expected JSON, received a different response")
    if site == "GitLab":
        if isinstance(data, list):
            if not data:
                return result(site, url, "not_found")
            if any(isinstance(user, dict) and str(user.get("username", "")).casefold() == username.casefold() and user.get("id") for user in data):
                return result(site, url, "found")
        return unknown(site, url, "Unexpected GitLab response")
    if not isinstance(data, dict):
        return unknown(site, url, "Unexpected API response structure")
    if site.startswith("Wikipedia"):
        query = data.get("query")
        users = query.get("users") if isinstance(query, dict) else None
        if isinstance(users, list) and len(users) == 1 and isinstance(users[0], dict):
            user = users[0]
            if "missing" in user or "invalid" in user:
                return result(site, url, "not_found")
            if user.get("userid") and str(user.get("name", "")).replace("_", " ").casefold() == username.replace("_", " ").casefold():
                return result(site, url, "found")
        return unknown(site, url, "Unexpected MediaWiki response")
    if site == "Roblox":
        users = data.get("data")
        if users == []:
            return result(site, url, "not_found")
        if isinstance(users, list):
            for user in users:
                if isinstance(user, dict) and str(user.get("requestedUsername", user.get("name", ""))).casefold() == username.casefold() and isinstance(user.get("id"), int) and user["id"] > 0:
                    return result(site, f"https://www.roblox.com/users/{user['id']}/profile", "found")
        return unknown(site, url, "Unexpected Roblox response")
    if site == "TikTok":
        if data.get("type") == "rich" and same_profile(str(data.get("author_url", "")), f"https://www.tiktok.com/@{name}") and data.get("html"):
            return result(site, url, "found")
        return unknown(site, url, "TikTok did not return a matching creator profile")
    fields = {
        "Github": ("login", "id"), "Dev.to": ("username", "id"),
        "Mastodon": ("acct", "id"), "DockerHub": ("username", "id"),
        "Chess.com": ("username", "player_id"), "Mixcloud": ("username", "key"),
        "HackerRank": ("username", "id"), "Instagram": ("username", "id"),
        "X": ("screen_name", "id"),
    }
    if site == "Instagram":
        payload = data.get("data")
        data = payload.get("user") if isinstance(payload, dict) else None
    elif site == "HackerRank":
        data = data.get("model")
    elif site == "X":
        if data.get("code") == 404:
            return result(site, url, "not_found")
        data = data.get("user")
    identity, identifier = fields[site]
    if site == "DockerHub" and isinstance(data, dict) and "orgname" in data:
        identity = "orgname"
    if isinstance(data, dict) and str(data.get(identity, "")).casefold() == username.casefold() and data.get(identifier):
        return result(site, url, "found")
    return unknown(site, url, "API did not return a matching profile")
