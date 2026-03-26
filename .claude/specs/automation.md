# Automation Spec: AI & CI/CD

## 1. GitHub Actions Content Automation
- **Trigger**: Pull Request targeting `main`.
- **Ignore**: Commits from `github-actions[bot]`.
- **Script**: `.github/scripts/content_automation.py` (Python 3.14).
- **Secrets**: `GEMINI_API_KEY`, `NTFY_TOPIC`.

## 2. AI Logic (Dual Model)

### Content Context & Traceability (CRITICAL)
- **Context Awareness**: The Python script must load the latest `llms-full.txt` from the **live production site** (e.g., via `curl https://srvrlss.dev/llms-full.txt`) before processing new posts. This ensures bidirectional linking (related posts and `mentioned_in`) is accurate to what is already published.
- **Traceability (Frontmatter Update)**:
  - Generate the image prompt using `nanobananav2`.
  - **AUTOMATIC COMMIT**: The script must update the post's frontmatter (`image_prompt`) with the generated string and commit this change back to the PR branch via Git.
  - **PR Comment**: Post the full image generation prompt and all AI-generated hooks as a grouped PR comment for human review.

### Text Generation (Gemini 3.1 Flash)
- **LinkedIn Hooks**: 3 variations per the Brand Voice story arc.
- **X Thread**: **3-tweet thread** with "Distilled Conviction."
- **Bluesky Thread**: **3-post thread** with technical depth.
- **Tag Extraction**: 3-5 technical tags.
- **Conditional TLDR**: Generate 2-sentence summary if empty.
- **Semantic Linking**: 
  - Suggest 2-3 "Related Posts" for the *new* post.
  - Identification of 2-3 *older* posts in `llms-full.txt` that should reference this new post.

### Image Generation (nanobananav2)
- **File Generation**: Generate a unique, minimalist WebP header image and save it to `static/images/posts/[slug].webp`.
- **Aesthetic**: Abstract architectural diagrams, serverless event flows, high-contrast textures. No stock-photo humans. Focus on "Calm Signal" minimalist baseline.

## 3. Brand Voice Guardrails
- **Banned Words**: `Utilize`, `Deep-dive`, `Game-changing`, `Synergy`, `Very`, `Extremely`, `Robust`, `Additionally`, `Furthermore`, `Moreover`.
- **Voice Characteristics**: Reflective-vulnerable + Urgently excited. Senior authoritative yet approachable.
- **Formatting**: Direct, active sentences. Short paragraphs (1-4 sentences).

## 4. Maintenance & Monitoring
- **Social Discussion Loop**: **Every Friday at 15:00 UTC**. Summarize LinkedIn/X/Bluesky technical insights and "Discussion Vibe" via Gemini.
- **Delivery**: Private push notification via `ntfy.sh` (using `NTFY_TOPIC`).
- **Content Freshness Audit**: **Every 3 weeks**. Identify "AI/Cloud Drift" or "Technical Decay" and open prioritized GitHub Issues.
- **Site Evolution Meta-Log**: In the deployment workflow, summarize architectural changes (e.g., "Updated typography to Lora", "Restructured Agent Accessibility") and automatically append to a `/changelog` post or page.

## 5. Resilience & Local Checking
- **CI Dependency**: The script must check if it is running in GitHub Actions (e.g., `os.getenv("GITHUB_ACTIONS") == "true"`).
- **Graceful Failure**: If secrets are missing or API calls fail (e.g., Gemini rate limit), the script must **NOT** fail the build. Instead, it should **automatically open a GitHub Issue** titled "Automation Script Failure: [Timestamp]" detailing the error, log a warning, and proceed without updating the metadata.
- **Local Run**: When run locally, the script should perform a "dry run" that validates the `llms-full.txt` context but makes no external API calls, commits, or issue creations.
- **Atomicity**: Ensure all frontmatter updates are atomic and do not corrupt the Markdown files.
