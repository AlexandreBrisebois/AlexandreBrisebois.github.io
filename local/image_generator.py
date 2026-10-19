#!/usr/bin/env python3
"""
srvrlss.dev Image Generation Tool
================================
Restored multi-shot image generation and critique loop.
Uses Google's Gemini / Imagen API.
"""

import argparse
import base64
import io
import json
import os
import pathlib
import re
import sys
import traceback

# Setup path to import content_automation
project_root = pathlib.Path(__file__).parent.parent
sys.path.append(str(project_root / ".github" / "scripts"))

try:
    import content_automation as ca
except ImportError:
    print("[ERROR] Could not import content_automation.py. Check paths.", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GEMINI_IMAGE_MODEL_PREFERENCE = [
    "gemini-3-pro-image-preview",   # nanobananav2 — generateContent + responseModalities
    "imagen-4.0-generate-001",
    "imagen-4.0-fast-generate-001",
    "imagen-3.0-generate-002",
    "imagen-3.0-generate-001",
    "imagen-3.0-fast-generate-001",
    "imagegeneration@006",
]

GEMINI_NATIVE_IMAGE_MODELS = {
    "gemini-3-pro-image-preview",
}

_resolved_image_model = None

# ---------------------------------------------------------------------------
# Logic
# ---------------------------------------------------------------------------

def get_image_prompt(frontmatter):
    """Support both legacy and hyphenated frontmatter keys."""
    return (frontmatter.get("image_prompt") or frontmatter.get("image-prompt") or "").strip()


def sniff_image_mime(img_bytes):
    """Infer MIME type from common image signatures."""
    if img_bytes.startswith(b"RIFF") and img_bytes[8:12] == b"WEBP":
        return "image/webp"
    if img_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if img_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return "application/octet-stream"


def extension_for_mime(mime_type):
    if mime_type == "image/png":
        return ".png"
    if mime_type == "image/jpeg":
        return ".jpg"
    return ".webp"


def convert_to_webp(img_bytes, mime_type):
    """Convert provider output to real WebP bytes using Pillow."""
    if mime_type == "image/webp":
        return img_bytes

    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "WebP conversion requires Pillow. Install it with './.venv/bin/pip install Pillow'."
        ) from exc

    with Image.open(io.BytesIO(img_bytes)) as image:
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")

        output = io.BytesIO()
        image.save(output, format="WEBP", quality=90, method=6)
        return output.getvalue()

def discover_image_model():
    """
    Query the Gemini models list and return (model_name, method).
    """
    global _resolved_image_model
    if _resolved_image_model is not None:
        return tuple(_resolved_image_model.split("|", 1)) if _resolved_image_model else None

    if not ca.GEMINI_API_KEY:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={ca.GEMINI_API_KEY}"
    try:
        data = json.loads(ca._http_get(url, timeout=15))
    except Exception as e:
        print(f"[WARN] Could not list models for image discovery: {e}", file=sys.stderr)
        _resolved_image_model = ""
        return None

    model_methods = {}
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

    for candidate in sorted(model_methods.keys()):
        if "imagen" in candidate or "imagegeneration" in candidate:
            method = model_methods[candidate]
            print(f"[WARN] Falling back to image model: {candidate} (method: {method})")
            _resolved_image_model = f"{candidate}|{method}"
            return candidate, method

    print("[WARN] No image generation model found in available Gemini models.")
    _resolved_image_model = ""
    return None


def generate_image_via_api(prompt):
    """
    Generate image bytes via Google Generative Language API.
    """
    if not ca.GEMINI_API_KEY:
        return None

    result = discover_image_model()
    if not result:
        return None
    model, method = result

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:{method}?key={ca.GEMINI_API_KEY}"
    )

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
        response = ca._http_json(url, payload)
        
        if method == "generateContent":
            for part in response.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"]["data"])
        elif method == "generateImages":
            img_data = response.get("generatedImages", [{}])[0].get("imageRawData")
            if img_data:
                return base64.b64decode(img_data)
        else: # predict
            predictions = response.get("predictions", [])
            if predictions:
                # predict usually returns base64 string in a dict
                data = predictions[0]
                if isinstance(data, dict) and "bytesBase64Encoded" in data:
                    return base64.b64decode(data["bytesBase64Encoded"])
                elif isinstance(data, str):
                    return base64.b64decode(data)
    except Exception as e:
        print(f"[ERROR] API call failed: {e}", file=sys.stderr)
    return None


def review_image_prompt(prompt):
    """Review the image prompt before the first paid generation call."""
    review_prompt = f"""Review this image-generation prompt for srvrlss.dev before any image is generated.

Original Prompt: {prompt}

Audit criteria:
1. The image should feel minimalist and abstract.
2. No faces, people, or logos should appear.
3. The palette should use a warm off-white base with restrained accents from forest, coral, oceanic, plum, slate, gold, eucalyptus, sienna, mulberry, and bronze.
4. The composition should work as a landscape-oriented blog hero image.
5. The prompt should be specific enough to reduce retries while staying visually clean.

Return JSON only:
{{
  "pass": true|false,
  "feedback": "1-2 sentences explaining what is missing if pass is false",
  "updated_prompt": "Either the original prompt if pass is true, or a revised prompt that better matches the criteria"
}}"""

    try:
        text = ca.call_gemini(review_prompt, temperature=0.2, max_tokens=900)
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            result = json.loads(match.group())
            updated_prompt = (result.get("updated_prompt") or prompt).strip()
            return {
                "pass": bool(result.get("pass", True)),
                "feedback": (result.get("feedback") or "Prompt review passed.").strip(),
                "updated_prompt": updated_prompt or prompt,
            }
    except Exception as e:
        print(f"[WARN] Prompt review failed: {e}", file=sys.stderr)

    return {"pass": True, "feedback": "Prompt review unavailable.", "updated_prompt": prompt}


def critique_image(img_bytes, prompt):
    """
    Use Gemini Vision to critique the generated image.
    """
    b64_img = base64.b64encode(img_bytes).decode("utf-8")
    mime_type = sniff_image_mime(img_bytes)
    
    critique_prompt = f"""Evaluate this generated image against the following prompt.

Original Prompt: {prompt}

Audit criteria (srvrlss.dev aesthetic):
1. Does it feel minimalist and abstract?
2. Are there any faces, people, or logos? (Strictly forbidden: FAIL if present).
3. Does it use the srvrlss.dev palette in a restrained, intentional way:
   warm off-white base, plus accents drawn from forest, coral, oceanic, plum,
   slate, gold, eucalyptus, sienna, mulberry, and bronze?
4. Do the colors feel distinct, balanced, and brand-aligned rather than generic or muddy?
5. Is it landscape orientation?

Return JSON only:
{{
  "keep": true|false,
  "feedback": "1-2 sentence explanation of what to improve if keep is false"
}}"""

    model = ca.discover_gemini_model() # Use regular gemini for vision
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={ca.GEMINI_API_KEY}"
    )
    
    payload = {
        "contents": [{
            "parts": [
                {"text": critique_prompt},
                {"inlineData": {"mimeType": mime_type, "data": b64_img}}
            ]
        }]
    }

    try:
        result = ca._http_json(url, payload)
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"[WARN] Critique failed: {e}", file=sys.stderr)
    
    return {"keep": True, "feedback": "Critique unavailable, keeping image."}


def run_image_generation(posts):
    """
    Processes a list of post paths for image generation.
    """
    if not ca.GEMINI_API_KEY:
        print("[ERROR] GEMINI_API_KEY not set.")
        return

    for post_path in posts:
        try:
            print(f"\n[IMAGE] Processing: {post_path.name}")
            content = post_path.read_text(encoding="utf-8")
            fm, body = ca.parse_frontmatter(content)
            
            image_prompt = get_image_prompt(fm)
            if not image_prompt:
                print(f"[SKIP] No image_prompt/image-prompt in {post_path.name}")
                continue

            slug = fm.get("slug") or post_path.stem
            img_dir = project_root / "static" / "images" / "posts"
            img_dir.mkdir(parents=True, exist_ok=True)

            print("[INFO] Reviewing image prompt before Shot 1...")
            prompt_review = review_image_prompt(image_prompt)
            reviewed_prompt = prompt_review["updated_prompt"]
            if prompt_review["pass"]:
                print("[OK] Prompt review passed.")
            else:
                print(f"[REVIEW] Prompt updated before Shot 1: {prompt_review['feedback']}")
                image_prompt = reviewed_prompt

            print(f"[INFO] Prompt: {image_prompt[:60]}...")
            
            # Shot 1
            print("[INFO] Generating Shot 1...")
            img_bytes = generate_image_via_api(image_prompt)
            if not img_bytes:
                print("[ERROR] Generation failed.")
                continue

            # Critique
            print("[INFO] Critiquing Shot 1...")
            critique = critique_image(img_bytes, image_prompt)
            
            if critique["keep"]:
                print(f"[OK] Accepted Shot 1: {critique['feedback']}")
            else:
                print(f"[RETRY] Rejected Shot 1: {critique['feedback']}")
                retry_prompt = f"{image_prompt}\n\nRevision: {critique['feedback']}"
                print("[INFO] Generating Shot 2...")
                img_bytes_2 = generate_image_via_api(retry_prompt)
                if img_bytes_2:
                    img_bytes = img_bytes_2
                    print("[OK] Shot 2 generated.")
                else:
                    print("[WARN] Shot 2 failed, using Shot 1 fallback.")

            # Save as WebP regardless of the provider's native output format.
            mime_type = sniff_image_mime(img_bytes)
            img_bytes = convert_to_webp(img_bytes, mime_type)
            extension = ".webp"
            img_path = img_dir / f"{slug}{extension}"
            img_path.write_bytes(img_bytes)
            print(f"[SUCCESS] Image saved to {img_path}")
            
            # Update Frontmatter
            fm["image"] = f"/images/posts/{slug}{extension}"
            ca.write_frontmatter_atomic(post_path, fm, body)
            print(f"[SUCCESS] Updated frontmatter for {post_path.name}")

        except Exception as e:
            print(f"[ERROR] Failed {post_path.name}: {e}")
            traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="srvrlss.dev Image Generator")
    parser.add_argument("--posts", help="Comma-separated filenames in content/posts/")
    args = parser.parse_args()

    if args.posts:
        posts = []
        for name in args.posts.split(","):
            p = project_root / "content" / "posts" / name.strip()
            if p.exists():
                posts.append(p)
            else:
                print(f"[WARN] Post not found: {name}")
    else:
        # Fallback to ca logic for changed posts
        posts = ca.get_changed_posts()

    if not posts:
        print("[INFO] No posts to process.")
        return

    run_image_generation(posts)

if __name__ == "__main__":
    main()
