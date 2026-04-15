---
title: 'Token Exhaustion: What Three AI Coding Agents Taught Me in a Single Week'
slug: token-exhaustion
date: 2026-04-10
lastmod: 2026-04-13
draft: false
description: "What if running out of tokens isn’t a tech failure, but a sign your workflow is broken? After a week with three AI coding agents, I discovered how my own habits drained my token budget and limited what I could build. This post shows why rethinking your approach, not just your tools, can unlock real progress."
tldr: "If you’re running out of tokens, it’s often not just the tool. It could be your workflow. My week with three AI coding agents showed me how my habits drained my tokens and limited what I could build. Rethink your approach, or you’ll waste your budget before you see real progress."
tags:
- quick-win
- lesson-learned
- ai-fluency
- prompt-engineering
- context-engineering
image_prompt: "Token exhaustion, abstracted as a minimalist architectural diagram:
  a sparse, high-contrast flow of muted earth-tone geometric shapes converging on
  a central barrier or 'wall'. One dominant focal point, wide negative space, asymmetric
  balance. No humans, no logos. Calm Signal palette: warm off-white, calm green, calibrated
  coral, oceanic deep blue, shadow plum, ink slate. Editorial, precise, quietly urgent
  lighting."
social_blurbs:
  linkedin: 'If you’re running out of tokens with AI coding agents, it’s probably not the tool, it’s your workflow. After a week with three AI coding agents, I realized my habits were draining my tokens and limited what I could actually build. Rethink your approach, or you’ll waste your budget before you see real progress. #AI #workflow #dev'
  x: 'If you’re running out of tokens, it’s not the tool,it’s your workflow. My week with three AI coding agents showed me how my habits drained my tokens and limited what I could build. Rethink your approach, or you’ll waste your budget before you see real progress. #AI #workflow #dev'
  bluesky: 'Ran out of tokens with three AI coding agents in one week, not because of the tools, but because my workflow was broken. My habits drained my budget and limited what I could build. Rethink your approach, or you’ll hit the same wall. #AI #workflow #dev'
social_posts:
  linkedin: 'https://www.linkedin.com/posts/alexandrebrisebois_token-exhaustion-what-three-ai-coding-agents-activity-7450136147541897216-Er7z/?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAEsTG8BGzDymbcZlTIFnj-W0HyD65bOaXg'
related_posts: []
mentioned_in: []
image: /images/posts/token-wall.webp
gradelevel: 5.3
readability: 74.0
ai_disclaimer: true
---

I use [GitHub Copilot](https://github.com/features/copilot). Curiosity pulled me toward [Antigravity](https://antigravity.google/) and [Claude Code](https://claude.com/product/claude-code). I had a few experiments in mind. This was the perfect chance. My plan was simple: I would jump from one tool to the next and experience their workflows firsthand. **The token wall blindsided me.**

{{<callout type="warning">}}
**Token Wall**: You run out of credits or have reached the productivity window usage limit.
{{</callout>}}

## The Token Wall: A Week of Surprises

First, GitHub Copilot. Next, Antigravity, with my Gemini Pro subscription. Finally, Claude Code on a brand new Pro account. Three AI coding agents. One week.

> I didn't run out of tokens because the tools were bad. I ran out because I was using them wrong. That's the conclusion. Everything else is the evidence.

By the time I ran out of tokens with Antigravity, I had a [prompt](https://github.com/AlexandreBrisebois/AlexandreBrisebois.github.io/blob/main/.claude/blog-build-prompt-v2.md) ready. My goal was to run a long session that would produce a new [blog](https://srvrlss.dev), including GitHub Actions and GenAI features.

Fifty minutes later, Claude Code delivered. I was amazed. Then I checked my token budget. My subscription was already past the 10% mark. That was the first time I stopped and thought, **this can't be right**.

## Context, Cost, and Flow

The session context never stays flat. Every exchange makes it grow. Each file attached, each tool running in the background, adds tokens to the conext. I worked in long lived sessions, convinced depth meant productivity. I missed the real cost: heavy context sessions burn more tokens.

When I hit the wall for the third time, I still didn't have that framing. I just had an empty balance and a half-finished project.

I tried to understand where I went wrong and soon realized I wasn’t alone. Others spoke up about hitting the token wall. That week, Anthropic enforced five-hour productivity windows and [sessions during peak hours used more tokens than during quiet hours](https://x.com/trq212/status/2037254607001559305).

I wasn't finished. I felt productive. I was in flow. So I enabled Claude's extended usage and watched a second, then a third round of tokens melt away.

> I was refueling a car with the engine running and the doors open.

## The Moment I Started Paying Attention

The token wall was not bad luck. It happened because of how I worked. I had built a machine tuned for rich context and I kept feeding it. I called it productivity. The bill called it wasteful.

**I wondered how full-time developers avoid hitting the token wall.** It felt like I had done something wrong and spent my tokens carelessly. Looking back, I had. And I had done it with the best intentions. My assumptions needed to be reevaluated.

What was I doing in those sessions that made them so expensive? That question had answers. The answers changed everything I did next.

> Token exhaustion is not a failure. It is a design constraint. Working within it is a mark of fluency, not defeat.

## The Forgotten Instructions

I had been experimenting with Claude Agents. I was using AI coding agents to optimize their agent.md files. I couldn't put my finger on it. Even after reviewing their instructions, I couldn’t explain why behaviors I had removed would sometimes reappear. It wasn’t consistent. Something was off.

The real culprit was invisible: a week earlier, I had loaded my writing profile as global agent instructions across GitHub Copilot, Gemini, and Claude... I wanted them to sound like me. It felt like a smart move. It wasn't... 

{{<callout type="note">}}
**Instruction** are files that provide persistent context and constraints that guide AI coding agents to align with specific project standards and personal workflows. They effectively act as a "source of truth" for the AI, allowing it to operate autonomously within the guardrails of your existing codebase.
{{</callout>}}

**I created a ghost in the machine.** The instructions quietly shaped every sessionand added a token tax. The global instructions conflicted with my agents, my prompts and my edits. The model got confused. I was at a loss!

The fix was simple. I stripped the global instructions. The ghost was gone.

> Keep instructions minimal, structured, and high‑signal; push detail into reference docs that the agents can read on demand. 

Instructions are powerful. They are the defaults and are applied to every session. Keep them lean because they count towards your token budget.

## Getting The Most Out of Each Session

**A session's context grows with every exchange**. The use of reasoning frameworks like Chain of Thought (CoT) and Tree of Thought (ToT) adds tokens to the context. Every file you attach and every tool you enable, including MCP servers and plugins, also contribute more tokens. The bottomline is that everything you add to a session consumes more tokens. Strategically structuring a session maximizes its effectiveness.

Start by **front loading the constraints, reference materials and instructions.** Refer back to them in your prompts to keep the session focused and avoid repetition.

**Spend time curating the context.** Only include what is necessary for the specific task at hand. Be specific about the success criteria, the output format and constraints.

Use tools to pull in context on demand and limit the number of tools an agent can call in a session. (eg. add a constraint to your prompt: "You can only use {tool} 3 times, if you need to use it more, ask me and provide a justification."). 

**Use CSV and Markdown files when possible**, models love text. PDFs and images are heavy on tokens and require extra processing.

From your IDE, **select text and add it to your chat session**. This allows you to be very specific and to focus the agent on the task at hand. If you have long documents, consider summarizing them and extracting only the relevant sections before adding them to the session.

Models often reveal their reasoning process. While this can be insightful, it quickly consumes tokens. Impose clear constraints to keep outputs focused. For example:

```
Constraint: Execute all reasoning frameworks internally. 
Output only the final result.

Default to 2-3 concise sentences. Avoid headers, bolding, 
or pleasantries unless I ask for 'details' or a 'deep dive.'

If instructions are ambiguous or conflicting, ask for 
clarification before proceeding.

Respond to this prompt with 'understood' to confirm you 
have internalized these constraints.
```

**Keep deep-dive exploration and planning sessions separate from sessions where you get work done.** Brainstorming noise causes the context to drift. The agents gets distracted. **Spend time building a strong, focused prompt.** Then use it in a new session to get the work done.

**Searching the web from AI Assistants is expensive**, and must me used strategically. It adds large amounts of information, some of which can be irrelevant and causes the models to lose focus.

> Irrelevant, noisy and conflicting information constribute to context drift and model confusion.

Consider alternative methods. Use Google Search, Bing or Perplexity. Gather the information in a structured Markdown file. Then use the file with the front loading technique to bootstrap your next work session.

If you review or edit a file more than once, **start a new session for each round**. This prevents multiple versions of the file from piling up in your context. Each session stays focused on the latest version, reducing context size and model confusion.

> New Task → New Session. 

Avoid trying to do too much at once. **Keep sessions focused on a single task or goal.** If you need to start a new task that builds on your current session, create a continuation prompt. 

Ask the agent to summarize key points, decisions, and next steps. Start your next session with a new, self-contained prompt. This technique helps you maintain your flow and keep a clean, focused context.

If you want to experiment with your own continuation prompts, here’s a detailed example I’ve found useful, you can adapt or borrow from it as you see fit:

```
You are a **Continuation‑Prompt Constructor**.  
Your job is to generate a single **System Initialization Block** 
that lets a new AI session recover this project’s state, constraints, 
and momentum, minimizing session amnesia.

Follow this schema and fill it with project‑specific content:

1. **Core Articles (Behavior & Values)**  
   - Role: “Act as a `[Senior Role]` for `[Project Name]`.”  
   - Reasoning style: “Use `[Methodology]` reasoning.”  
   - Communication: “Tone `[X]`, detail level `[Y]`, 
     format `[e.g., Markdown, bullet‑heavy, no fluff]`.”  

2. **Layered Context Bounds**  
   - Lexicon Layer: “Key terms and acronyms 
     (use these exactly): `[list]`.”  
   - Environment Layer: “Stack and hard constraints 
     (only suggest compatible options): `[hardware/OS/tools]`.”  
   - Exclusion Layer (“Graveyard”): 
     “Do not re‑propose: `[discarded approaches/ideas]`.”  

3. **Logic Ledger (Precedents & State)**  
   - Immutable Decisions (Precedents): 
     “Locked choices that must not be questioned: `[list]`.”  
   - State of Work:  
     - Completed: `[main milestones]`.  
     - Current Vector: 
       `[the specific problem or friction point we are solving now]`.  

4. **Continuity & Validation Gate**  
   - Constitutional Check: “All actions must respect 
     the Core Articles and Immutable Decisions above.”  
   - First‑Reply Requirement: “Your first response in 
     the new session must be a **Context Audit** that:  
     - Restates the mission, stack, and constraints in 
       your own words.  
     - Identifies the Current Vector and the main blocking 
       constraint.  
     - Confirms alignment before proposing next steps.”  

5. **Generator Safeguards (For You, the Constructor)**  
   - If the Current Vector or next step is unclear, 
     ask me **one** clarifying question before generating the block.  
   - If you see conflicting directions or pivots, 
     briefly list the contradictions and ask me to confirm 
     the current **North Star** before finalizing.  
   - Output a single, copy‑pasteable block starting with:  
     `### NEW SESSION INITIALIZATION: [PROJECT NAME] ###`
```

## Changing My Defaults Gave Me More Mileage

> I made mistakes! I was well intentioned and I had a lot to learn!

Jumping into execution with just a vague idea always cost me more tokens and left me with weaker results. I thought I was being productive by brainstorming and building as I went, but the session would drift and my intent would blur. 

**The real aha moment came when I treated planning as a separate activity, crystallizing what I wanted before I ever hit “run.”** Planning forced me to get specific and precise about my goals. When I gave vague instructions, I spent the rest of the session steering the agent and burning tokens.

> Clarity up front meant fewer corrections, less drift, and better results.

Antigravity’s solid plan-first approach pushed me to structure my thoughts, identify clear outcomes, and define success. I found myself iterating, refining, and building a clear goal for the agent.

Claude Code in VS Code also has a planning feature. Like Antigravity, I could provide feedback by selecting text and leaving comments, or by giving global feedback. Claude would revise and adjust the plan, but the separation between planning and execution wasn’t as clear cut as in Antigravity. 

Anthropic released [ultraplan](https://code.claude.com/docs/en/ultraplan) this week. This new experience is a leap forward from the VS Code extension. Start `/ultraplan [what you want to get done]` from your CLI, and you're pulled to Claude Code on the web to draft your plan. Once you're ready, you can execute it remotely or back in your terminal.

Antigravity still has the upper hand, and **I expect this space will evolve rapidly**. Ultraplan, at the time of writing, feels like a fast-forward through planning and into execution. I felt rushed, and kept pushing back to keep iterating on my plan. I found myself gravitating back to Antigravity for planning sessions.

> The more powerful the tool, the more it tempts me to use it for everything

Don't get caught by the **AI Paradox**: The more powerful and engaging the tool, the more it tempts me to use it for everything, even when it’s not the best choice. 

When I’m in flow, it feels good to delegate even the smallest tasks to an agent (eg. merging a branch or searching & replacing a string). But that satisfaction is deceptive, because I end up burning precious tokens on actions that are faster and cheaper if I do them myself. 

**Years of habits vanished, eclipsed by the novelty and thrill of AI.** The cost? Tokens spent on activities that, on their own, don’t add significant value. 

The accumulation of these small, unnecessary delegations greatly contributed to my token consumption. Build on your hard-won habits. Use shortcuts, built-in tools, and the full power of your IDE for what they do best. **Let AI amplify your intent, not replace it.**

> Challenge your defaults

Use the right model for the task. Don’t always reach for the most powerful model. Start with the one designed for your task’s actual complexity. As of April 2026, my new go-to choices are Gemini 3 Flash, GPT-5.4 mini on GitHub Copilot, and Claude Haiku 4.6. I reserve the more powerful models only for specific tasks that require them.

Now, I ask models to review my prompts and recommend the best model for each task. While their suggestions aren’t perfect, they reveal patterns that help me make better choices.

## Forging a Head Towards AI Fluency

> Tokens are the new currency!

The biggest shift I made wasn’t just in my tools, it was in how I approached every session, every prompt, every choice. Throughout the week, I burned through tokens without realizing that my global instructions were inflating every session. Once I stripped them back, my token use dropped and my results dramatically improved.

> Token exhaustion wasn’t a failure; it was the wake-up call I needed.

Now, I focus on giving each agent a clear target, breaking work into smaller composable pieces, and sharing only what matters for the task at hand. These changes didn’t just save tokens, they made every session more intentional and effective.

If you’re burning tokens, ask yourself: What invisible habits are driving your costs? 

What’s the first thing you’ll change to get more value from every session?