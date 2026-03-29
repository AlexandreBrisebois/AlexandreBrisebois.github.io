# Plan: Landing Page Hero Image + Loop Cleanup

## Context
The landing page currently lists all `Site.RegularPages` including the About page, and has no hero image. The goal is to:
1. Add a dynamically generated hero image synthesized from the 10 most recent published posts
2. Remove About from the post list (keep it in top nav)
3. Add a manual + auto-trigger for hero image regeneration via GitHub Actions

This supports the brand pivot toward "AI enthusiast" by making the hero image a living visual synthesis of the blog's current thinking.

## Conflict Risk: PR #17

**PR #17** (`claude/update-image-generation-nF1rJ`) is open and merges into main. It rewrites `content_automation.py` significantly — removing `gen_image_prompt`, `gen_refined_image_prompt`, `gen_tldr`, `gen_tags`, `gen_social_hooks`, and changing `critique_image`'s signature.

**Strategy:** The HTML/CSS changes (Phases 1–3) have zero conflict with PR #17. The script additions (Phase 4) must be designed against the **post-PR #17 version** of the script. Recommend:
- Implement Phases 1–3 now (safe, no overlap)
- Rebase the branch on main after PR #17 merges, then implement Phase 4

The plan below is written for the post-PR #17 script state.

---

## Phases

### Phase 1 — Rewrite `layouts/index.html`
**File:** `layouts/index.html`
**Current state:** 22 lines. `range .Site.RegularPages.ByDate.Reverse` includes `content/about.md`. No hero, no tag strip, no latest-card marker.
**Replaces the entire file** with the consolidated final state below — four concerns in one edit:
- Filter to posts section only (excludes About)
- Hero image block (gracefully absent when `hero.webp` doesn't exist yet)
- Tag navigation strip above post list (top 7 tags by count, links to tag pages)
- Latest card marker (`post-card--latest` on first card)

```html
{{ define "main" }}
<div class="home">
  <p class="anchor-statement">A thinking space for outcomes — where cloud engineering, AI agents, and systems thinking meet.</p>

  {{ if fileExists "static/images/hero.webp" }}
  <div class="hero-image">
    <img src="/images/hero.webp" alt="Visual synthesis of recent thinking" loading="eager" decoding="async">
  </div>
  {{ end }}

  {{ $tags := slice }}
  {{ range .Site.Taxonomies.tags.ByCount }}
    {{ if lt (len $tags) 7 }}{{ $tags = $tags | append .Page.Title }}{{ end }}
  {{ end }}
  {{ if $tags }}
  <nav class="tag-strip">
    {{ range $tags }}
    <a href="{{ "/tags/" | relLangURL }}{{ . | urlize }}/" class="tag-chip">{{ . }}</a>
    {{ end }}
  </nav>
  {{ end }}

  <section class="post-list">
    {{ $pages := (where .Site.RegularPages "Section" "posts").ByDate.Reverse }}
    {{ range $i, $p := $pages }}
    <article class="post-card{{ if eq $i 0 }} post-card--latest{{ end }}">
      {{ $isRetro := or (in (default slice .Params.tags) "retrospective") (in .Title "Retrospective") }}
      {{ $title := .Title }}
      {{ if $isRetro }}
        {{ $title = replace .Title "Retrospective" "Lessons Learned" }}
      {{ end }}
      <h2>
        {{ if $isRetro }}<span class="lessons-badge">Lessons Learned</span>{{ end }}
        <a href="{{ .RelPermalink }}">{{ $title }}</a>
      </h2>
      <time datetime="{{ .Date.Format "2006-01-02" }}">{{ .Date.Format "January 2, 2006" }}</time>
      {{ with .Description }}<p>{{ . }}</p>{{ end }}
    </article>
    {{ end }}
  </section>
</div>
{{ end }}
```

Note: Inside `range $i, $p := $pages`, `.` is still the current page — existing `.Params`, `.Title`, `.RelPermalink` references are unchanged.

---

### Phase 2 — Add CSS for hero image, tag strip, and latest card
**File:** `static/css/main.css`
**Current state:** No `.hero-image`, `.tag-strip`, `.tag-chip`, or `.post-card--latest` rules.
**Append** four new rule blocks consistent with the "Calm Signal" design system (`#F7F5F0` bg, `#0D1117` dark, `#2D6A4F` green, `#E76F51` coral, max list width 860px):

- **`.hero-image`** — full width up to 860px, `border-radius` matching existing tokens, `aspect-ratio: 16/9`, `object-fit: cover`, subtle box-shadow matching `.post-cover`
- **`.tag-strip`** — horizontal flex row, `gap: 0.5rem`, `flex-wrap: wrap`, `margin-bottom: 1.5rem`
- **`.tag-chip`** — small pill: `border: 1px solid #2D6A4F`, `border-radius: 999px`, `padding: 0.2rem 0.6rem`, `font-size: 0.8rem`, muted text, no background — hover fills with `#2D6A4F` at 10% opacity
- **`.post-card--latest`** — `border-left: 3px solid #E76F51` — no other change

---

### Phase 3 — Extend OG/Twitter card in `layouts/partials/head.html`
**File:** `layouts/partials/head.html`
**Current state (line 12):** `{{ with .Params.image }}<meta property="og:image" content="{{ . | absURL }}">{{ end }}` — only fires for pages with an `image` frontmatter field. The home page has none, so no OG image today. Twitter card (line 15) has no image tag at all.
**Change:** Extend the OG image line with an `else if` fallback for the home page, and add a matching Twitter image tag:

```html
{{ with .Params.image }}
<meta property="og:image" content="{{ . | absURL }}">
<meta name="twitter:image" content="{{ . | absURL }}">
{{ else if and .IsHome (fileExists "static/images/hero.webp") }}
<meta property="og:image" content="{{ "/images/hero.webp" | absURL }}">
<meta name="twitter:image" content="{{ "/images/hero.webp" | absURL }}">
{{ end }}
```

Every time the hero script regenerates and deploys, the landing page's social previews update automatically. No change to post-level OG images.

---

### Phase 4 — Add `# Current Focus` to `layouts/index.llms.txt`
**File:** `layouts/index.llms.txt`
**Current state (line 1):** `# srvrlss.dev — Full Content for LLM Consumption`
**Change:** Prepend a `Current Focus` block that Hugo populates from `data/hero.yaml` (written by the hero script). When the file doesn't exist yet, the block is silently omitted:

```
{{ with .Site.Data.hero }}{{ with .current_focus }}# Current Focus
{{ . }}

{{ end }}{{ end }}
```

Place this before the existing `# srvrlss.dev` header line.

---

### Phase 5 — Add hero image generation to `content_automation.py`
**File:** `.github/scripts/content_automation.py`
**Dependency:** Post-PR #17 script state (this branch is already reset to that base).
**Three additions:**

**5a. Update `BRAND_VOICE_RULES` constant** — append one line:
```
- Current pivot: AI enthusiast and builder. Lead with AI-native perspective, cloud is the substrate.
```

**5b. New functions** — add after the existing `load_production_context()` function:

```python
def get_recent_posts(n: int = 10) -> list[dict]:
    """
    Read the n most recent non-draft posts from content/posts/*.md.
    Sorted by date frontmatter descending.
    Returns list of {title, description, tldr, tags}.
    Uses tldr as the primary signal — it's a Gemini-curated 2-sentence summary
    of the full post, far denser per token than a raw body excerpt.
    Falls back to description when tldr is absent.
    """
    posts_dir = pathlib.Path("content/posts")
    entries = []
    for md in posts_dir.glob("*.md"):
        fm, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
        if fm.get("draft"):
            continue
        date_val = fm.get("date")
        entries.append((date_val, {
            "title": fm.get("title", md.stem),
            "description": fm.get("description", ""),
            "tldr": fm.get("tldr", ""),
            "tags": fm.get("tags") or [],
        }))
    entries.sort(key=lambda x: str(x[0] or ""), reverse=True)
    return [e[1] for e in entries[:n]]


def gen_hero_context(posts: list[dict]) -> dict:
    """
    Single Gemini call that returns both the image prompt and the current_focus line.
    One call avoids serializing the same post context twice.
    Returns {"image_prompt": str, "current_focus": str}.
    """
    lines = []
    for p in posts:
        summary = p.get("tldr") or p.get("description") or ""
        tags = ", ".join(p["tags"]) if p["tags"] else "untagged"
        lines.append(f"- {p['title']} [{tags}]: {summary}")
    context_block = "\n".join(lines)

    prompt = f"""You are generating metadata for the landing page of srvrlss.dev, a blog by Alexandre Brisebois.

{BRAND_VOICE_RULES}

Recent posts (most recent first):
{context_block}

Return JSON only with two fields:
{{
  "image_prompt": "<under 120 words. Abstract architectural / AI-flow diagram. Calm Signal aesthetic: muted earth tones, warm off-white, deep green, coral accent. NO humans, faces, logos. Landscape orientation. Synthesizes the dominant themes across these posts.>",
  "current_focus": "<one sentence, ≤20 words, brand voice: what this blog is actively exploring right now>"
}}"""
    raw = call_gemini(prompt, temperature=0.8, max_tokens=400)
    match = re.search(r"\{[\s\S]*?\}", raw)
    if match:
        try:
            result = json.loads(match.group())
            if "image_prompt" in result and "current_focus" in result:
                return result
        except json.JSONDecodeError:
            pass
    # Fallback: treat raw output as just the image prompt
    return {"image_prompt": raw.strip()[:500], "current_focus": ""}


def run_hero_image_generation() -> None:
    """
    Generate a landing-page hero image synthesized from the 10 most recent posts.
    Outputs: static/images/hero.webp, static/images/hero-image-prompt.md, data/hero.yaml
    All three are committed to the current branch in a single commit.
    """
    if not GEMINI_API_KEY:
        print("[WARN] GEMINI_API_KEY not set — skipping hero image generation.", file=sys.stderr)
        return

    posts = get_recent_posts(10)
    if not posts:
        print("[WARN] No published posts found — skipping hero generation.", file=sys.stderr)
        return

    print(f"[INFO] Generating hero image from {len(posts)} posts.")
    context = gen_hero_context(posts)
    image_prompt = context["image_prompt"]
    current_focus = context.get("current_focus", "")

    img_dir = pathlib.Path("static/images")
    img_dir.mkdir(parents=True, exist_ok=True)
    hero_path = img_dir / "hero.webp"
    prompt_path = img_dir / "hero-image-prompt.md"
    data_dir = pathlib.Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    hero_yaml_path = data_dir / "hero.yaml"

    img_bytes = generate_image_via_api(image_prompt)
    if img_bytes:
        critique = critique_image(img_bytes, image_prompt)
        print(f"[INFO] Image critique: {critique['feedback']}")
        if not critique["keep"]:
            retry_prompt = f"{image_prompt}\n\nRevision: {critique['feedback']}"
            img_bytes_2 = generate_image_via_api(retry_prompt)
            if img_bytes_2:
                img_bytes = img_bytes_2
        hero_path.write_bytes(img_bytes)
        print(f"[INFO] Hero image written to {hero_path}")
    else:
        print("[WARN] Image generation failed — hero.webp not updated.", file=sys.stderr)
        return

    prompt_path.write_text(image_prompt, encoding="utf-8")
    hero_yaml_path.write_text(
        f"current_focus: {yaml.dump(current_focus).strip()}\n", encoding="utf-8"
    )

    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email",
                    "github-actions[bot]@users.noreply.github.com"], check=True)
    for path in [hero_path, prompt_path, hero_yaml_path]:
        subprocess.run(["git", "add", str(path)], check=False)
    status = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if status.returncode == 0:
        print("[INFO] No changes to commit for hero image.")
        return
    subprocess.run(
        ["git", "commit", "-m", "[automation] Regenerate landing page hero image"], check=True
    )
    subprocess.run(["git", "push"], check=True)
    send_ntfy("Hero image regenerated and pushed.", title="srvrlss.dev Hero")
```

**5c. Argparse** — add `"hero-image"` to `choices` in `main()` and dispatch:
```python
elif args.mode == "hero-image":
    _safe_run(run_hero_image_generation)
```

Reused post-PR #17 functions (no modification needed):
- `generate_image_via_api(prompt)` — image generation
- `critique_image(img_bytes, image_prompt)` — 2-arg signature
- `call_gemini(prompt, temperature, max_tokens)` — text generation
- `parse_frontmatter(content)` — frontmatter parsing
- `send_ntfy(message, title)` — notifications
- `_safe_run(fn)` — error wrapper

---

### Phase 6 — Add `generate-hero` GitHub Actions workflow
**File:** `.github/workflows/generate-hero.yml` *(new file)*
**Triggers:** Manual (`workflow_dispatch`) + automatic after successful deploy (`workflow_run`).
**Loop prevention:** The `workflow_run` event fires when `Deploy` completes. The hero script commits as `github-actions[bot]`. A second deploy fires for the hero image commit, but the hero workflow's `if` condition blocks it: `github.event.workflow_run.head_commit.author.name != 'github-actions[bot]'`.

```yaml
name: Generate Hero Image

on:
  workflow_dispatch:
  workflow_run:
    workflows: ["Deploy"]
    types: [completed]
    branches: [main]

permissions:
  contents: write

jobs:
  generate-hero:
    runs-on: ubuntu-latest
    if: |
      github.event_name == 'workflow_dispatch' ||
      (github.event_name == 'workflow_run' &&
       github.event.workflow_run.conclusion == 'success' &&
       github.event.workflow_run.head_commit.author.name != 'github-actions[bot]')

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python 3.14
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'

      - name: Install dependencies
        run: pip install pyyaml==6.0.3

      - name: Generate hero image
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          NTFY_TOPIC: ${{ secrets.NTFY_TOPIC }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          REPO: ${{ github.repository }}
          GITHUB_ACTIONS: "true"
        run: python3 .github/scripts/content_automation.py --mode hero-image
```

---

## Critical Files

| Phase | File | Nature of change |
|-------|------|-----------------|
| 1 | `layouts/index.html` | Full rewrite (23 → ~50 lines): posts-only loop, hero block, tag strip, latest marker |
| 2 | `static/css/main.css` | Append 4 new rule blocks: `.hero-image`, `.tag-strip`, `.tag-chip`, `.post-card--latest` |
| 3 | `layouts/partials/head.html` | Extend line 12: add `else if` fallback + Twitter image tag |
| 4 | `layouts/index.llms.txt` | Prepend 3-line `Current Focus` block (no-op when `data/hero.yaml` absent) |
| 5 | `.github/scripts/content_automation.py` | Add `get_recent_posts()`, `gen_hero_context()`, `run_hero_image_generation()`; extend argparse; update `BRAND_VOICE_RULES` |
| 6 | `.github/workflows/generate-hero.yml` | New file |
| — | `data/hero.yaml` | Created at runtime by Phase 5 script; committed to repo |
| — | `static/images/hero.webp` | Created at runtime by Phase 5 script; committed to repo |
| — | `static/images/hero-image-prompt.md` | Created at runtime by Phase 5 script; committed to repo |

---

## Sequencing

1. **First:** Reset `claude/landing-page-hero-image-eZUlB` to start from `claude/update-image-generation-nF1rJ`:
   ```bash
   git checkout claude/landing-page-hero-image-eZUlB
   git reset --hard origin/claude/update-image-generation-nF1rJ
   git push -u origin claude/landing-page-hero-image-eZUlB --force-with-lease
   ```
2. **Then:** Implement all phases in order.
3. **Commit `implementation-plan.md`** to the branch alongside the code changes — the plan file lives in the PR as a record of intent.
4. **When PR #17 merges to main:** `git rebase origin/main` — clean, no conflicts since we started from that state.

---

## Verification

1. `hugo server` locally → landing page shows hero block (or graceful empty if no `hero.webp`), About absent from post list but present in nav, tag strip and latest-card coral border visible
2. `python3 .github/scripts/content_automation.py --mode hero-image` locally (dry-run) → prints N posts found, both `image_prompt` and `current_focus` parsed, exits cleanly without API calls
3. Trigger `generate-hero` workflow manually → `static/images/hero.webp`, `static/images/hero-image-prompt.md`, and `data/hero.yaml` all committed to the branch
4. Merge → deploy fires → `generate-hero` fires after → new hero committed → redeploy → live site shows updated hero + OG image + `# Current Focus` in llms.txt

---

## Branch
All work on: `claude/landing-page-hero-image-eZUlB`, reset to start from `claude/update-image-generation-nF1rJ`.
When PR #17 merges to main → `git rebase origin/main` (trivial, no conflicts).
