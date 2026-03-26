---
title: Why I Built This Blog
date: 2026-03-01 09:00:00+00:00
description: Plain Markdown. Git commits. No CMS, no vendor lock-in, no plugin ecosystem
  to baby-sit. This is why.
tags:
- engineering
- gitops
- writing
draft: false
slug: why-i-built-this-blog
image: /images/posts/why-i-built-this-blog.webp
tldr: A static site generator and a text editor are all you need. Everything else
  is someone else's product decision making itself your problem.
social_posts:
  linkedin: ''
  x: ''
  bluesky: ''
related_posts:
- About
- 'Lessons Learned: A Project That Went Sideways'
mentioned_in:
- About
- 'Lessons Learned: A Project That Went Sideways'
image_prompt: 'Minimalist abstract architectural diagram of a Git-based static site
  workflow. Thin, precise vector lines and geometric nodes representing serverless
  event flows. High-contrast grainy paper texture, "Calm Signal" aesthetic. Color
  palette: warm off-white background, deep forest green lines, and subtle coral accents.
  Clean, wide composition, landscape orientation, technical yet organic, no humans,
  no logos.'
---

The previous version of this blog lived on WordPress. That sentence alone should explain the impulse to start over.

It's not that WordPress is broken. It does what it promises. But every update felt like a negotiation — plugins drift, themes conflict, and somewhere beneath it all, your actual content is locked in a database you technically own but practically can't touch without a GUI.

I wanted something different. A blog that lives in a Git repository. That builds to static HTML. That deploys to a CDN in minutes and costs nothing to run at scale.

Hugo gives me that. A pull request is a draft. A merge is a publish. The entire editorial workflow is a `git log`.

There's something honest about this approach. The writing is the source. Not a row in a database, not a JSON blob from an API — a plain text file with a date and some frontmatter. Readable without a browser. Editable without a login.

I'm not anti-CMS for ideological reasons. I'm anti-CMS because I've watched too many content systems become the main character of their own story. The tool starts serving itself instead of the writer.

A CMS that requires maintenance, updates, plugins, and credentials is infrastructure. Infrastructure that produces content. That inversion is the problem.

This is the opposite of that. The writing is the infrastructure. Everything else is just a build step.
