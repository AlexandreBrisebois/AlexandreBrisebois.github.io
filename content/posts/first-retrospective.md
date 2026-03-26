---
title: 'Lessons Learned: A Project That Went Sideways'
date: 2026-03-15 09:00:00+00:00
description: A cloud migration that looked clean on the architecture diagram and fell
  apart in production. What happened, what we changed, and what I carry forward.
tags:
- retrospective
- cloud
- engineering
- lessons-learned
draft: false
slug: lessons-learned-project-went-sideways
tldr: Clean diagrams don't survive contact with production traffic. The pivots that
  saved us weren't technical — they were decisions about what to stop defending.
social_posts:
  linkedin: ''
  x: ''
  bluesky: ''
related_posts:
- About
mentioned_in:
- About
image_prompt: 'Minimalist abstract architectural diagram of a serverless event flow.
  Geometric composition showing three nodes and connecting paths where one path subtly
  drifts off-axis. High-contrast tactile paper texture. "Calm Signal" aesthetic with
  clean lines and wide whitespace. Color palette: warm off-white background, deep
  forest green elements, and a singular muted coral accent. No humans, no faces, no
  logos, no text. Professional, sophisticated, landscape orientation.'
---

The architecture diagram looked clean. Three services, two queues, one database. We had reviewed it in five separate meetings and everyone agreed it was the right call.

The first week in production proved otherwise.

## What Happened

We were migrating a batch processing workload to a serverless event-driven architecture. The premise was sound: replace a scheduled VM-based job with a pipeline of cloud functions triggered by a message queue. Lower cost, better observability, no infrastructure to manage.

What we underestimated was message ordering. The existing system had an implicit dependency on sequential processing that the team had stopped thinking about years ago — it was just how the system worked. When we introduced async consumers, those ordering guarantees disappeared. Downstream systems started failing in ways that took three days to trace back to the root cause.

{{< callout type="warning" >}}
Implicit ordering guarantees are the most dangerous kind. They survive for years because nothing ever breaks — until you change the processing model.
{{< /callout >}}

## The Pivot Points

The first pivot was stopping. We had momentum, the migration was 70% complete, and stopping felt like failure. It wasn't. It was the only thing that prevented a larger incident.

The second pivot was admitting we didn't fully understand the system we were replacing. We had documentation. We had architecture diagrams. What we lacked was a map of every assumption baked into the original design — assumptions that had calcified into invisible constraints.

We spent two days writing those constraints down. Not to be thorough. To stop guessing.

{{< callout type="note" >}}
Before migrating any system, document what the current system is *not* doing — the failure modes it prevents by accident, the orderings it enforces by convention. These are as important as what it does intentionally.
{{< /callout >}}

The third pivot was scope reduction. We shipped a version that preserved the sequential processing guarantee and accepted that we'd revisit the async architecture in a second phase. It wasn't the elegant solution we'd designed.

It shipped.

## Lessons for the Future

The technical fix was straightforward once we understood the problem. The harder lessons were organizational.

Diagrams build consensus, not understanding. A room full of people agreeing on an architecture is not the same as a room full of people understanding the system that architecture replaces.

"Done" on a migration means the new system handles everything the old system handled — including the things nobody documented.

Momentum is a liability when you're moving in the wrong direction.

{{< callout type="tip" >}}
Schedule a pre-mortem before any significant migration. Ask the team: "If this fails two weeks after launch, what will we wish we had understood earlier?" The answers are almost always more useful than the architecture review.
{{< /callout >}}

The project shipped eventually. We carry it differently now.
