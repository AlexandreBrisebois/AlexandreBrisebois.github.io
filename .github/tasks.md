# Tasks: Update Image Generation

Branch: `claude/update-image-generation-nF1rJ`
File: `.github/scripts/content_automation.py`

## Phases

- [x] A — Setup: branch + tasks.md
- [x] B — Remove TLDR, tags, social hooks generation
- [x] C — Read image prompt from `{slug}-image-prompt.md`
- [x] D — Update model constants (gemini-3.1-pro-image, GEMINI_CRITIQUE_MODEL)
- [x] E — Update `critique_image()` (yes/no, gemini-3.1-flash, tighter tokens)
- [x] F — Update retry logic (original prompt + critique, no refined-prompt call)
- [x] G — Mode 3 token reduction (remove BRAND_VOICE_RULES, condense prompt, max_tokens=1024)
- [x] H — Commit and push
