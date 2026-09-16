# Graph Report - src  (2026-09-16)

## Corpus Check
- 12 files · ~4,309 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 118 nodes · 260 edges · 11 communities (6 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8af1f0ee`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Horus.py
- .render
- site_scanner
- .check
- check_browser
- inspect_profile
- ProfileHTML
- check_social
- APITests
- Q: Quel username a le plus de hits avec Horus parmi 33gael, gael, horus, github et youtube ?

## God Nodes (most connected - your core abstractions)
1. `PageDetectionTests` - 26 edges
2. `inspect_profile()` - 18 edges
3. `APITests` - 17 edges
4. `check_browser()` - 15 edges
5. `unknown()` - 14 edges
6. `site_checker()` - 11 edges
7. `check_social()` - 11 edges
8. `SocialFallbackTests` - 11 edges
9. `site_scanner()` - 10 edges
10. `ProfileHTML` - 10 edges

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

## Communities (11 total, 4 thin omitted)

### Community 0 - "Horus.py"
Cohesion: 0.55
Nodes (6): check_api(), detect_profile(), http_result(), result(), same_profile(), unknown()

### Community 1 - ".render"
Cohesion: 0.24
Nodes (4): Console, get_valid_username(), print_result(), ResultDisplayTests

### Community 2 - "site_scanner"
Cohesion: 0.23
Nodes (7): Browser, BrowserContext, site_scanner(), check(), get_browser_ua(), launch_browser(), new_stealth_context()

### Community 4 - "check_browser"
Cohesion: 0.20
Nodes (3): site_checker(), check_browser(), BrowserNavigationTests

### Community 5 - "inspect_profile"
Cohesion: 0.29
Nodes (3): inspect_profile(), navigation_result(), NavigationTests

### Community 9 - "Q: Quel username a le plus de hits avec Horus parmi 33gael, gael, horus, github et youtube ?"
Cohesion: 0.50
Nodes (3): Answer, Q: Quel username a le plus de hits avec Horus parmi 33gael, gael, horus, github et youtube ?, Source Nodes

## Knowledge Gaps
- **2 isolated node(s):** `Answer`, `Source Nodes`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 13 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PageDetectionTests` connect `.check` to `check_browser`, `inspect_profile`, `ProfileHTML`?**
  _High betweenness centrality (0.190) - this node is a cross-community bridge._
- **Why does `site_checker()` connect `check_browser` to `Horus.py`, `site_scanner`, `.check`, `inspect_profile`, `check_social`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Why does `inspect_profile()` connect `inspect_profile` to `Horus.py`, `check_browser`, `check_social`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **What connects `Answer`, `Source Nodes` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._