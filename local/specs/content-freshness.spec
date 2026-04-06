# Content Freshness Audit Specification

## Goal
Detect AI/Cloud Drift and Technical Decay in published blog posts periodically (every 3 weeks).

## Workflow
1.  **Enumerate Posts**: Scan `content/posts/*.md` for all published content.
2.  **Extract Metadata**: Parse frontmatter for `title`, `date`, `tags`, and a brief excerpt of the body.
3.  **Evaluate for Drift**:
    *   **AI/Cloud Drift**: Identify stale model names (e.g., deprecated Gemini versions), service APIs that have evolved, or outdated pricing.
    *   **Technical Decay**: Identify outdated code patterns, old tooling, or best practices that have shifted.
4.  **Reporting**:
    *   Generate a prioritized list of maintenance tasks (High/Medium/Low priority).
    *   Open GitHub Issues for each detected issue with labels `content-freshness` and `automation`.
    *   Assign maintenance to `AlexandreBrisebois`.

## Prompt Draft
Today is {today}. Flag blog posts with outdated content. Look for:
- AI/Cloud Drift: stale model names, service APIs, pricing
- Technical Decay: outdated code, tooling, or best practices
Return JSON array only:
[{"title":"...","issue_type":"AI/Cloud Drift"|"Technical Decay","priority":"high"|"medium"|"low","description":"1 sentence"}]
