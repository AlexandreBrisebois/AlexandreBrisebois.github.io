# srvrlss.dev

Personal blog of Alexandre Brisebois

**Site**: [srvrlss.dev](https://srvrlss.dev/)
**Author**: [Alexandre Brisebois](https://github.com/AlexandreBrisebois)

Built with [Hugo](https://gohugo.io/), deployed to GitHub Pages.

---

## 🎨 Design System: "Calm Signal"

The site uses a custom, theme-aware design system called **"Calm Signal"**, designed for high readability and professional aesthetics.

### 🌓 Insight Signals (Auto-Badging)
The site uses a custom, theme-aware palette calibrated for **WCAG 2.1 AA contrast** (minimum 4.5:1). "Insight Pills" are automatically applied based on post tags or titles to provide immediate value signals.

| Signal | Color Variable | Brand Hue | Logic & Value Signal |
| :--- | :--- | :--- | :--- |
| **Lesson Learned** | `--color-forest` | Forest Green | `lesson-learned`, `retrospective`. Growth & evolution. |
| **Experiment** | `--color-gold` | Harvest Gold | `experiment`, "Experiment" in title. Discovery & trials. |
| **Quick Win** | `--color-coral` | Calibrated Coral | `quick-win`. High-impact, low-effort priority. |
| **Deep Dive** | `--color-oceanic` | Oceanic Blue | `deep-dive`. Technical rigor & deep analysis. |
| **Blueprint** | `--color-mulberry` | Muted Mulberry | `blueprint`. Reusable, structural solutions. |
| **Archive** | `--color-plum` | Shadow Plum | `archive`. Historical reference or older content. |
| **Meta** | `--color-slate` | Ink Slate | `meta`, `site`. Content about the blog or system. |
| **Experimental+** | `--color-eucalyptus`| Eucalyptus | Alternative trial signal for specialized discovery. |
| **Retrospective+**| `--color-sienna` | Burnt Sienna | Alternative growth signal for depth of failure. |
| **Research+** | `--color-bronze` | Antique Bronze | Alternative rigor signal for foundational research. |

### Custom Shortcodes
Enhance your content with these built-in shortcodes:

#### **Callouts**
Standardized blocks for notes, tips, and warnings.
```markdown
{{< callout type="note|tip|warning" >}}
Your content here.
{{< /callout >}}
```

#### **Videos**
Responsive video embeds.
```markdown
{{< video src="https://example.com/video.mp4" title="Video Title" >}}
```

---

## 🛠️ Local Development

### Local Dev Suite (`local/loop.sh`)
The repository includes a local development script to streamline builds and automation. Run it from the root directory:

```bash
bash local/loop.sh
```

**Options include:**
1.  **Start Hugo Server**: Launches the dev server at `http://localhost:1313` with drafts enabled.
2.  **Run Automation (Dry Run)**: Safely validate GitHub Actions automation locally.
3.  **Run Automation (Full)**: Execute the full content automation pipeline (requires `GEMINI_API_KEY`).
4.  **Run Image Generation**: Start the multi-shot image generation and critique loop.

### Prerequisites
- [Hugo](https://gohugo.io/installation/) (Extended version recommended)
- Python 3.x (for automation scripts)
- `.env` file in `local/` for API keys (e.g., `GEMINI_API_KEY`)
