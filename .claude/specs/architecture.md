# Architecture Spec: Hugo & SEO

## 1. Core Config (`config.yaml`)
Include these keys:
```yaml
baseURL: "https://srvrlss.dev/"
languageCode: "en-us"
title: "srvrlss.dev"                   
theme: ""                                 # no external theme — custom layouts only
author:
  name: "Alexandre Brisebois"
permalinks:
  posts: /posts/:slug/
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
markup:
  highlight:
    style: "github-dark"
    lineNos: false
    codeFences: true
related:
  threshold: 80
  indices:
    - name: tags
      weight: 100
    - name: date
      weight: 10
```

## 2. Frontmatter Schema (`archetypes/default.md`)
Enforce this exact YAML schema for all posts:
```yaml
---
title: ""
date: YYYY-MM-DDTHH:MM:SS+00:00
description: ""           # Meta description and excerpt
tags: []                  # [retrospective, learning, engineering]
draft: false
slug: ""                  # optional override
tldr: ""                  # executive summary (2 sentences)
social_posts:
  linkedin: ""            # Context: Full URL to the active discussion thread
  x: ""                   # Context: Full URL to the X thread
  bluesky: ""             # Context: Full URL to the Bluesky thread
related_posts: []         # Suggested by Gemini based on llms-full.txt
mentioned_in: []          # Suggested by Gemini (older posts that link HERE)
image_prompt: ""          # Generating prompt (populated by automation)
---
```

## 3. LLMS & Markdown Templates
- **`layouts/_default/index.llms.txt`**: List of all posts with description.
- **`layouts/_default/index.llmsfull.txt`**: Concatenation of full post content.
- **Output formats**: HTML, RSS, `llms`, `llmsfull`, and Markdown (at `/posts/[slug]/index.md`).
- **Related Content**: Implement with these exact weights:
  ```yaml
  related:
    threshold: 80
    indices:
      - name: tags
        weight: 100
      - name: date
        weight: 10
  ```
- **Structure**: Scaffold `static/robots.txt` for crawler guidance and `archetypes/default.md` for the base template.
- **Shortcode Logic**: Share buttons must use **Vanilla JS** (Clipboard API) for the "Copy Link" functionality. No external JS libraries.

## 4. SEO & Structured Data
Implement the following in `layouts/partials/head.html`:
- **JSON-LD Schema**: `Article`, `Person` (including social links), and `BreadcrumbList`.
- **Open Graph**: `og:title`, `og:description`, `og:image`.
- **Twitter Card**: `twitter:card: "summary_large_image"`.
- **Canonical URL**: Dynamic canonical link.
- **Speculation Rules API**: `script type="speculationrules"` for pre-rendering.
- **Analytics**: Cloudflare Web Analytics beacon (`layouts/partials/analytics.html`). Only render if `cloudflare_token` is present.
- **Accessibility**: "Skip to Content" link present.
- **Asset Optimization**: Ensure all images have **`loading="lazy"`** and **`decoding="async"`** attributes.

## 5. Shortcode Implementation Details
Prevent over-engineering; use these minimalist patterns:
- **`callout.html`**: 
  ```html
  <div class="callout callout-{{ .Get "type" | default "note" }}">
    {{ .Inner | markdownify }}
  </div>
  ```
- **`video.html`**: 
  ```html
  <div class="video-wrapper">
    <iframe src="{{ .Get "src" }}" frameborder="0" allowfullscreen></iframe>
  </div>
  ```

## 6. Deployment Workflow (`deploy.yml`)
Enforce these permissions:
```yaml
permissions:
  contents: write
```
- **Action**: Use `peaceiris/actions-gh-pages@v4` with `github_token: ${{ secrets.GITHUB_TOKEN }}`.
