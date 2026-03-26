# Project Task List: Hugo Blog Build (v2)

- [x] Phase 0: Discovery, Safety, and Roadmap
    - [x] Environment check: `hugo v0.159.1+extended`, `git 2.50.1`, `python3.14.3`.
    - [x] All 4 specs loaded: architecture.md, design.md, automation.md, content.md.
    - [x] Cloudflare Analytics token verified: `c4d654ab4e2542b2a78b1de0562111ad`.
    - [x] Secrets confirmed: `GEMINI_API_KEY`, `NTFY_TOPIC`.
- [x] Phase 1: Scaffolding & Core Architecture
    - [x] config.yaml with output formats (HTML, RSS, llms, llmsfull, markdown).
    - [x] All layouts: baseof, list, single, single.md (raw Markdown output).
    - [x] All partials: head, header, footer, analytics, social-share, post-meta.
    - [x] Shortcodes: callout (note/warning/tip), video (16:9 responsive).
    - [x] LLMS templates: index.llms.txt, index.llmsfull.txt.
    - [x] Content: about.md, hello-world.md, first-retrospective.md (with callouts).
    - [x] `hugo --minify` clean: 29 pages, 0 errors.
- [x] Phase 2: Design "Calm Signal" & CSS
    - [x] Full CSS rewrite: CSS variables, light/dark mode, smooth transitions.
    - [x] Glassmorphism: backdrop-filter blur(8px) on callouts and code blocks.
    - [x] Lessons Learned visual badge for retrospective posts.
    - [x] Image render hook: loading="lazy" decoding="async" on all markdown images.
    - [x] Mobile 375px: no horizontal scroll, responsive typography.
    - [x] WCAG 2.1 AA contrast verified analytically.
- [x] Phase 3: SEO, Agent Accessibility, and Structured Output
    - [x] llms.txt and llms-full.txt generating correctly (raw Markdown, no entities).
    - [x] Per-post /posts/[slug]/index.md: 200 OK for both posts.
    - [x] JSON-LD: Article, Person, BreadcrumbList — all parse as valid JSON.
    - [x] Speculation Rules API in <head>.
    - [x] Cloudflare Analytics beacon (conditional on cloudflare_token param).
    - [x] Skip-to-content link present on all pages.
- [x] Phase 4: CI/CD & AI Automation
    - [x] deploy.yml: peaceiris/actions-hugo@v3 + peaceiris/actions-gh-pages@v4, CNAME, meta-log.
    - [x] content-automation.yml: PR-triggered, python3.14, commit-back write permissions.
    - [x] maintenance.yml: Friday social loop (cron 0 15 * * 5) + 3-week freshness audit.
    - [x] content_automation.py: syntax-checked with python3.14 -m py_compile.
    - [x] Dry-run mode: validates production context, reports changed posts, no API calls.
    - [x] Graceful failure: opens GitHub Issue, posts PR comment, never fails build (sys.exit 0).
    - [x] Atomic frontmatter: temp-file rename pattern.

## COMPLETE — All 4 phases shipped. Branch: new-blog.
