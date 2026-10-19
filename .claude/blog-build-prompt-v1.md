# Claude Code Prompt: Personal Blog — Hugo + GitHub Pages

## Your Role

You are acting as a **senior engineer and marketing designer** with deep expertise in:
- Static site architecture and Hugo
- Developer-focused design systems
- SEO and structured content
- GitOps workflows and GitHub Actions
- AI/agent-accessible content design

The audience for this blog is **CTOs, tech enthusiasts, and engineers**. Design and engineering decisions must reflect that — no hand-holding, no bloat, no noise. Every choice should be intentional.

---

## Context & References

The following resources serve as the primary source of truth for the author's identity and design preferences. Leverage these to understand the brand's aesthetic and technical focus. The author is a **Technical Outcome Leader** building at the intersection of multi-cloud engineering (GCP, AWS, Azure), AI agents, and serverless patterns.

- **Current Blog:** [SRVRLSS.DEV](https://srvrlss.dev/)
- **GitHub Profile:** [Alexandre Brisebois](https://github.com/AlexandreBrisebois)
- **LinkedIn Profile:** [Alexandre Brisebois](https://www.linkedin.com/in/alexandrebrisebois/)
- **Docker Hub:** [brisebois](https://hub.docker.com/u/brisebois)
- **Blog Source Repository:** [AlexandreBrisebois.github.io](https://github.com/AlexandreBrisebois/AlexandreBrisebois.github.io)
- **Bluesky:** [Alexandre Brisebois](https://bsky.app/profile/alexandrebrisebois.bsky.social)

---

## Project Goal

Build a **complete, production-ready Hugo blog** hosted on GitHub Pages. This is a personal blog for reflection, experimentation, learning, failure, and retrospectives. The blog is the author's thinking space — raw, honest, technical.

Start from zero. No existing codebase. Build everything from scratch.

---

## Technical Stack

- **Static site engine:** Hugo (latest stable)
- **Hosting:** GitHub Pages (deploy via `gh-pages` branch)
- **CI/CD:** GitHub Actions (build + deploy on push to `main`)
- **Content format:** Markdown (`.md`) with YAML frontmatter
- **AI Integration:** Google Gemini 3.1 Flash (`gemini-3.1-flash`) and **Nano Banana 2** (`nano-banana-2`) via GitHub Actions for metadata and visual automation.
- **No JavaScript frameworks.** No React, no Vue, no MDX. Hugo shortcodes for rich content only.
- **No heavy CSS frameworks.** Write clean, custom CSS. No Bootstrap, no Tailwind CDN.

---

## Repository Structure

Scaffold the following structure completely:

```
/
├── .github/
│   └── workflows/
│       └── deploy.yml          ← Build + deploy to GitHub Pages
├── archetypes/
│   └── default.md              ← Post template with full frontmatter
├── content/
│   ├── about.md                ← Bio/Professional profile
│   └── posts/
│       ├── hello-world.md      ← Sample post: "Why I built this blog"
│       └── first-retrospective.md ← Sample post: a fake retrospective
├── layouts/
│   ├── _default/
│   │   ├── baseof.html
│   │   ├── list.html
│   │   └── single.html
│   ├── index.html              ← Homepage
│   ├── partials/
│   │   ├── head.html           ← Meta, SEO, OG tags, Analytics
│   │   ├── header.html
│   │   ├── footer.html
│   │   ├── post-meta.html
│   │   └── analytics.html      ← Cloudflare Web Analytics snippet
│   └── shortcodes/
│       ├── callout.html        ← For notes/warnings/tips
│       └── video.html          ← For embedded video
├── layouts/
│   ├── _default/
│   │   └── index.llms.txt      ← Hugo template: generates llms.txt at build
│   │   └── index.llms-full.txt ← Hugo template: generates llms-full.txt at build
├── static/
│   └── robots.txt
├── config.yaml                 ← Full Hugo config with SEO and output formats
├── .gitignore
└── README.md
```

---

## Git Configuration (.gitignore)

Create a `.gitignore` file to ensure local build artifacts and environment-specific files are not committed to the repository. The CI/CD pipeline will handle clean builds.

Include the following:
- `public/` (Hugo build output)
- `resources/` (Generated assets)
- `.hugo_build.lock`
- `.DS_Store` (Mac system files)
- `node_modules/` (if any dependencies are added later)

---

## Design Direction

### Aesthetic: "Calm Signal"

The design must feel **calm and energizing** — like reading a well-written internal engineering doc or a thoughtful technical post from someone who respects your time. It should feel **of 2026 but age gracefully** — no trends that will look dated in 18 months.

**Design principles:**
- The design **supports the content**. It must never compete with it.
- Generous whitespace. Content breathes.
- Typography is the primary design element.
- Color is used sparingly — as signal, not decoration.
- No hero sections. No animations on load. No parallax. No carousels.
- Subtle hover states only. Motion is reserved for meaning.

### Typography

Choose a **distinctive, editorial font pairing** appropriate for a technical audience:
- **Display / headings:** `Instrument Serif` (Semi-bold, 600). A strong, contemporary serif with personality.
- **Body text:** `Source Serif 4` (Regular, 400). A highly legible, comfortable reading font optimized for long-form. Body text size: 18–20px with generous line height (1.7–1.8).
- **Monospace / code:** `JetBrains Mono` or `Berkeley Mono`. Inline code and code blocks must be beautifully styled.

Load fonts via Google Fonts or self-hosted — no font rendering jank.

### Color Palette & Dark Mode

Implement a **system-aware dark mode** using `@media (prefers-color-scheme: dark)`. No manual toggle is required. The site must default to the user's system theme.

**Light Mode (Default):**
A warm, editorial palette. Not clinical white — warm or slightly tinted.
```css
--color-bg:        #F7F5F0;   /* warm off-white — like good paper */
--color-surface:   #EFECE5;   /* subtle card/block differentiation */
--color-ink:       #1A1A18;   /* near-black, not pure black */
--color-muted:     #6B6860;   /* secondary text, metadata */
--color-accent:    #2D6A4F;   /* a single calm green — signal, not decoration */
--color-accent-2:  #E76F51;   /* warm coral — used very sparingly for highlights */
--color-border:    #DDD9D0;   /* subtle dividers */
--color-code-bg:   #1E1E1C;   /* dark code blocks — high contrast island */
```

> [!IMPORTANT]
> **Code Block Contrast:** Always use `github-dark` syntax highlighting. In light mode, ensure these dark blocks provide a sharp, professional contrast against the warm-white background, acting as a clear "island" of technical focus that does not clash with the background.

**Dark Mode:**
A "Midnight Tech" palette. High legibility, low strain.
```css
--color-bg:        #0D1117;   /* deep navy/black */
--color-surface:   #161B22;   /* surface differentiation */
--color-ink:       #C9D1D9;   /* soft white text */
--color-muted:     #8B949E;   /* muted metadata */
--color-accent:    #4D9375;   /* slightly brighter green for dark bg */
--color-border:    #30363D;   /* dark dividers */
--color-code-bg:   #0D1117;   /* match bg or slightly darker */
```

This palette should feel like a high-quality printed technical journal. Calm. Professional. Human.

### UI Accents (Glassmorphism & Texture)
Use subtle glassmorphism for **callouts (`{{< callout >}}`) and code blocks**:
- `backdrop-filter: blur(8px) saturate(180%)`
- `background-color: rgba(var(--color-surface-rgb), 0.7)` 
- A 1px border with `rgba(var(--color-border-rgb), 0.3)`
- This adds depth and a "premium" feel while maintaining the "Calm Signal" minimalist baseline.

### Layout

- **Max content width:** 680px centered for post body. 860px for list pages.
- **Mobile-first.** Fully responsive. Phone must feel native — no horizontal scroll, no tiny text, no broken layouts.
- **iPad comfortable.** Reading on iPad is a primary use case.
- **No sidebar.** Single-column content. Navigation is minimal.

### Navigation

Minimal header:
- **Wordmark (left):** A high-impact, CSS-only text wordmark for `srvrlss.dev`. Use `Instrument Serif` with slightly tightened letter-spacing and appropriate weight to feel like a premium editorial mark.
- **Navigation links:** `Writing` · `About` · `RSS` (right)
- The `About` link must point to `/about/`.
- No hamburger menus. On mobile, stack or abbreviate.

Minimal footer:
- Copyright line
- RSS link
- `llms.txt` link (for agents)
- **LinkedIn Follow CTA**: A prominent, minimalist "Follow on LinkedIn" link that encourages the reader to connect with the author's primary social platform. Style it as an authoritative signal, not a noisy button.

### Homepage

The homepage is a **reverse-chronological post list**. No hero. No bio block at the top. Open directly with the **Anchor Statement** followed by posts.

**Anchor Statement:** A single-sentence, high-impact "Statement of Intent" at the very top (e.g., "A thinking space for technical outcomes and lessons learned in the multi-cloud era."). Style it with `Instrument Serif`, sized between a heading and body text, to anchor the site's purpose for new visitors.

Each post in the list shows:
- Title (linked)
- Date
- 1-line description or excerpt
- Tags (optional, minimal)

**"Lessons Learned" Pivot:** Posts in the `retrospective` category or with "Retrospective" in the title must be visually tagged or titled as **"Lessons Learned"**. The narrative should always pivot from "what went wrong" to "what was gained/learned for future technical outcomes."

No post thumbnails. No card shadows. Clean list.

---

## Content & SEO

### Frontmatter Schema (enforce in archetype)

```yaml
---
title: ""
date: YYYY-MM-DDTHH:MM:SS+00:00
description: ""           # Used for meta description and post list excerpt
tags: []                  # e.g. [retrospective, learning, engineering]
draft: false
slug: ""                  # optional override
tldr: ""                  # optional executive summary (2 sentences)
# Social Distribution & Discussion URLs
social_posts:
  linkedin: ""            # Full URL to the active discussion thread
  x: ""                   # Full URL to the X thread
  bluesky: ""             # Full URL to the Bluesky thread
# Bidirectional Context
related_posts: []           # Automatically suggested by Gemini based on llms-full.txt
mentioned_in: []            # Older posts that now link to this one
# AI Traceability
image_prompt: ""            # The exact prompt used to generate the header image
---
```

### SEO Requirements (implement fully)

In `layouts/partials/head.html`, implement:
- `<meta name="description">` from frontmatter
- Open Graph tags: `og:title`, `og:description`, `og:type`, `og:url`, `og:image`
- Twitter Card tags
- Canonical URL
- `<link rel="alternate" type="application/rss+xml">` for RSS discovery
- **Structured Data:** Implement JSON-LD for:
    - **Article schema** (headline, date, description, image).
    - **Person schema** for the author (referencing the bio, including social links).
    - **BreadcrumbList schema** for site hierarchy signals.
- **Performance:** Add **Speculation Rules API** script tag for pre-rendering (making it feel like a single-page app in modern browsers).
- Hugo's built-in sitemap (enable in config).
- **Accessibility:** Add a "Skip to Content" link for accessibility.

### Analytics

In `layouts/partials/analytics.html`, implement the **Cloudflare Web Analytics** beacon.
- **Privacy-First:** Ensure it uses the "JS Snippet" (beacon) method which works even with external DNS (like GoDaddy) and requires no cookies.
- **Conditional Loading:** Only render the script if `params.analytics.cloudflare_token` is set in `config.yaml`.
- **Placement:** Include the `analytics.html` partial at the end of `head.html`.

### RSS Feed

Hugo's built-in RSS. Ensure full content is in the feed (not just summary). Configure in `config.yaml`.

---

## Agent Accessibility (`llms.txt`)

**Do not use a static file or a GitHub Action for this.** Hugo generates `llms.txt` and `llms-full.txt` natively at build time — including during local `hugo server` — so the files are always in sync with published content. No post-processing, no external tools, no secrets needed.

### Hugo Output Formats for `llms.txt`

In `config.yaml`, define two custom output formats and add them to the home outputs:

```yaml
# Output formats
outputFormats:
  llms:
    baseName: "llms"
    isPlainText: true
    mediaType: "text/plain"
    rel: "alternate"
    root: true
  llmsfull:
    baseName: "llms-full"
    isPlainText: true
    mediaType: "text/plain"
    rel: "alternate"
    root: true

outputs:
  home: [HTML, RSS, llms, llmsfull]
  page: [HTML, Markdown]
  section: [HTML, RSS]
```

### `llms.txt` Template

Create `layouts/_default/index.llms.txt`:

```
# {{ .Site.Title }}

> {{ .Site.Params.description }}

## Posts

{{ range (where (sort .Site.RegularPages "Date" "desc") "Draft" "ne" true) -}}
- [{{ .Title }}]({{ .Permalink }}): {{ .Description }}
{{ end }}
## About

This is a personal blog by {{ .Site.Params.author.name }}. Reflections on engineering, building, learning, and failure.

## Feeds

- RSS: {{ .Site.BaseURL }}index.xml
- Sitemap: {{ .Site.BaseURL }}sitemap.xml
- Full content: {{ .Site.BaseURL }}llms-full.txt
```

This renders at `yourdomain.com/llms.txt` on every build, automatically listing every published post with its description.

### `llms-full.txt` Template

Create `layouts/_default/index.llmsfull.txt`. This concatenates the full content of every post into a single file — useful for agents that want to ingest everything at once:

```
# {{ .Site.Title }} — Full Content

> {{ .Site.Params.description }}

---
{{ range (where (sort .Site.RegularPages "Date" "desc") "Draft" "ne" true) }}
# {{ .Title }}

Published: {{ .Date.Format "2006-01-02" }}
URL: {{ .Permalink }}

{{ .Content | plainify }}

---
{{ end }}
```

Renders at `yourdomain.com/llms-full.txt`.

### Markdown Output per Post

Configure Hugo output formats so every post is also available as clean Markdown at:
`/posts/[slug]/index.md`

This allows agents to fetch a post URL with `.md` appended and receive raw, clean content — no HTML, no nav, no noise. Implement this via Hugo's `outputs` config and a `single.md` layout template that renders just the title, date, and content in plain Markdown.

---

## About Page

Create `content/about.md` with a professional bio. This is the only "identity" or "bio" block on the site.

**Bio Requirements:**
- **Voice:** Reflective-vulnerable blended with urgently excited. Use "I" for personal learning and opinions.
- **Content:** Briefly mention the background in multi-cloud engineering (GCP, AWS, Azure), AI agents, and serverless patterns. Reference the "srvrlss.dev" brand as a fresh start.
- **Tone:** Technical Outcome Leader. Senior, authoritative, yet approachable.
- **Formatting:** Clean markdown, 3-4 paragraphs max. Point to LinkedIn and GitHub.

---

## GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Hugo Blog

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true
          fetch-depth: 0

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true

      - name: Build
        run: hugo --minify

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public

---
## AI-Powered Automation Workflow
### 1. PR-Triggered Content Automation (`.github/workflows/generate-metadata.yml`)
Trigger on **`pull_request`** targeting `main`. This workflow must:

1. **Self-Audit**: Ignore commits by "github-actions[bot]".
2. **Contextual Awareness**: Load the latest `llms-full.txt` (from the current live site) as a knowledge base.
3. **Execute Brand Tasks (for each new/modified post)**:
   - **LinkedIn Hooks**: Generate 3 variations of a "Hook" per the Brand Voice story arc.
   - **X Thread Drafting**: Distill into a 3-tweet thread with "Distilled Conviction."
   - **Bluesky Threading**: Distill into a 3-post thread with technical depth for the dev community.
   - **Tag Extraction**: Suggest 3-5 technical tags (e.g., Serverless, AI Agents).
   - **Conditional TLDR**: If `tldr` is empty, generate a 2-sentence "Who is this for?" summary.
   - **Bidirectional Semantic Linking**:
      - Suggest 2-3 "Related Posts" for the *new* post's `related_posts` frontmatter.
      - **Crucial**: Identify 2-3 *older* posts in `llms-full.txt` that should reference this new post. Provide a list of these files and the specific frontmatter update (`mentioned_in`) needed.
   - **Image Generation (Nano Banana 2)**: 
       - Generate a unique, minimalist WebP header image (`static/images/posts/[slug].webp`) using a Gemini-generated prompt.
       - **Image Aesthetic**: Minimalist, technical, high-contrast. No stock-photo humans. Focus on **abstract architectural diagrams, serverless event flows, and high-contrast technical textures** that align with "Calm Signal."
   - **Brand Voice Guardrail (CRITICAL)**: All generated content (LinkedIn hooks, X threads, tags, TLDRs) must strictly avoid the following banned words: `Utilize`, `Deep-dive`, `Game-changing`, `Synergy`, `Very`, `Extremely`, `Robust`, `Additionally`, `Furthermore`, `Moreover`. Use direct, active sentences consistent with srvrlss.dev Brand Voice.
   - **Traceability (CRITICAL)**:
       - Post the full **image generation prompt** as a PR comment so the author can review and iterate.
       - Automatically update the post's frontmatter (`image_prompt`) with this prompt via a Git commit back to the PR branch.
4. **Delivery**: Post all results (LinkedIn hooks, X threads, tags, related posts, and the image prompt) as a grouped PR comment.

### 2. Scheduled Maintenance Workflows (`.github/workflows/maintenance.yml`)

1. **Social Discussion Loop (Private)**:
   - **Trigger**: Every Friday at 15:00 UTC.
   - **Task**: 
     - Use a Node.js or Python script to scan `content/posts/` and sort by `date` desc.
     - Select the last **5 published posts** and extract `linkedin`, `x`, and `bluesky` URLs from the `social_posts` frontmatter.
   - **Action**: Use Gemini to visit each URL (where provided) and summarize the key technical insights and "Discussion Vibe" from the comments across all platforms.
   - **Delivery**: Send a **private push notification** via `ntfy.sh` (e.g., `curl -d "[Summary]" ntfy.sh/${{ secrets.NTFY_TOPIC }}`). *Zero cost, zero setup, private.*

2. **Content Freshness Audit (Internal)**:
   - **Trigger**: Every **3 weeks**.
   - **Task**: Review the entire `llms-full.txt` file.
   - **Action**: Gemini identifies posts that may be suffering from "AI Drift", "Cloud Drift" or "Technical Decay" based on known updates in Cloud providers or AI services or frameworks since the post date.
   - **Delivery**: Open a **GitHub Issue** titled "Content Maintenance: [Date]" with a prioritized list of suggested updates or "Retrospective" follow-ups.

### 3. Site Evolution Meta-Log (Automated)
In the deployment workflow, if changes are detected in `layouts/`, `static/css/`, or `config.yaml`:
   - Use Gemini to summarize the architectural change (e.g., "Updated typography to Lora", "Restructured Agent Accessibility").
   - **Action**: Automatically append this entry to a `/changelog` post or page to maintain the "Maker-honest" narrative.

---
```

---

## Hugo Config (`config.yaml`)

```yaml
baseURL: "https://srvrlss.dev/"  # placeholder
languageCode: "en-us"
title: "srvrlss.dev"                   # placeholder
theme: ""                                 # no external theme — custom layouts only

# Author
author:
  name: "Alexandre Brisebois"

# Permalinks
permalinks:
  posts: /posts/:slug/

# Output formats
outputs:
  home: [HTML, RSS]
  page: [HTML, Markdown]
  section: [HTML, RSS]

# Enable sitemap
sitemap:
  changeFreq: weekly
  priority: 0.5

# RSS full content
params:
  rssFullContent: true
  description: "A blog about learning, building and deploying things."
  # Analytics
  analytics:
    cloudflare_token: "c4d654ab4e2542b2a78b1de0562111ad"  # Add your Cloudflare Web Analytics token here

# Markup
markup:
  highlight:
    style: "github-dark"
    lineNos: false
    codeFences: true
  goldmark:
    renderer:
      unsafe: false

# Taxonomies
taxonomies:
  tag: tags

# Related Content
related:
  threshold: 80
  includeNewer: false
  toLower: false
  indices:
    - name: tags
      weight: 100
    - name: date
      weight: 10
```

---

## Social Share Buttons

Implement a set of **impactful, minimalist social share buttons** at the bottom of every post page (`single.html`).

### Platforms
- **X (Twitter)**
- **LinkedIn**
- **Reddit**
- **Bluesky**
- **Copy Link**: A "Copy to Clipboard" button with a brief "Copied!" visual feedback.

### Key Requirements
- **No external JavaScript libraries.** Use vanilla JS only for the "Copy Link" functionality (Clipboard API).
- **SVG Icons only.** No icon fonts (FontAwesome, etc.). Embed SVGs directly in the partial.
- **Design Aesthetic:**
  - Monochromatic by default (using `--color-muted` or `--color-border`).
  - Subtle transition to `--color-accent` or the platform's brand color on hover.
  - No heavy boxes or backgrounds. Just the icons with generous spacing.
  - Align with the "Calm Signal" principle — these should be available but not distracting.
- **Accessibility:** Each button must have a clear `aria-label` and `title`.
- **Implementation:** Create a dedicated partial `layouts/partials/share-buttons.html` and include it at the end of the post content in `single.html`.

### Discussion CTA (LinkedIn Strategy)
In addition to sharing, include a specific **"Discuss on LinkedIn"** call-to-action block. It should only render if `linkedin_post_url` is present in the frontmatter. Style it as a "Calm Signal"—a simple, authoritative link that invites the reader to join the existing conversation where the peers are.

---

## Shortcodes to Implement

### `callout.html`
Usage in posts: `{{< callout type="note" >}} Your note here {{< /callout >}}`
Types: `note`, `warning`, `tip`. Style cleanly with left border accent, no heavy box.

### `video.html`
Usage: `{{< video src="https://youtube.com/..." >}}`
Renders a responsive 16:9 iframe embed, centered, with subtle border.

---

## Sample Posts

Write two sample posts using real Markdown and the correct frontmatter schema:

**Post 1: `hello-world.md`**
Title: "Why I Built This Blog"
Content: A short, honest reflection on why a technical person starts a blog. Why GitOps. Why plain Markdown. The anti-CMS manifesto. ~300 words. First-person voice. No fluff.

**Post 2: `first-retrospective.md`**
Title: "Lessons Learned: A Project That Went Sideways"
Content: A realistic engineering retrospective reframed as a "Lessons Learned" post. A project that was scoped poorly, shipped late, and what was learned to pivot the failure into expertise growth. Demonstrate use of the `callout` shortcode in the post body. Use sections: What happened / The Pivot Points / Lessons for the Future. ~500 words.

---

## Local Development

After scaffolding, the following must work with no errors:

```bash
hugo server -D
```

Opens at `http://localhost:1313`. Hot reload on file save. Draft posts visible.

Document in `README.md`:
- Prerequisites (`hugo` binary)
- `hugo server -D` to run locally
- `git push` to deploy
- How to create a new post: `hugo new posts/my-post.md`

---

## Quality Bar

Before considering this done, verify:

- [ ] `hugo server -D` runs with zero errors or warnings
- [ ] `hugo --minify` builds cleanly to `/public`
- [ ] Homepage lists sample posts correctly
- [ ] Single post page renders with correct typography and layout
- [ ] Code blocks render with dark background and correct syntax highlighting
- [ ] All SEO meta tags present and correct on post pages (inspect `<head>`)
- [ ] Cloudflare Web Analytics beacon script present in `<head>` (when token is provided)
- [ ] RSS feed at `/index.xml` contains full post content
- [ ] Site responds to system theme changes (Light/Dark)
- [ ] About page renders correctly with professional bio
- [ ] `llms.txt` accessible at `/llms.txt` — lists all posts and includes "About" section
- [ ] `llms-full.txt` accessible at `/llms-full.txt` — contains full post content
- [ ] Both files regenerate correctly on `hugo server` locally (not just CI)
- [ ] Markdown output works at `/posts/[slug]/index.md`
- [ ] Structured data (Article, Person, Breadcrumb) is valid (test with Schema Markup Validator)
- [ ] Speculation Rules script is present in `<head>`
- [ ] Images have `loading="lazy"` and `decoding="async"` attributes
- [ ] Color contrast meets WCAG 2.1 AA (especially for accent text)
- [ ] GitHub Actions workflow is valid YAML (can be linted with `actionlint`)
- [ ] Social share buttons (X, LinkedIn, Reddit, Bluesky, Copy Link) functional on post pages
- [ ] "Copy Link" provides immediate visual feedback (e.g., "Copied!")
- [ ] Site is fully readable and usable on 375px mobile width
- [ ] No JavaScript errors in console
- [ ] No external CDN dependencies for critical CSS/fonts that would break offline

---

## What Not to Build

- No comments system (use the LinkedIn Discussion CTA instead)
- No search feature
- No pagination beyond basic Hugo pagination
- No newsletter signup
- No cookie banners
- No JavaScript frameworks or bundlers

---

## Future Roadmap (Parking Lot)
The following features are NOT part of the initial build but should be kept in mind for future architectural compatibility:
- **Voice Audit**: A GitHub Action step to score posts against the "Technical Outcome Leader" persona.
- **Interactive Demos**: A pattern for allowing small, isolated JS "islands" for technical demonstrations.
