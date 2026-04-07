
## The Bottom Line: The New Waste Is Skipping Research & Planning

I'm sharing this because I want to help you skip to the good parts!

**In 2026, the most expensive mistake in AI engineering is treating a fast-moving assumption like a stable fact.**

I learned this the hard way. When building is cheap... I mean one command, one agent, one local model away. The real cost is not failed code, but the hours and tokens lost by skipping a ten-minute check. I spent a morning building a custom MLX-LM wrapper for Gemma 4:26B on Apple Silicon, only to discover that Ollama had already shipped official support. My work was sound, but my premise was stale.

> The new waste is not failed execution. The new waste is skipping the ten-minute validation pass that tells you whether custom work is justified.

## When Building Is Cheap, Doubt Is Priceless

**Momentum is seductive, but unchecked assumptions are expensive.**

I woke up ready to wire Gemma 4:26B into my local agent workflow. I remembered MLX-LM as the only viable path for Apple hardware. Within an hour, I had a working tool, a clean repo, and a dopamine hit. 

**But a nagging doubt crept in.** 

What if Ollama had caught up? A quick search showed that not only did Ollama support Apple Silicon, but it also offered direct Gemma 4 integration ([Ollama Quickstart](https://docs.ollama.com/quickstart), [Ollama Gemma 4](https://ollama.com/library/gemma4)). 

{{< callout type="note" >}}
The release of Ollama 0.19 (March 30, 2026) marked a pivot from llama.cpp to Apple’s MLX framework as the primary backend for Apple Silicon. This transition is specifically designed to leverage the M5 chip's GPU Neural Accelerators and Unified Memory Architecture (UMA) without requiring manual user flags.
{{< /callout >}}

**My custom patch was obsolete before it shipped.** I deleted my code, updated Ollama, and started over. The official path was smoother, faster, and maintained by someone else!

> When the official path is one install and one run command away, custom wrappers need a higher bar.

## The Real Cost of Acting on Stale Assumptions

**Assumptions now age faster than code.**

The technical error wasn’t using MLX-LM. For fine-tuning or Apple-first control, it’s still the right tool ([MLX-LM](https://github.com/ml-explore/mlx-lm)). My mistake was assuming Ollama hadn’t caught up. This time the cost of building was low, just a few hours and tokens. **And, the real cost of not checking first was the lost opportunity to focus on something new and exciting.**

## Workflow Discipline Over Heroic Builds

**Workflow discipline is the new moat.**

This episode forced me to tighten my own patterns. While creating the custom MLX-LM wrapper, I faced a new challenges that highlighted the importance of clear structure and maintainability. Now, when building tools for agent skills, I bundle everything in a single folder. I add a `tool-spec.json` for clarity and use [uv](https://github.com/astral-sh/uv) for zero-config execution. These habits make it easier for agents to use the tools without having to define them in your workspace. The deeper lesson lesson here is humility. In a space where knowledge decays in days, the only defensible workflow is one that puts validation first.

> The highest-ROI step in any build is searching to validate whether a feature already exists.

I'll take this a step further, this is a time where we **must** review our workflows regularly. 

Challenge tool choices, check for new features, and validate assumptions. The pace of change is so fast that yesterday's good practice can become today's technical debt. 

Seek to simplify, to consolidate and to use what's already built and supported. The real moat is adapting to the evolving landscape and keeping complexity down. Managing change, complexity and adoption are the new hero skills.

## What I’ll Do Differently (And What You Should, Too)

**Building in public means learning in public.**

I wasted a morning, I gained a sharper workflow and a story worth sharing. The next time I feel the urge to build before I check, I’ll remember: the cost of building the wrong thing is always greater than not having to build it at all. For leaders and practitioners, the lesson is clear. 

Don’t trust your last round of research. Don’t assume the landscape is static. The only thing cheaper than building is searching first!

> How much of your current workflow is built on assumptions that were true last week, but not today?

