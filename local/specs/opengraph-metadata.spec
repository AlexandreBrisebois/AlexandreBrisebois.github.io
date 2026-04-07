# OpenGraph Metadata Specification

## Goal
Ensure that all blog posts and pages have complete, valid, and high-quality OpenGraph and Twitter Card metadata to ensure premium social sharing experiences on LinkedIn, X (Twitter), and other platforms.

## Core Requirements
- **og:title**: Must be provided. Home: Site Title. Pages: Post Title — Site Title.
- **og:description**: Must be provided. Prioritize `description` front-matter, fallback to `tldr`, then Hugo `.Summary`.
- **og:url**: Must be an absolute URL and MUST end with a trailing slash `/` for GitHub Pages consistency.
- **og:type**: `article` for blog posts, `website` for all other pages.
- **og:site_name**: Must be "srvrlss.dev".
- **og:locale**: Must be "en_US".
- **og:image**:
    - Must be an absolute URL.
    - Format: WebP.
    - Post Priority: `social-image.webp` (in post bundle/dir) > `image` param > `/images/hero.webp`.
    - Home Priority: `/images/hero.webp`.
    - Recommended Size: 1200x630 (1.91:1) or 1200x675 (16:9).
- **og:image:alt**: Must be provided for all images.
- **og:image:width**: Automatically generated for resources or hardcoded for the default hero.
- **og:image:height**: Automatically generated for resources or hardcoded for the default hero.

## Twitter Card Requirements
- **twitter:card**: `summary_large_image`.
- **twitter:site**: Handle from site params (e.g., `@brisebois`).
- **twitter:creator**: Handle from site params (e.g., `@brisebois`).
- **twitter:url**: Same as `og:url`.
- **twitter:title**: Same as `og:title`.
- **twitter:description**: Same as `og:description`.
- **twitter:image**: Same as `og:image`.
- **twitter:image:alt**: Same as `og:image:alt`.

## Article Requirements (for posts)
- **article:published_time**: Required.
- **article:modified_time**: Required.
- **article:author**: `https://srvrlss.dev/about/`.
- **article:section**: Primary category or tag.
- **article:tag**: Array of tags from front-matter.

## Future Implementation
- **og:audio**: For podcast or narration-enabled posts. Reference absolute `.mp3` or `.m4a`.
- **og:video**: For posts with embedded videos. Reference absolute `.mp4` or YouTube/Vimeo URLs.

## Validation (Local Loop)
1. **Check Frontmatter**: All posts should have `tldr` or `description`.
2. **Check Images**: Any image referenced in `og:image` must exist in the `static/` directory or as a Page Resource.
3. **Check URLs**: Ensure no broken links in social metadata.
4. **Consistency**: All URLs must have the trailing slash.
