#!/usr/bin/env python3
"""
srvrlss.dev Content Automation
================================
Modes:
  (default)       PR automation: social hooks, semantic linking, image prompt, commit-back
  --mode social-loop      Friday: summarize social discussion vibe via ntfy
  --mode freshness-audit  Every 3 weeks: detect AI/Cloud drift, open GitHub Issues

Resilience contract:
  - Never sys.exit(1). Failures open a GitHub Issue and continue.
  - Local (non-CI) runs perform a dry-run only — no API calls, commits, or issues.
  - NTFY_TOPIC is optional; missing it skips notifications silently.
  - Missing GEMINI_API_KEY reports via PR comment and Issue, then exits 0.
"""

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone

import yaml  # pyyaml

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

IS_CI: bool = os.getenv("GITHUB_ACTIONS") == "true"
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
NTFY_TOPIC: str = os.getenv("NTFY_TOPIC", "")
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
PR_NUMBER: str = os.getenv("PR_NUMBER", "")
REPO: str = os.getenv("REPO", "")
BASE_BRANCH: str = os.getenv("BASE_BRANCH", "main")

PRODUCTION_LLMS_URL = "https://srvrlss.dev/llms-full.txt"
GEMINI_TEXT_MODEL = "gemini-3.1-flash"
IMAGE_MODEL = "nanobananav2"

BANNED_WORDS = [
    "utilize", "deep-dive", "game-changing", "synergy",
    "very", "extremely", "robust", "additionally",
    "furthermore", "moreover",
]

BRAND_VOICE_RULES = """
Brand voice rules (srvrlss.dev by Alexandre Brisebois):
- Register: Reflective-vulnerable blended with urgently excited.
- Sentences: Direct, active. Vary length. Single-sentence paragraphs are a signature move.
- Paragraphs: 1–4 sentences max.
- Pronouns: "I" for personal learning/opinions. "We" for shared outcomes/success.
- NEVER use these banned words: utilize, deep-dive, game-changing, synergy, very,
  extremely, robust, additionally, furthermore, moreover.
- NEVER open with "In this article..." or "Let's dive into...".
- NEVER use consulting-deck tone. NEVER fake enthusiasm.
- Multi-cloud by default: GCP, AWS, Azure as peers.
- Microsoft is origin story, not current identity.
"""


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _http_json(url: str, payload: dict, token: str = "") -> dict:
    """POST JSON payload, return parsed response dict."""
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())


def _http_get(url: str, timeout: int = 15) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode("utf-8")


# ---------------------------------------------------------------------------
# Gemini API
# ---------------------------------------------------------------------------

def call_gemini(prompt: str, temperature: float = 0.7) -> str:
    """Generate text via Gemini REST API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_TEXT_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 2048},
    }
    result = _http_json(url, payload)
    return result["candidates"][0]["content"]["parts"][0]["text"]


def generate_image_via_api(prompt: str) -> bytes | None:
    """
    Attempt image generation via nanobananav2.
    Returns raw bytes on success, None on failure.
    The API endpoint mirrors Gemini's experimental image generation format.
    """
    if not GEMINI_API_KEY:
        return None
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{IMAGE_MODEL}:generateImage?key={GEMINI_API_KEY}"
    )
    payload = {"prompt": prompt, "responseFormat": "webp"}
    try:
        result = _http_json(url, payload)
        import base64
        raw = result.get("image", {}).get("data", "")
        return base64.b64decode(raw) if raw else None
    except Exception as e:
        print(f"[WARN] Image generation via {IMAGE_MODEL} failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split a Markdown file into (frontmatter dict, body string)."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content
    fm = yaml.safe_load(content[3:end]) or {}
    body = content[end + 4:]
    return fm, body


def write_frontmatter_atomic(filepath: pathlib.Path, fm: dict, body: str) -> None:
    """Write frontmatter + body atomically via temp-file rename."""
    import io
    buf = io.StringIO()
    buf.write("---\n")
    yaml.dump(fm, buf, default_flow_style=False, allow_unicode=True, sort_keys=False)
    buf.write("---")
    buf.write(body)
    tmp = filepath.with_suffix(".tmp")
    tmp.write_text(buf.getvalue(), encoding="utf-8")
    tmp.replace(filepath)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def get_changed_posts() -> list[pathlib.Path]:
    """Return new/modified content/posts/*.md files vs the base branch."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{BASE_BRANCH}...HEAD"],
            capture_output=True, text=True, check=True,
        )
        paths = [
            pathlib.Path(p) for p in result.stdout.strip().splitlines()
            if p.startswith("content/posts/") and p.endswith(".md")
        ]
        return [p for p in paths if p.exists()]
    except subprocess.CalledProcessError as e:
        print(f"[WARN] git diff failed: {e}", file=sys.stderr)
        return []


def git_commit_and_push(filepath: pathlib.Path, message: str) -> None:
    """Stage a file, commit, and push to the current branch."""
    subprocess.run(
        ["git", "config", "user.name", "github-actions[bot]"], check=True
    )
    subprocess.run(
        ["git", "config", "user.email",
         "github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "add", str(filepath)], check=True)
    # Skip if nothing staged
    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], capture_output=True
    )
    if status.returncode == 0:
        print(f"[INFO] No changes to commit for {filepath.name}")
        return
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

def post_pr_comment(body: str) -> None:
    if not all([GITHUB_TOKEN, PR_NUMBER, REPO]):
        print("[WARN] Skipping PR comment: missing GITHUB_TOKEN, PR_NUMBER, or REPO",
              file=sys.stderr)
        return
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    _http_json(url, {"body": body}, token=GITHUB_TOKEN)


def open_github_issue(title: str, body: str, labels: list[str] | None = None) -> None:
    if not all([GITHUB_TOKEN, REPO]):
        print("[WARN] Cannot open GitHub Issue: missing GITHUB_TOKEN or REPO",
              file=sys.stderr)
        return
    url = f"https://api.github.com/repos/{REPO}/issues"
    payload: dict = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    try:
        _http_json(url, payload, token=GITHUB_TOKEN)
        print(f"[INFO] Opened GitHub Issue: {title}")
    except Exception as e:
        print(f"[WARN] Could not open GitHub Issue: {e}", file=sys.stderr)


def send_ntfy(message: str, title: str = "srvrlss.dev") -> None:
    if not NTFY_TOPIC:
        return
    try:
        req = urllib.request.Request(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={"Title": title, "Priority": "default"},
        )
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception as e:
        print(f"[WARN] ntfy notification failed: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# AI generation functions
# ---------------------------------------------------------------------------

def check_banned_words(text: str) -> list[str]:
    lower = text.lower()
    return [w for w in BANNED_WORDS if re.search(r"\b" + re.escape(w) + r"\b", lower)]


def gen_tldr(title: str, body: str) -> str:
    prompt = f"""{BRAND_VOICE_RULES}

Write a 2-sentence TLDR for this blog post. Be direct and punchy. No filler.
The TLDR should capture the core insight and the "so what." No labels.

Title: {title}
Content (first 1500 chars): {body[:1500]}

Return exactly 2 sentences separated by a space."""
    return call_gemini(prompt, temperature=0.5).strip()


def gen_social_hooks(title: str, body: str, context: str) -> dict:
    prompt = f"""{BRAND_VOICE_RULES}

Generate social media content for a new post on srvrlss.dev.

Post title: {title}
Post content (first 2000 chars): {body[:2000]}
Existing blog context (for awareness, not copying): {context[:1500]}

Generate in JSON format:
{{
  "linkedin": [
    "Variation 1 (story arc: hook → tension → insight → CTA, 3-5 sentences)",
    "Variation 2 (lead with a question or surprising observation)",
    "Variation 3 (lead with a strong opinion or counterintuitive claim)"
  ],
  "x_thread": [
    "Tweet 1/3 (hook, under 280 chars)",
    "Tweet 2/3 (core insight, under 280 chars)",
    "Tweet 3/3 (takeaway or CTA, under 280 chars)"
  ],
  "bluesky_thread": [
    "Post 1/3 (hook with technical depth, under 300 chars)",
    "Post 2/3 (specifics and nuance, under 300 chars)",
    "Post 3/3 (practical takeaway, under 300 chars)"
  ]
}}

Return only the JSON object."""
    raw = call_gemini(prompt)
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"linkedin": [], "x_thread": [], "bluesky_thread": []}


def gen_tags(title: str, body: str) -> list[str]:
    prompt = f"""Extract 3-5 specific technical tags from this blog post.
Lowercase, hyphenated where needed (e.g., "serverless", "cloud-native", "ai-agents").
Focus on concrete technical topics, not abstract themes.
Return only a JSON array, e.g.: ["serverless", "event-driven", "cloud-native"]

Title: {title}
Content: {body[:1000]}"""
    raw = call_gemini(prompt, temperature=0.3)
    match = re.search(r"\[.*?\]", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return []


def gen_semantic_links(title: str, body: str, context: str) -> dict:
    prompt = f"""Given existing blog content and a new post, identify:
1. "related_posts": 2-3 existing post titles most thematically related to the new post.
2. "mentioned_in": 2-3 existing post titles where it would make sense to add a link TO the new post.

New post title: {title}
New post excerpt: {body[:800]}

Existing posts (llms-full.txt):
{context[:3000]}

Return JSON only:
{{
  "related_posts": ["Title 1", "Title 2"],
  "mentioned_in": ["Title A", "Title B"]
}}"""
    raw = call_gemini(prompt, temperature=0.4)
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"related_posts": [], "mentioned_in": []}


def gen_image_prompt(title: str, body: str) -> str:
    prompt = f"""Generate a concise image generation prompt for a minimalist blog header image.

Style requirements:
- Abstract architectural diagrams or serverless event flows
- High-contrast textures, "Calm Signal" minimal baseline
- Muted earth tones (warm off-white, deep green, coral accent)
- NO stock-photo humans, NO faces, NO logos
- WebP format, landscape orientation

Post title: {title}
Post excerpt: {body[:500]}

Return only the image prompt (under 120 words). No labels, no explanation."""
    return call_gemini(prompt, temperature=0.8).strip()


# ---------------------------------------------------------------------------
# Production context
# ---------------------------------------------------------------------------

def load_production_context() -> str:
    try:
        return _http_get(PRODUCTION_LLMS_URL, timeout=15)
    except Exception as e:
        print(f"[WARN] Could not load production context: {e}", file=sys.stderr)
        return "[Production context unavailable — new site, no published posts yet]"


# ---------------------------------------------------------------------------
# Mode: PR automation
# ---------------------------------------------------------------------------

def run_pr_automation() -> None:
    if not GEMINI_API_KEY:
        msg = (
            "## Content Automation — Skipped\n\n"
            "`GEMINI_API_KEY` is not set in GitHub Repository Secrets. "
            "Add it to enable AI-powered content hooks, semantic linking, and image prompts."
        )
        post_pr_comment(msg)
        open_github_issue(
            title=f"Automation Script Failure: {_now_str()}",
            body="**Cause:** `GEMINI_API_KEY` not found in secrets.\n\n"
                 "Add it at: Settings → Secrets and variables → Actions.",
            labels=["automation", "configuration"],
        )
        return

    context = load_production_context()
    posts = get_changed_posts()

    if not posts:
        print("[INFO] No new/changed posts detected. Nothing to do.")
        return

    comment_sections: list[str] = [
        "## Content Automation Report\n",
        f"*{len(posts)} post(s) processed · {_now_str()}*\n\n---\n",
    ]

    for post_path in posts:
        print(f"[INFO] Processing: {post_path}")
        try:
            content = post_path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(content)
            title = fm.get("title", post_path.stem)
            slug = fm.get("slug") or post_path.stem
            fm_updated = False

            comment_sections.append(f"### {title}\n")

            # --- TLDR ---
            if not fm.get("tldr"):
                tldr = gen_tldr(title, body)
                fm["tldr"] = tldr
                fm_updated = True
                comment_sections.append(f"**Generated TLDR:**\n> {tldr}\n\n")

            # --- Tags ---
            if not fm.get("tags"):
                tags = gen_tags(title, body)
                if tags:
                    fm["tags"] = tags
                    fm_updated = True
                    comment_sections.append(
                        f"**Generated Tags:** {' '.join(f'`#{t}`' for t in tags)}\n\n"
                    )

            # --- Semantic links ---
            links = gen_semantic_links(title, body, context)
            if links.get("related_posts"):
                fm["related_posts"] = links["related_posts"]
                fm_updated = True
            if links.get("mentioned_in"):
                fm["mentioned_in"] = links["mentioned_in"]
                fm_updated = True
            comment_sections.append("**Semantic Links:**\n")
            comment_sections.append(
                f"- Related posts: {', '.join(links.get('related_posts', ['none found']))}\n"
            )
            comment_sections.append(
                f"- Add backlinks in: {', '.join(links.get('mentioned_in', ['none found']))}\n\n"
            )

            # --- Social hooks ---
            hooks = gen_social_hooks(title, body, context)
            banned_found = check_banned_words(
                " ".join(
                    hooks.get("linkedin", [])
                    + hooks.get("x_thread", [])
                    + hooks.get("bluesky_thread", [])
                )
            )
            if banned_found:
                comment_sections.append(
                    f"⚠️ **Brand voice warning — banned words detected:** "
                    f"{', '.join(f'`{w}`' for w in banned_found)}\n\n"
                )

            comment_sections.append("**LinkedIn Hooks:**\n")
            for i, hook in enumerate(hooks.get("linkedin", []), 1):
                comment_sections.append(f"<details><summary>Variation {i}</summary>\n\n{hook}\n\n</details>\n\n")

            comment_sections.append("**X Thread:**\n")
            for tweet in hooks.get("x_thread", []):
                comment_sections.append(f"> {tweet}\n\n")

            comment_sections.append("**Bluesky Thread:**\n")
            for post in hooks.get("bluesky_thread", []):
                comment_sections.append(f"> {post}\n\n")

            # --- Image prompt ---
            image_prompt = gen_image_prompt(title, body)
            fm["image_prompt"] = image_prompt
            fm_updated = True
            comment_sections.append(
                f"**Image Prompt** (for `static/images/posts/{slug}.webp`):\n"
                f"```\n{image_prompt}\n```\n\n"
            )

            # --- Image generation ---
            img_dir = pathlib.Path(f"static/images/posts")
            img_dir.mkdir(parents=True, exist_ok=True)
            img_path = img_dir / f"{slug}.webp"
            img_bytes = generate_image_via_api(image_prompt)
            if img_bytes:
                img_path.write_bytes(img_bytes)
                comment_sections.append(f"✅ **Image generated:** `{img_path}`\n\n")
                subprocess.run(["git", "add", str(img_path)], check=False)
            else:
                comment_sections.append(
                    "ℹ️ **Image:** Use the prompt above with your preferred image generator. "
                    f"Save the result to `{img_path}`.\n\n"
                )

            # --- Commit frontmatter back to PR ---
            if fm_updated:
                write_frontmatter_atomic(post_path, fm, body)
                git_commit_and_push(
                    post_path,
                    f"[automation] Update frontmatter for {post_path.name}",
                )

            comment_sections.append("---\n")

        except Exception:
            err = traceback.format_exc()
            print(f"[ERROR] Failed processing {post_path}:\n{err}", file=sys.stderr)
            comment_sections.append(
                f"⚠️ **Automation error for {post_path.name}** — "
                "see the GitHub Issue opened by the automation.\n\n---\n"
            )
            open_github_issue(
                title=f"Automation Script Failure: {_now_str()}",
                body=f"**Post:** `{post_path}`\n\n**Error:**\n```\n{err}\n```",
                labels=["automation", "bug"],
            )

    post_pr_comment("\n".join(comment_sections))
    send_ntfy(
        f"Content automation complete — PR #{PR_NUMBER}, {len(posts)} post(s) processed.",
        title="srvrlss.dev PR",
    )


# ---------------------------------------------------------------------------
# Mode: Social discussion loop (Friday)
# ---------------------------------------------------------------------------

def run_social_loop() -> None:
    """
    Summarize discussion vibe across posts with active social_posts links.
    Reads post frontmatter for LinkedIn/X/Bluesky URLs, generates a summary via
    Gemini based on post titles + context, and delivers via ntfy.
    """
    if not GEMINI_API_KEY:
        print("[WARN] GEMINI_API_KEY not set — skipping social loop.", file=sys.stderr)
        return

    posts_dir = pathlib.Path("content/posts")
    posts_with_links: list[dict] = []

    for md in sorted(posts_dir.glob("*.md")):
        fm, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
        social = fm.get("social_posts", {}) or {}
        if any(social.get(k) for k in ("linkedin", "x", "bluesky")):
            posts_with_links.append({
                "title": fm.get("title", md.stem),
                "links": social,
            })

    if not posts_with_links:
        print("[INFO] No posts with social links found.")
        send_ntfy("No posts with active social discussion links found.", title="srvrlss.dev weekly")
        return

    post_list = "\n".join(
        f"- {p['title']}: "
        + ", ".join(f"{k}={v}" for k, v in p["links"].items() if v)
        for p in posts_with_links
    )

    prompt = f"""{BRAND_VOICE_RULES}

You are doing a weekly social discussion review for srvrlss.dev.
The following posts have active social discussion threads (LinkedIn/X/Bluesky):

{post_list}

Write a brief, honest "Discussion Vibe" summary (3-5 sentences):
- Which posts seem to be generating conversation based on the topic areas?
- What recurring themes are emerging across the technical community?
- One action the author might take this week (respond, follow-up post, etc.)

Be direct, no fluff. Private summary — not for publishing."""

    summary = call_gemini(prompt, temperature=0.6)
    send_ntfy(summary, title="srvrlss.dev Weekly Discussion")
    print(f"[INFO] Social loop summary sent via ntfy.\n\n{summary}")


# ---------------------------------------------------------------------------
# Mode: Content freshness audit (every 3 weeks)
# ---------------------------------------------------------------------------

def run_freshness_audit() -> None:
    """
    Detect AI/Cloud Drift and Technical Decay in published posts.
    Opens prioritized GitHub Issues for outdated content.
    """
    if not GEMINI_API_KEY:
        print("[WARN] GEMINI_API_KEY not set — skipping freshness audit.", file=sys.stderr)
        return

    posts_dir = pathlib.Path("content/posts")
    today = datetime.now(timezone.utc)
    post_summaries: list[str] = []

    for md in sorted(posts_dir.glob("*.md")):
        fm, body = parse_frontmatter(md.read_text(encoding="utf-8"))
        date_val = fm.get("date")
        if date_val:
            if hasattr(date_val, "strftime"):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)[:10]
        else:
            date_str = "unknown"
        post_summaries.append(
            f"- Title: {fm.get('title', md.stem)}\n"
            f"  Date: {date_str}\n"
            f"  Tags: {', '.join(fm.get('tags', []))}\n"
            f"  Excerpt: {body[:200].strip()}"
        )

    prompt = f"""{BRAND_VOICE_RULES}

Today is {today.strftime('%Y-%m-%d')}. Review these blog posts for content freshness issues.

Identify posts with:
1. **AI/Cloud Drift** — technical claims about AI or cloud services that may be outdated
   (e.g., model names, service pricing, API shapes that evolve rapidly)
2. **Technical Decay** — code examples, tooling references, or best practices that
   the ecosystem has moved past

Posts:
{chr(10).join(post_summaries)}

For each issue found, return a JSON array:
[
  {{
    "title": "Post title",
    "issue_type": "AI/Cloud Drift" | "Technical Decay",
    "priority": "high" | "medium" | "low",
    "description": "Specific concern in 1-2 sentences"
  }}
]

Return only the JSON array. If no issues, return [].
"""

    raw = call_gemini(prompt, temperature=0.3)
    match = re.search(r"\[[\s\S]*?\]", raw)
    if not match:
        print("[INFO] Freshness audit: no issues detected.")
        return

    try:
        issues = json.loads(match.group())
    except json.JSONDecodeError:
        print("[WARN] Could not parse freshness audit response.", file=sys.stderr)
        return

    if not issues:
        print("[INFO] Freshness audit: all posts appear current.")
        send_ntfy("Content freshness audit complete — no issues found.", title="srvrlss.dev Audit")
        return

    print(f"[INFO] Freshness audit: {len(issues)} issue(s) found.")
    for issue in issues:
        title = f"[{issue.get('issue_type', 'Content')}] {issue.get('title', 'Unknown post')} — {issue.get('priority', 'medium').upper()} priority"
        body = (
            f"**Post:** {issue.get('title')}\n"
            f"**Issue type:** {issue.get('issue_type')}\n"
            f"**Priority:** {issue.get('priority')}\n\n"
            f"**Description:** {issue.get('description')}\n\n"
            f"*Detected by automated freshness audit on {today.strftime('%Y-%m-%d')}.*"
        )
        open_github_issue(title=title, body=body, labels=["content-freshness", "automation"])

    send_ntfy(
        f"Freshness audit: {len(issues)} issue(s) opened as GitHub Issues.",
        title="srvrlss.dev Audit",
    )


# ---------------------------------------------------------------------------
# Local dry-run
# ---------------------------------------------------------------------------

def run_dry_run() -> None:
    print("[DRY RUN] Running local validation — no API calls will be made.")
    print(f"[DRY RUN] Checking production context from {PRODUCTION_LLMS_URL} ...")

    try:
        context = _http_get(PRODUCTION_LLMS_URL, timeout=10)
        print(f"[DRY RUN] ✓ Production context: {len(context)} chars")
    except Exception as e:
        print(f"[DRY RUN] ⚠ Production context unavailable: {e}")

    posts = get_changed_posts()
    print(f"[DRY RUN] Changed posts vs origin/{BASE_BRANCH}: {len(posts)}")
    for p in posts:
        fm, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        tldr_status = "present" if fm.get("tldr") else "MISSING (would generate)"
        tags_status = str(fm.get("tags", [])) if fm.get("tags") else "MISSING (would generate)"
        print(
            f"  - {p.name}\n"
            f"    title:  {fm.get('title', '?')!r}\n"
            f"    tldr:   {tldr_status}\n"
            f"    tags:   {tags_status}\n"
            f"    image:  {'set' if fm.get('image_prompt') else 'MISSING (would generate)'}"
        )

    print("\n[DRY RUN] Complete. Set GITHUB_ACTIONS=true to run in full mode.")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _safe_run(fn) -> None:
    """Run a function; on failure, open a GitHub Issue and exit 0."""
    try:
        fn()
    except Exception:
        err = traceback.format_exc()
        print(f"[ERROR] Unhandled exception:\n{err}", file=sys.stderr)
        open_github_issue(
            title=f"Automation Script Failure: {_now_str()}",
            body=f"**Mode:** {fn.__name__}\n\n**Error:**\n```\n{err}\n```",
            labels=["automation", "bug"],
        )
        sys.exit(0)  # Never fail the build


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="srvrlss.dev content automation")
    parser.add_argument(
        "--mode",
        choices=["pr", "social-loop", "freshness-audit"],
        default="pr",
        help="Execution mode (default: pr)",
    )
    args = parser.parse_args()

    if not IS_CI:
        run_dry_run()
        return

    if args.mode == "pr":
        _safe_run(run_pr_automation)
    elif args.mode == "social-loop":
        _safe_run(run_social_loop)
    elif args.mode == "freshness-audit":
        _safe_run(run_freshness_audit)


if __name__ == "__main__":
    main()
