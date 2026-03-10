# Source: Phil Schmid — Practical Guide to Evaluating and Testing Agent Skills

> **Author:** Philipp Schmid (Google DeepMind, ex-Hugging Face)
> **Date:** March 4, 2026
> **URL:** https://www.philschmid.de/testing-skills
> **Related:** https://www.philschmid.de/agent-harness-2026

---

## Why This Matters

SkillsBench counted over 47,000 unique skills across 6,300+ repos. Most are AI-generated and "vibe-checked" with a few manual runs before shipping. Phil argues: "You wouldn't ship a TypeScript library without a test suite — so why ship a Skill without an evaluation?"

This skill (`skill-quality-eval`) implements the **structural/deterministic** layer of Phil's harness — the checks that require zero LLM calls and catch the most common quality issues.

---

## The 4-Step Eval Harness

### Step 1: Create a Prompt Set (10-20 prompts)

Each prompt declares success criteria:

```json
{
  "id": "py_basic_generation",
  "prompt": "Write a Python script that sends a text prompt to Gemini...",
  "should_trigger": true,
  "expected_checks": ["correct_sdk", "current_model", "interactions_api"]
}
```

Key: include **negative controls** — prompts that should NOT trigger the skill. Too-broad descriptions trigger on everything.

### Step 2: Run the Agent and Capture Output

Test through the same interface the agent uses. Isolate each run — accumulated context bleeds between test cases.

### Step 3: Deterministic Checks (what this skill implements)

Each check is a small boolean function. Fast, repeatable, no LLM cost:

```python
CHECK_REGISTRY = {
    "correct_sdk":      check_correct_sdk,
    "current_model":    check_current_model,
    "interactions_api": check_interactions_api,
    # ...
}
```

**This is what `run-eval.js` automates** — structural validation of command files:
- YAML frontmatter exists
- Description >= 40 chars
- No internal jargon
- Contains directive verbs (action language)
- Similar commands have distinct descriptions

### Step 4: LLM-as-Judge (for qualitative checks)

Use structured output (Pydantic/Zod schemas) for parseable grades. Use selectively — deterministic checks are fast; LLM grading adds cost and latency.

---

## Three Dimensions of Success

| Dimension | Description |
|-----------|-------------|
| **Outcome** | Did it produce a usable result? Code compiles, API responds. |
| **Style & Instructions** | Correct SDK, model IDs, naming conventions, formatting. |
| **Efficiency** | Token count, retries, time. Most undervalued dimension. |

Grade **outcomes, not paths** — agents find creative solutions.

---

## 10 Best Practices

1. **Start with the skill description** — name/description are THE trigger mechanism
2. **Use directives, not information** — `"Always use X"` works; `"X is recommended"` doesn't
3. **Include negative tests** — overly broad descriptions trigger on everything
4. **Start small, extend from failures** — 10-20 prompts; every user-reported bug = new test case
5. **Grade outcomes, not paths** — don't penalize unexpected routes to correct answers
6. **Isolate each run** — context bleed between tests masks failures
7. **Run multiple trials** — 3-5 trials per case; agent behavior is nondeterministic
8. **Test across harnesses** — same skill behaves differently across frameworks
9. **Graduate your evals** — capability evals at ~100% become regression evals
10. **Detect skill retirement** — if evals pass WITHOUT the skill, the model absorbed it — retire the skill

---

## What This Skill Checks (mapped to Phil's framework)

| Phil's Concept | Our Implementation |
|---|---|
| "Description is THE trigger mechanism" | Checks `description:` exists, >= 40 chars |
| "Use directives, not information" | Checks for action verbs (Run, Fix, Scan, Extract...) |
| Avoid confusing users | Jargon detection (dogfood, --dangerously, etc.) |
| "Include negative tests" (differentiation) | Duplicate description detection between similar commands |
| Frontmatter is required | Validates `---` YAML block at top of file |

---

## Key Insight: Description Rewrites Fix Most Failures

> "The two fixes that mattered most were (1) rewriting the skill description to match user intent rather than API terminology, and (2) replacing passive deprecation warnings with explicit instructions. The description change alone fixed 5 of 7 failures."

This is why our eval focuses heavily on description quality — it's the single highest-leverage fix for skill reliability.

---

## Related: Agent Harness Philosophy

From Phil's companion article ["The Importance of Agent Harness in 2026"](https://www.philschmid.de/agent-harness-2026):

- Model leaderboard gaps are shrinking, but **durability** (instruction-following across 100+ tool calls) is the real differentiator
- Agent Harness = Operating System analogy (Model = CPU, Context = RAM, Harness = OS)
- Three developer priorities: **Start Simple**, **Build to Delete**, **The Harness is the Dataset**
- "The ability to improve a system is proportional to how easily you can verify its output"

---

## Further Reading

- [Phil Schmid: Testing Skills](https://www.philschmid.de/testing-skills)
- [Phil Schmid: Agent Harness 2026](https://www.philschmid.de/agent-harness-2026)
- [Anthropic: Demystifying Evals for AI Agents](https://docs.anthropic.com)
- [Anthropic: Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [SkillsBench paper](https://arxiv.org/html/2602.12670v1)
