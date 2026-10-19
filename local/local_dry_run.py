#!/usr/bin/env python3
"""
Local Dry-Run for srvrlss.dev Content Automation
Validates changes to blog posts locally before pushing to GitHub.
"""

import sys
import os
import pathlib

sys.path.append(str(project_root / ".github" / "scripts"))

try:
    import content_automation as ca
except ImportError:
    print("[ERROR] Could not import content_automation.py. Ensure the path is correct.", file=sys.stderr)
    sys.exit(1)

def run_local_validation():
    print("[LOCAL VALIDATION] Running validation — no API calls will be made.")
    
    # Try to check production context if possible
    try:
        print(f"[LOCAL VALIDATION] Checking production context connection...")
        # Note: PRODUCTION_LLMS_URL is being removed from the main script, 
        # so this is just a placeholder for local logic.
        url = "https://srvrlss.dev/llms-full.txt"
        context = ca._http_get(url, timeout=5)
        print(f"[LOCAL VALIDATION] ✓ Production context accessible: {len(context)} chars")
    except Exception as e:
        print(f"[LOCAL VALIDATION] ⚠ Production context unavailable: {e}")

    posts = ca.get_changed_posts()
    print(f"[LOCAL VALIDATION] Changed posts vs origin/{ca.BASE_BRANCH}: {len(posts)}")
    
    for p in posts:
        try:
            content = p.read_text(encoding="utf-8")
            fm, _ = ca.parse_frontmatter(content)
            
            tldr_status = "present" if fm.get("tldr") else "MISSING"
            tags_status = f"{len(fm.get('tags', []))} tags" if fm.get("tags") else "EMPTY"
            
            print(f"  - {p.name}")
            print(f"    title: {fm.get('title', '?')!r}")
            print(f"    tldr:  {tldr_status}")
            print(f"    tags:  {tags_status}")
        except Exception as e:
            print(f"  - {p.name}: ERROR parsing: {e}")

    print("\n[LOCAL VALIDATION] Complete.")

if __name__ == "__main__":
    run_local_validation()
