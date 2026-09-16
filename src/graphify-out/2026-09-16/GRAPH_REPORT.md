# Graph Report - src  (2026-09-16)

## Corpus Check
- 29 files · ~4,508 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 150 nodes · 329 edges · 8 communities (4 shown, 3 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8af1f0ee`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- check_api
- .render
- check_browser
- .check
- inspect_profile
- ProfileHTML
- check_social

## God Nodes (most connected - your core abstractions)
1. `check_browser()` - 29 edges
2. `PageDetectionTests` - 26 edges
3. `check_api()` - 25 edges
4. `inspect_profile()` - 24 edges
5. `APITests` - 17 edges
6. `unknown()` - 14 edges
7. `site_checker()` - 11 edges
8. `check_social()` - 11 edges
9. `SocialFallbackTests` - 11 edges
10. `site_scanner()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `PageDetectionTests` --uses--> `ProfileHTML`  [INFERRED]
  tests/test_scraping.py → social_media/detection.py
- `site_checker()` --calls--> `check_api()`  [EXTRACTED]
  Horus.py → social_media/api.py
- `site_checker()` --calls--> `inspect_profile()`  [EXTRACTED]
  Horus.py → social_media/detection.py
- `site_checker()` --calls--> `unknown()`  [EXTRACTED]
  Horus.py → social_media/detection.py
- `site_checker()` --calls--> `check_social()`  [EXTRACTED]
  Horus.py → social_media/social.py

## Import Cycles
- None detected.

## Communities (8 total, 3 thin omitted)

### Community 0 - "check_api"
Cohesion: 0.18
Nodes (14): check_api(), ft_chess(), detect_profile(), http_result(), result(), same_profile(), unknown(), ft_hackerrank() (+6 more)

### Community 1 - ".render"
Cohesion: 0.26
Nodes (4): Console, get_valid_username(), print_result(), ResultDisplayTests

### Community 2 - "check_browser"
Cohesion: 0.12
Nodes (16): Browser, BrowserContext, site_checker(), site_scanner(), check(), check_browser(), ft_facebook(), ft_playstation() (+8 more)

### Community 5 - "inspect_profile"
Cohesion: 0.15
Nodes (7): inspect_profile(), navigation_result(), ft_linkedin(), ft_pinterest(), ft_youtube(), BrowserNavigationTests, NavigationTests

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `check_browser()` connect `check_browser` to `check_api`, `inspect_profile`, `check_social`?**
  _High betweenness centrality (0.226) - this node is a cross-community bridge._
- **Why does `site_checker()` connect `check_browser` to `check_api`, `.check`, `inspect_profile`, `check_social`?**
  _High betweenness centrality (0.175) - this node is a cross-community bridge._
- **Why does `check_api()` connect `check_api` to `check_browser`, `check_social`?**
  _High betweenness centrality (0.174) - this node is a cross-community bridge._
- **Should `check_browser` be split into smaller, more focused modules?**
  _Cohesion score 0.12121212121212122 - nodes in this community are weakly interconnected._
- **Should `.check` be split into smaller, more focused modules?**
  _Cohesion score 0.09759759759759759 - nodes in this community are weakly interconnected._
- **Should `inspect_profile` be split into smaller, more focused modules?**
  _Cohesion score 0.14761904761904762 - nodes in this community are weakly interconnected._