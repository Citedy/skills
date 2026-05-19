# Quota UX And Prompt Behavior

Use this reference when changing AdClaw chat behavior, Host dashboard copy,
provider error mapping, or acceptance tests around included Host AI.

## Customer Promise

Use simple customer-facing language:

```text
Included Host AI: up to N messages per billing period.
Very large contexts are subject to fair-use limits.
Need more or a specific model? Add your own provider key inside AdClaw.
```

Do not promise unlimited usage, exact token counts, or permanent grant-backed
pricing.

## Limit Reached Error

The Host AI proxy should block before calling Workers AI and return a stable
machine-readable code:

```json
{
  "error": {
    "type": "insufficient_quota",
    "code": "adclaw_host_ai_limit_reached",
    "message": "Included Host AI messages for Starter are used. Your limit resets on 2026-06-19. Add your own LLM key, upgrade, or wait for the next period.",
    "plan": "starter",
    "messages_limit": 300,
    "messages_used": 300,
    "reset_at": "2026-06-19T00:00:00Z"
  }
}
```

Recommended statuses:

```text
429 quota reached
402 subscription required/suspended
401 invalid or revoked sandbox token
503 Workers AI/provider outage
```

## UI Mapping

The AdClaw UI should not show raw Cloudflare/provider errors. It should map
`adclaw_host_ai_limit_reached` to:

```text
Included Host AI limit reached

You used the included messages for this billing period.
Your workspace still works. Add your own LLM provider key, upgrade, or wait
until the included messages reset.

[Add my own LLM key] [Upgrade plan]
```

## Prompt Regression Cases

At minimum, test:

- first paid user message succeeds without LLM key setup;
- Citedy status works without pasted Citedy key;
- second message with staging quota `1` shows friendly limit state;
- subscription-required state is different from quota-exhausted state;
- provider outage does not look like customer quota exhaustion;
- customer BYO provider failure falls back to Host AI while included quota
  remains;
- BYO provider path remains available after included Host AI is exhausted.
