# Claude Code Prompt: Personal Blog (v2) — Hugo + GitHub Pages

> [!IMPORTANT]
> **AGENTIC INSTRUCTION**: You are a senior engineer and marketing designer. Maintain a `task.md` file in the root of the project to track your progress through these phases. Do not attempt to complete the entire prompt in one turn.
> 
> **AGENTIC BEST PRACTICES**:
> 1. **Context Refresh**: At the start of EVERY phase, re-read the relevant file in `specs/`. Do not rely on its presence in your earlier memory.
> 2. **Git Checkpoints**: At the completion of EVERY phase (Phase 1, 2, 3, etc.), perform a `git add .` and `git commit -m "Checkpoint: [Phase Name]"` to preserve the state.
> 3. **Validation**: Use the browser tool frequently to confirm visual outcomes before moving to the next sub-task.

## Context & References (Primary Source of Truth)

Leverage these to understand the author's identity and design preferences:
- **Current Blog:** [SRVRLSS.DEV](https://srvrlss.dev/)
- **GitHub Profile:** [Alexandre Brisebois](https://github.com/AlexandreBrisebois)
- **LinkedIn Profile:** [Alexandre Brisebois](https://www.linkedin.com/in/alexandrebrisebois/)
- **Docker Hub:** [brisebois](https://hub.docker.com/u/brisebois)
- **Blog Source Repository:** [AlexandreBrisebois.github.io](https://github.com/AlexandreBrisebois/AlexandreBrisebois.github.io)
- **Bluesky:** [Alexandre Brisebois](https://bsky.app/profile/alexandrebrisebois.bsky.social)

---

## Phase 0: Discovery & Roadmap

1.  **Environment Check**: Verify your tools. Run `hugo version`, `git --version`, and `python3 --version`.
2.  **Secrets Pre-Check**: Ask the user to confirm that `GEMINI_API_KEY` and `NTFY_TOPIC` are ready to be added to GitHub Secrets. Do NOT proceed to Phase 4 without this confirmation.
3.  **Strategic Research**: Use `find_by_name` and `view_file` to understand any existing context or files in the current directory before starting.
4.  **Read Specs**: **READ** the following files in the `specs/` directory to understand the high-fidelity requirements:
    - [specs/design.md](file://.claude/specs/design.md)
    - [specs/architecture.md](file://.claude/specs/architecture.md)
    - [specs/automation.md](file://.claude/specs/automation.md)
    - [specs/content.md](file://.claude/specs/content.md)

---

## Phase 1: Scaffolding & Core Architecture

Build the foundation. **REQUIRED**: Refer to [specs/architecture.md](file://.claude/specs/architecture.md) for the exact `config.yaml` schema, and [specs/content.md](file://.claude/specs/content.md) for the professional bio and sample post voice requirements.

### 1.1 Scaffold Structure
Create the following structure exactly:
*   Standard Hugo directories (`content/posts`, `layouts`, `static`, `archetypes`).
*   **Git Initialization**: Run `git init`. Create the `main` branch. 
*   **GitHub Pages Setup**: Create an empty `gh-pages` branch (`git checkout --orphan gh-pages && git rm -rf . && git commit --allow-empty -m "Initial gh-pages" && git checkout main`).
```
/
├── .github/workflows/deploy.yml
├── archetypes/default.md (YAML frontmatter)
├── content/
│   ├── about.md (Professional bio)
│   └── posts/ (hello-world.md, first-retrospective.md)
├── layouts/
│   ├── _default/ (baseof.html, list.html, single.html, single.md)
│   ├── index.html
│   ├── partials/ (head, header, footer, analytics, social-share, post-meta)
│   └── shortcodes/ (callout, video)
├── static/ (robots.txt, images/)
├── config.yaml
└── README.md
```

### 1.2 Validation
*   Run `hugo server -D`.
*   **VERIFICATION**: Use the browser tool to visit `http://localhost:1313`. Ensure the homepage and sample posts render.
*   **STOP & WAIT**: Report completion of Phase 1 and wait for user approval before moving to Design.

---

## Phase 2: Design "Calm Signal" & CSS

Now, apply the aesthetic. **REQUIRED**: Refer to [specs/design.md](file://.claude/specs/design.md) for hex codes, typography, glassmorphism, and the homepage **Anchor Statement**.

### 2.1 Design Specs: "Calm Signal"
*   **Typography**: `Instrument Serif` (600) for headings, `Source Serif 4` (400) for body.
*   **Color Palette**: Implement the system-aware dark mode as specified in the original design tokens (Light: `#F7F5F0`, Dark: `#0D1117`).
*   **Glassmorphism**: Use `backdrop-filter` for callouts and code blocks.
*   **Contrast**: `github-dark` syntax highlighting. Ensure sharp contrast in Light mode.

### 2.2 Visual Feedback Loop
*   After implementing the CSS, use the browser tool to capture screenshots of the site in both mobile and desktop views.
*   **CRITIQUE**: Compare your results against the "Calm Signal" principles AND the "Lessons Learned Pivot" requirements in `specs/design.md`.
*   **STOP & WAIT**: Present your critique and screenshots to the user. Wait for approval before starting Phase 3.

---

## Phase 3: SEO, Agents & Accessibility

Make the blog discoverable by humans and accessible to AI agents. **REQUIRED**: Refer to [specs/architecture.md](file://.claude/specs/architecture.md) for the JSON-LD schemas, RSS full-content logic, and the `single.md` raw Markdown layout.

### 3.1 LLMS Visibility
*   **llms.txt & llms-full.txt**: Implement via Hugo Output Formats as specified in the architecture spec. Ensure they regenerate on every build.
*   **Markdown Outputs**: Ensure every post is available as raw Markdown at `/posts/[slug]/index.md`.

### 3.2 Advanced SEO
*   **JSON-LD**: Implement Article, Person, and Breadcrumb schemas from the spec.
*   **Speculation Rules API**: Add the pre-rendering script to `<head>`.
*   **Accessibility**: "Skip to Content" link and `loading="lazy"` on all images.

---

## Phase 4: CI/CD & AI-Powered Automations

Finalize the Ops and the "Agentic Loop." **REQUIRED**: Refer to [specs/automation.md](file://.claude/specs/automation.md) for the Python 3.14 script requirements, bidirectional linking logic, and **automatic frontmatter commit-back traceability**.

### 4.1 Deployment
*   **GitHub Actions**: Build and deploy to `gh-pages` branch on push to `main`.
*   **Hugo Version**: Use `peaceiris/actions-hugo@v3` with `extended: true` and `hugo-version: 'latest'`.

### 4.2 Content Automation (PR Triggered)
*   **Implementation**: Write the custom Python 3.14 script as described in the automation spec.
*   **Models**: Use `gemini-3.1-flash` (text) and `nanobananav2` (images).
*   **Secrets**: Use `GEMINI_API_KEY` and `NTFY_TOPIC` from GitHub Repository Secrets.
*   **Tasks**:
    *   **LinkedIn/X/Bluesky Hook generation**: Following the srvrlss.dev Brand Voice (no banned words).
    *   **Semantic Linking**: Suggest 2-3 "Related Posts" and identify 2-3 "Mentioned In" candidates.
    *   **Image Generation Prompting**: Generate a prompt for a minimalist, abstract architectural diagram.
*   **Reporting**: The script should post all findings back as a grouped PR comment.
*   **Brand Voice**: Strictly enforce the banned words list in `specs/automation.md`.

> [!CAUTION]
> **Self-Correction Guardrail**: If `NTFY_TOPIC` is not found, disable the private notification but continue with the PR comment. If `GEMINI_API_KEY` is missing, report this as a PR failure.

---

## Performance Guardrails
1.  **Direct, Active Sentence Rule**: All generated content must be srvrlss.dev Brand Voice compliant. (No "Utilize," "Deep-dive," "Game-changing").
2.  **No Placeholders**: Write the actual bio (reflective-vulnerable) and the actual sample posts.
---

## Shortcodes & Content Requirements
**REQUIRED**: Implement these specific Hugo shortcodes as defined in the original spec:
- **`callout.html`**: Types: `note`, `warning`, `tip`. Left-border accent, minimalist style.
- **`video.html`**: Responsive 16:9 iframe embed.

**Sample Posts**: Write two real Markdown posts:
1. `hello-world.md`: "Why I Built This Blog" (Anti-CMS manifesto, ~300 words).
2. `first-retrospective.md`: "Lessons Learned: A Project That Went Sideways" (Demonstrate `callout` shortcode, ~500 words).

---

## Quality Bar (Final Verification)

Before declaring the project complete, the agent must verify:
- [ ] `hugo server -D` runs with zero errors/warnings.
- [ ] `hugo --minify` builds cleanly to `/public`.
- [ ] Homepage correctly lists sample posts with "Calm Signal" styling from `specs/design.md`.
- [ ] **Mobile Check**: Site is fully readable on 375px width (no horizontal scroll).
- [ ] **Dark Mode**: System theme transitions work correctly via CSS variables.
- [ ] **Glassmorphism**: Backdrop filters (8px blur) and 1px borders are applied.
- [ ] **LLMS Check**: `/llms.txt` and `/llms-full.txt` are valid and up-to-date.
- [ ] **Speculation Rules**: Script is present and correctly formatted in `<head>`.
- [ ] **Automation Logic**: `.github/scripts/content_automation.py` is written and syntax-checked with `python3.14 -m py_compile`.
- [ ] **Maintenance Checks**: Identify "AI/Cloud Drift" or "Technical Decay" (per `specs/automation.md`).
- [ ] **Accessibility**: "Skip to Content" link present and `loading="lazy"` on all images.
- [ ] **WCAG Check**: Verify color contrast meets **WCAG 2.1 AA** (especially for accent text).
- [ ] **Drafts**: Verify that `hugo server -D` shows draft posts as expected.
- [ ] **Analytics**: Cloudflare beacon script is present in `<head>` (when token is provided).

---

## What Not to Build
- No comments system (use LinkedIn Discussion CTA).
- No search feature.
- No pagination beyond basic Hugo defaults.
- No newsletter signup or cookie banners.
- No JavaScript frameworks or bundlers.

---

## Future Roadmap (Parking Lot)
These features are NOT part of the initial build but must be kept in mind for architecture:
- **Voice Audit**: A GitHub Action step to score posts against the "Technical Outcome Leader" persona.
- **Interactive Demos**: A pattern for allowing small, isolated JS "islands" for technical demonstrations.

3.  **Session Integrity**: If you crash or lose context, read the `task.md` to resume exactly where you left off.
