# Cross-Post Linking Specification

## Goal
Enrich new blog posts with internal references to thematic content across srvrlss.dev.

## Workflow
1.  **Identify Related Posts**: Scan existing blog posts for the 2–3 most thematically related titles.
2.  **Update Frontmatter**: Append the identified post titles to the `related_posts` field in the new post's YAML frontmatter.
3.  **Ensure Context**: Load `llms-full.txt` (the text representation of the published site) to provide the AI model with modern and relevant context.
4.  **Consistency**: Use the same technical keywords and brand voice to categorize thematic relationships.

## Metadata Rules
*   Do not repeat the current post title in `related_posts`.
*   Ensure titles are specific and reflect a technical connection.
