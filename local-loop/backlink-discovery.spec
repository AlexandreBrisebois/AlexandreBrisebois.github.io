# Backlink Discovery Specification

## Goal
Automatically identify existing blog posts that should be updated to link to a newly created post.

## Workflow
1.  **Analyze Context**: Provide the titles and first 1,000 characters of all existing published blog posts (via `llms-full.txt`).
2.  **Evaluate for Relevance**:
    *   Find 2–3 existing posts where referencing the *new post title* provides value.
    *   Prioritize posts that discuss the same technology stack (e.g., Gemini, Imagen, Google Cloud).
3.  **Reporting**:
    *   Identify the target existing posts in the new post's `mentioned_in` frontmatter field.
    *   Trigger an automated GitHub Issue to notify the author to manually add the links.
4.  **Issue Assignment**: Assign any resulting maintenance issues to `AlexandreBrisebois`.

## Metadata Rules
*   Maintain a reference to the `mentioned_in` list in the automation report.
*   Only suggest posts with a direct and technical connection.
