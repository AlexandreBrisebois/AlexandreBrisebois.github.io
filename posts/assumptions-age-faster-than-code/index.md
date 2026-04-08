
## The New Waste Is Skipping Research & Planning

**In 2026, the most expensive mistake in AI engineering is treating a fast-moving assumption like a stable fact.**

One prompt, one agent away, generating code has become so cheap that I skipped the research phase entirely. I learned this the hard way while building a tool to run Gemma 4 on Apple Silicon. My intuition defaulted to execution because building felt faster than searching. The real cost was the hours and tokens lost by skipping a ten-minute check. I found that official support already existed. My work was sound and my premise was stale.

> The new waste is not failed execution. It is skipping the ten-minute research that determines whether custom work is justified.

## The Seduction of Momentum

**Momentum is seductive, but assumptions are expensive.**

I woke up ready to wire Gemma 4:26B into my local workflow. I remembered MLX-LM as the only path for Apple hardware. Within an hour, I had a working tool and a clean repository. The "Maker's High" had blinded me to the search bar. I felt productive while I was actually building technical debt. Then, I had that nagging feeling of doubt.

What if the landscape changed since I last checked? A quick search showed that Ollama already supported Apple Silicon with direct Gemma 4 integration ([Ollama Quickstart](https://docs.ollama.com/quickstart), [Ollama Gemma 4](https://ollama.com/library/gemma4)).

{{< callout type="note" >}}
The release of Ollama 0.19 (March 30, 2026) marked a pivot from llama.cpp to Apple’s MLX framework as the primary backend for Apple Silicon. This transition leverages the M5 chip's GPU Neural Accelerators and Unified Memory Architecture (UMA) without requiring manual user flags.
{{< /callout >}}

**My custom patch was obsolete before it shipped.** I deleted my code and updated Ollama. The official path was smoother and maintained by a larger team. When the official path is one install away, custom wrappers need a higher bar.

## Assumptions Age Faster Than Code

The technical error was not using MLX-LM. For fine-tuning on Apple Silicon, it remains the right tool ([MLX-LM](https://github.com/ml-explore/mlx-lm)). My mistake was assuming that nothing had changed. **The cost of building was luring and it cost me the chance to focus on creating new value.** This failure teaches me to prioritize a fresh landscape check over momentum.

## Workflow Discipline Is the New Moat

**The deepest lesson here is humility.** In a space where knowledge decays in days, the only defensible workflow puts validation first. We must review our patterns regularly and challenge tool choices. Validate assumptions before they become debt. Seek to simplify and consolidate.

> Managing change and complexity are the new hero skills.

## The Cost of the Wrong Build

I spent a morning on effort fueled by a stale assumption and it cost me the opportunity to create value. Don't trust the recency of your research. If you haven't checked the landscape this morning, pause and do it now.

The only thing cheaper than building is a ten-minute search.

> How much of your current workflow is built on assumptions that were true last week, but not today?

