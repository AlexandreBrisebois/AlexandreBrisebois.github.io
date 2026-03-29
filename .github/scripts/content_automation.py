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
NTFY_TOPIC: str = os.getenv("NTFY_TOPIC", "")
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
PR_NUMBER: str = os.getenv("PR_NUMBER", "")
REPO: str = os.getenv("REPO", "")
BASE_BRANCH: str = os.getenv("BASE_BRANCH", "main")
FORCE_POSTS: str = os.getenv("FORCE_POSTS", "")

PRODUCTION_LLMS_URL = "https://srvrlss.dev/llms-full.txt"

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

# Ordered preference list for image generation — first match wins.
# Models using generateContent (Gemini native image) come first.
GEMINI_IMAGE_MODEL_PREFERENCE = [
    "gemini-3-pro-image-preview",   # generateContent + responseModalities
    "imagen-4.0-generate-001",
    "imagen-4.0-fast-generate-001",
    "imagen-3.0-generate-002",
    "imagen-3.0-generate-001",
    "imagen-3.0-fast-generate-001",
    "imagegeneration@006",
]

# Models that use generateContent + responseModalities instead of generateImages/predict
GEMINI_NATIVE_IMAGE_MODELS = {
    "gemini-3-pro-image-preview",
}

_resolved_gemini_model: str | None = None
_resolved_image_model: str | None = None

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
    """
    Query the Gemini models list and return the best available text model.
    Walks GEMINI_MODEL_PREFERENCE in order; falls back to the first
    generateContent-capable model if none match.
    """
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

    # Nothing matched the preference list — pick any flash, then any available
    for candidate in sorted(available):
        if "flash" in candidate:
            print(f"[WARN] Preferred models unavailable; falling back to: {candidate}")
            _resolved_gemini_model = candidate
            return candidate

    if available:
        fallback = sorted(available)[0]
        print(f"[WARN] No flash model found; falling back to: {fallback}")
        _resolved_gemini_model = fallback
        return fallback

    raise RuntimeError(f"No generateContent-capable Gemini models found. Available: {available}")


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


def call_gemini_vision(img_bytes: bytes, mime_type: str, prompt: str, temperature: float = 0.4) -> str:
    """Generate text from an image + text prompt via Gemini multimodal REST API."""
    import base64
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")
    model = discover_gemini_model()
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": mime_type, "data": base64.b64encode(img_bytes).decode()}},
            ]
        }],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 256},
    }
    result = _http_json(url, payload)
    return result["candidates"][0]["content"]["parts"][0]["text"]


def discover_image_model() -> tuple[str, str] | None:
    """
    Query the Gemini models list and return (model_name, method) for the best
    available image generation model, where method is the API endpoint suffix
    ('generateImages' or 'predict'). Returns None if nothing is available.
    """
    global _resolved_image_model
    if _resolved_image_model is not None:
        return tuple(_resolved_image_model.split("|", 1)) if _resolved_image_model else None  # type: ignore

    if not GEMINI_API_KEY:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    try:
        data = json.loads(_http_get(url, timeout=15))
    except Exception as e:
        print(f"[WARN] Could not list models for image discovery: {e}", file=sys.stderr)
        _resolved_image_model = ""
        return None

    # Build map of model_id -> supported image method
    model_methods: dict[str, str] = {}
    for m in data.get("models", []):
        name = m["name"].split("/")[-1]
        methods = m.get("supportedGenerationMethods", [])
        if name in GEMINI_NATIVE_IMAGE_MODELS and "generateContent" in methods:
            model_methods[name] = "generateContent"
        elif "generateImages" in methods:
            model_methods[name] = "generateImages"
        elif "predict" in methods and ("imagen" in name or "imagegeneration" in name):
            model_methods[name] = "predict"

    for preferred in GEMINI_IMAGE_MODEL_PREFERENCE:
        if preferred in model_methods:
            method = model_methods[preferred]
            print(f"[INFO] Using image model: {preferred} (method: {method})")
            _resolved_image_model = f"{preferred}|{method}"
            return preferred, method

    # Fall back to any discovered imagen model
    for candidate in sorted(model_methods.keys()):
        if "imagen" in candidate or "imagegeneration" in candidate:
            method = model_methods[candidate]
            print(f"[WARN] Falling back to image model: {candidate} (method: {method})")
            _resolved_image_model = f"{candidate}|{method}"
            return candidate, method

    print("[WARN] No image generation model found in available Gemini models.")
    _resolved_image_model = ""
    return None


def _extract_image_bytes(result: dict) -> bytes | None:
    """Extract base64-encoded image bytes from generateImages, predict, or generateContent response."""
    import base64
    # generateContent response: candidates[0].content.parts[].inlineData.data
    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData", {})
            raw = inline.get("data", "")
            if raw:
                return base64.b64decode(raw)
    # generateImages response: {"generatedImages": [{"image": {"imageBytes": "..."}}]}
    for images_key in ("generatedImages", "images"):
        images = result.get(images_key, [])
        if images:
            for key in ("imageBytes", "data"):
                raw = images[0].get("image", {}).get(key) or images[0].get(key, "")
                if raw:
                    return base64.b64decode(raw)
    # predict response: {"predictions": [{"bytesBase64Encoded": "..."}]}
    for pred in result.get("predictions", []):
        raw = pred.get("bytesBase64Encoded") or pred.get("imageBytes", "")
        if raw:
            return base64.b64decode(raw)
    return None


def generate_image_via_api(prompt: str) -> bytes | None:
    """
    Generate a WebP image using the best available Imagen model.
    Tries generateImages payload first, then predict payload on 404.
    Returns raw bytes on success, None on failure.
    """
    if not GEMINI_API_KEY:
        return None

    result = discover_image_model()
    if not result:
        return None
    model, method = result

    base_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:{method}?key={GEMINI_API_KEY}"
    )

    # Payload varies by method
    if method == "generateContent":
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }
    elif method == "generateImages":
        payload = {"prompt": prompt, "number_of_images": 1}
    else:  # predict
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 1},
        }

    try:
        data = _http_json(base_url, payload)
        img = _extract_image_bytes(data)
        if img:
            return img
        print(f"[WARN] Image model {model} returned no image bytes.", file=sys.stderr)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Model listed but endpoint unavailable — likely permissions/billing
            print(
                f"[WARN] {model}:{method} returned 404. "
                "Image generation may require billing or API enablement.",
                file=sys.stderr,
            )
        else:
            print(f"[WARN] Image generation via {model} failed: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] Image generation via {model} failed: {e}", file=sys.stderr)
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
    buf.write("---\n")
    buf.write(body)
    tmp = filepath.with_suffix(".tmp")
    tmp.write_text(buf.getvalue(), encoding="utf-8")
    tmp.replace(filepath)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def get_changed_posts() -> list[pathlib.Path]:
    """
    Return posts to process. Checks FORCE_POSTS first (manual override),
    then falls back to git diff vs the base branch.
    """
    if FORCE_POSTS:
        paths = []
        for name in FORCE_POSTS.split(","):
            name = name.strip()
            if not name:
                continue
            p = pathlib.Path("content/posts") / name
            if p.exists():
                paths.append(p)
            else:
                print(f"[WARN] FORCE_POSTS: {p} does not exist, skipping.", file=sys.stderr)
        print(f"[INFO] FORCE_POSTS override: {[str(p) for p in paths]}")
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


def critique_image(img_bytes: bytes, image_prompt: str) -> dict:
    """
    Ask Gemini to evaluate the generated image against the image prompt.
    Returns {"keep": bool, "feedback": str}.
    """
    prompt = f"""Does this image match the following description?

{image_prompt}

Reply JSON only: {{"keep": true or false, "feedback": "2-3 sentences: what is wrong and specifically what the next image must do differently to match the description."}}
Only keep if the image clearly matches the description."""

    raw = call_gemini_vision(img_bytes, "image/webp", prompt)
    match = re.search(r"\{[\s\S]*?\}", raw)
    if match:
        try:
            result = json.loads(match.group())
            if "keep" in result and "feedback" in result:
                return result
        except json.JSONDecodeError:
            pass
    return {"keep": False, "feedback": raw.strip()[:300]}


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
# Hero image generation helpers
# ---------------------------------------------------------------------------

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
    Single Gemini call returning both the image prompt and the current_focus line.
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

    print(f"[INFO] Generating hero image from {len(posts)} post(s).")
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
    subprocess.run(
        ["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
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

            # --- Image prompt ---
            prompt_file = post_path.parent / f"{slug}-image-prompt.md"
            if not prompt_file.exists():
                comment_sections.append(
                    f"⚠️ **No image prompt file found:** `{prompt_file}` — skipping image.\n\n"
                )
                image_prompt = None
            else:
                image_prompt = prompt_file.read_text(encoding="utf-8").strip()
                comment_sections.append(
                    f"**Image Prompt** (from `{prompt_file.name}`):\n"
                    f"```\n{image_prompt}\n```\n\n"
                )

            # --- Image generation (2-shot with critique) ---
            if image_prompt:
                img_dir = pathlib.Path("static/images/posts")
                img_dir.mkdir(parents=True, exist_ok=True)
                img_path = img_dir / f"{slug}.webp"
                img_initial_path = img_dir / f"{slug}-initial.webp"

                img_bytes = generate_image_via_api(image_prompt)
                if img_bytes:
                    critique = critique_image(img_bytes, image_prompt)
                    comment_sections.append(
                        f"**Image Critique (shot 1):** {critique['feedback']}\n\n"
                    )
                    if critique["keep"]:
                        img_path.write_bytes(img_bytes)
                        fm["image"] = f"/images/posts/{slug}.webp"
                        fm_updated = True
                        comment_sections.append(f"✅ **Image accepted (shot 1):** `{img_path}`\n\n")
                        subprocess.run(["git", "add", str(img_path)], check=False)
                    else:
                        img_initial_path.write_bytes(img_bytes)
                        subprocess.run(["git", "add", str(img_initial_path)], check=False)

                        retry_prompt = f"{image_prompt}\n\nRevision: {critique['feedback']}"
                        img_bytes_2 = generate_image_via_api(retry_prompt)
                        if img_bytes_2:
                            img_path.write_bytes(img_bytes_2)
                            fm["image"] = f"/images/posts/{slug}.webp"
                            fm_updated = True
                            comment_sections.append(f"✅ **Image accepted (shot 2):** `{img_path}`\n\n")
                            subprocess.run(["git", "add", str(img_path)], check=False)
                        else:
                            img_path.write_bytes(img_bytes)
                            fm["image"] = f"/images/posts/{slug}.webp"
                            fm_updated = True
                            comment_sections.append(
                                "⚠️ **Shot 2 generation failed — using shot 1 as fallback.**\n\n"
                            )
                            subprocess.run(["git", "add", str(img_path)], check=False)
                else:
                    comment_sections.append(
                        f"ℹ️ **Image generation failed.** Save an image manually to `{img_path}`.\n\n"
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

    prompt = f"""Today is {today.strftime('%Y-%m-%d')}. Flag blog posts with outdated content.

Look for:
- AI/Cloud Drift: stale model names, service APIs, pricing
- Technical Decay: outdated code, tooling, or best practices

Posts:
{chr(10).join(post_summaries)}

Return JSON array only:
[{{"title":"...","issue_type":"AI/Cloud Drift"|"Technical Decay","priority":"high"|"medium"|"low","description":"1 sentence"}}]
If none, return []."""

    raw = call_gemini(prompt, temperature=0.3, max_tokens=1024)
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
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        slug = fm.get("slug") or p.stem
        prompt_file = p.parent / f"{slug}-image-prompt.md"
        print(
            f"  - {p.name}\n"
            f"    title:        {fm.get('title', '?')!r}\n"
            f"    image prompt: {'found' if prompt_file.exists() else 'MISSING'} ({prompt_file.name})\n"
            f"    image:        {'set' if fm.get('image') else 'not yet set'}"
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
        choices=["pr", "social-loop", "freshness-audit", "hero-image"],
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
    elif args.mode == "hero-image":
        _safe_run(run_hero_image_generation)


if __name__ == "__main__":
    main()
