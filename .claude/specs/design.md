# Design Spec: "Calm Signal"

## Typography Stack
- **Headings (Display)**: `Instrument Serif` (Semi-bold, 600). Tightened letter-spacing.
- **Body Text**: `Source Serif 4` (Regular, 400). Optimized for long-form. Size: 18–20px. Line-height: 1.7–1.8.
- **Code/Monospace**: `JetBrains Mono` or `Berkeley Mono`.
- **Loading**: Use Google Fonts or self-hosted to prevent FOUT/rendering jank.

## Color Tokens (CSS Variables)

### Light Mode (Default)
```css
:root {
  --color-bg:        #F7F5F0;   /* warm off-white */
  --color-surface:   #EFECE5;   /* block differentiation */
  --color-ink:       #1A1A18;   /* near-black */
  --color-muted:     #6B6860;   /* secondary text */
  --color-accent:    #2D6A4F;   /* calm green */
  --color-accent-2:  #E76F51;   /* warm coral highlight */
  --color-border:    #DDD9D0;   /* subtle dividers */
  --color-code-bg:   #1E1E1C;   /* dark code blocks */
}
```

### Dark Mode
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg:        #0D1117;   /* deep navy/black */
    --color-surface:   #161B22;
    --color-ink:       #C9D1D9;
    --color-muted:     #8B949E;
    --color-accent:    #4D9375;
    --color-border:    #30363D;
    --color-code-bg:   #0D1117;
  }
}
```

## UI Accents
- **Glassmorphism**: Apply to callouts and code blocks.
  - `backdrop-filter: blur(8px) saturate(180%)`
  - `background-color: rgba(var(--color-surface-rgb), 0.7)` 
  - **1px border** with `rgba(var(--color-border-rgb), 0.3)`
- **Social Share Platforms**: X (Twitter), LinkedIn, Reddit, Bluesky, Copy Link.
- **Code Highlighting**: Use `github-dark` for consistent contrast in both modes.

## Layout & Navigation
- **Max Content Width**: **680px** (post body), **860px** (list pages).
- **Mobile Width**: Native feel at 375px. No horizontal scroll.
- **Shortcodes**: The `video` shortcode must be **centered** with a responsive 16:9 ratio and a subtle 1px border.
- **Header**: Wordmark (left) using `Instrument Serif` (Semi-bold, 600) with slightly tightened letter-spacing. Navigation (right): `Writing`, **`About`**, `RSS`.
- **Constraint**: The `About` link MUST point to **`/about/`**.
- **Anchor Statement**: A single-sentence "Statement of Intent" at the very top of the homepage (e.g., "A thinking space for technical outcomes..."). Style with `Instrument Serif`, sized between a heading and body text.
- **Lessons Learned Pivot**: Posts in the `retrospective` category or with "Retrospective" in the title must be visually tagged or titled as **"Lessons Learned"**.
- **Footer**: Simplified copyright, RSS link, `llms.txt`, and authoritative "Follow on LinkedIn" link.
