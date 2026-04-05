#!/usr/bin/env python3
"""
srvrlss.dev Content Automation
================================
Modes:
  - (default) PR automation: TLDR and Technical Tags enrichment.

Resilience contract:
  - Never sys.exit(1). Failures open a GitHub Issue and continue.
  - Local (non-CI) runs perform a dry-run only — no API calls, commits, or issues.
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
import time
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
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
PR_NUMBER: str = os.getenv("PR_NUMBER", "")
REPO: str = os.getenv("REPO", "")
BASE_BRANCH: str = os.getenv("BASE_BRANCH", "main")
FORCE_POSTS: str = os.getenv("FORCE_POSTS", "")

# Ordered preference list for text generation — first match wins.
GEMINI_MODEL_PREFERENCE = [
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
]

_resolved_gemini_model: str | None = None

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
- Current pivot: AI enthusiast and builder. Lead with AI-native perspective, cloud is the substrate.
"""

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

_RETRYABLE_CODES = {429, 500, 502, 503, 504}

def _http_json(url: str, payload: dict, token: str = "", retries: int = 3) -> dict:
    """POST JSON payload, return parsed response dict. Retries on transient errors."""
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code not in _RETRYABLE_CODES:
                raise
            last_exc = e
            wait = 2 ** attempt
            print(f"[WARN] HTTP {e.code} on attempt {attempt + 1}/{retries}, retrying in {wait}s…", file=sys.stderr)
            time.sleep(wait)
    raise last_exc  # type: ignore


def _http_get(url: str, timeout: int = 15) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode("utf-8")


# ---------------------------------------------------------------------------
# Gemini API
# ---------------------------------------------------------------------------

def discover_gemini_model() -> str:
    global _resolved_gemini_model
    if _resolved_gemini_model:
        return _resolved_gemini_model

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    try:
        data = json.loads(_http_get(url, timeout=15))
    except Exception as e:
        raise RuntimeError(f"Could not list Gemini models: {e}") from e

    available = {
        m["name"].split("/")[-1]
        for m in data.get("models", [])
        if "generateContent" in m.get("supportedGenerationMethods", [])
    }

    for preferred in GEMINI_MODEL_PREFERENCE:
        if preferred in available:
            print(f"[INFO] Using Gemini model: {preferred}")
            _resolved_gemini_model = preferred
            return preferred

    for candidate in sorted(available):
        if "flash" in candidate:
            _resolved_gemini_model = candidate
            return candidate

    if available:
        fallback = sorted(available)[0]
        _resolved_gemini_model = fallback
        return fallback

    raise RuntimeError(f"No generateContent-capable Gemini models found.")


def call_gemini(prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
    """Generate text via Gemini REST API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")
    model = discover_gemini_model()
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    result = _http_json(url, payload)
    return result["candidates"][0]["content"]["parts"][0]["text"]


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content
    fm = yaml.safe_load(content[3:end]) or {}
    body = content[end + 4:]
    return fm, body


def write_frontmatter_atomic(filepath: pathlib.Path, fm: dict, body: str) -> None:
    import io
    buf = io.StringIO()
    buf.write("---\n")
    yaml.dump(fm, buf, default_flow_style=False, allow_unicode=True, sort_keys=False)
    buf.write("---\n")
    buf.write(body)
    tmp = filepath.with_suffix(".tmp")
    tmp.write_text(buf.getvalue(), encoding="utf-8")
    tmp.replace(filepath)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def get_changed_posts() -> list[pathlib.Path]:
    if FORCE_POSTS:
        paths = []
        for name in FORCE_POSTS.split(","):
            name = name.strip()
            if not name: continue
            p = pathlib.Path("content/posts") / name
            if p.exists(): paths.append(p)
        return paths

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
    except Exception:
        return []


def git_commit_and_push(filepath: pathlib.Path, message: str) -> None:
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", str(filepath)], check=True)
    status = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if status.returncode == 0: return
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

def post_pr_comment(body: str) -> None:
    if not all([GITHUB_TOKEN, PR_NUMBER, REPO]): return
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    _http_json(url, {"body": body}, token=GITHUB_TOKEN)


def open_github_issue(title: str, body: str, labels: list[str] | None = None) -> None:
    if not all([GITHUB_TOKEN, REPO]): return
    url = f"https://api.github.com/repos/{REPO}/issues"
    payload = {
        "title": title,
        "body": body,
        "assignees": ["AlexandreBrisebois"]
    }
    if labels: payload["labels"] = labels
    _http_json(url, payload, token=GITHUB_TOKEN)


# ---------------------------------------------------------------------------
# PR automation
# ---------------------------------------------------------------------------

def check_banned_words(text: str) -> list[str]:
    lower = text.lower()
    return [w for w in BANNED_WORDS if re.search(r"\b" + re.escape(w) + r"\b", lower)]


def gen_tldr(title: str, body: str) -> str:
    prompt = f"""{BRAND_VOICE_RULES}
Write a 2-sentence TLDR for this blog post. Be direct and punchy. No filler.
Title: {title}
Content: {body[:1500]}
Return exactly 2 sentences separated by a space."""
    return call_gemini(prompt, temperature=0.5).strip()


def gen_tags(title: str, body: str) -> list[str]:
    prompt = f"""Extract 3-5 specific technical tags from this blog post.
Lowercase, hyphenated, JSON array format.
Title: {title}
Content: {body[:1000]}"""
    raw = call_gemini(prompt, temperature=0.3)
    match = re.search(r"\[.*?\]", raw, re.DOTALL)
    if match:
        try: return json.loads(match.group())
        except: pass
    return []


def run_pr_automation() -> None:
    if not GEMINI_API_KEY:
        post_pr_comment("## Content Automation — Skipped\n\n`GEMINI_API_KEY` is not set.")
        open_github_issue(
            title=f"Automation Script Failure: {_now_str()}",
            body="**Cause:** `GEMINI_API_KEY` not found in secrets.",
            labels=["automation", "configuration"],
        )
        return

    posts = get_changed_posts()
    if not posts: return

    comment_sections = [
        "## Content Automation Report\n",
        f"*{len(posts)} post(s) processed · {_now_str()}*\n\n---\n",
    ]

    for post_path in posts:
        try:
            content = post_path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(content)
            title = fm.get("title", post_path.stem)
            fm_updated = False

            comment_sections.append(f"### {title}\n")

            if not fm.get("tldr"):
                tldr = gen_tldr(title, body)
                fm["tldr"] = tldr
                fm_updated = True
                comment_sections.append(f"**Generated TLDR:**\n> {tldr}\n\n")
            else:
                comment_sections.append("ℹ️ **TLDR already present** — skipping.\n\n")

            if not fm.get("tags"):
                tags = gen_tags(title, body)
                if tags:
                    fm["tags"] = tags
                    fm_updated = True
                    comment_sections.append(f"**Generated Tags:** {' '.join(f'`#{t}`' for t in tags)}\n\n")
            else:
                comment_sections.append("ℹ️ **Tags already present** — skipping.\n\n")

            if fm_updated:
                write_frontmatter_atomic(post_path, fm, body)
                git_commit_and_push(post_path, f"[automation] Update frontmatter for {post_path.name}")

            comment_sections.append("---\n")

        except Exception:
            err = traceback.format_exc()
            open_github_issue(
                title=f"Automation Script Failure: {_now_str()}",
                body=f"**Post:** `{post_path}`\n\n**Error:**\n```\n{err}\n```",
                labels=["automation", "bug"],
            )

    post_pr_comment("\n".join(comment_sections))


def run_dry_run() -> None:
    print("[DRY RUN] Local validation is now managed via local-loop/local_dry_run.py")


def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _safe_run(fn) -> None:
    try:
        fn()
    except Exception:
        err = traceback.format_exc()
        open_github_issue(
            title=f"Automation Script Failure: {_now_str()}",
            body=f"**Mode:** {fn.__name__}\n\n**Error:**\n```\n{err}\n```",
            labels=["automation", "bug"],
        )
        sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(description="srvrlss.dev content automation")
    parser.add_argument("--mode", choices=["pr"], default="pr")
    args = parser.parse_args()

    if not IS_CI:
        run_dry_run()
        return

    if args.mode == "pr":
        _safe_run(run_pr_automation)


if __name__ == "__main__":
    main()
