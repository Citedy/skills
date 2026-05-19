# Accounting Model

Use this reference when changing plan limits, D1 usage tables, Workers AI proxy
logic, usage digests, or customer-visible included message copy.

## Baseline Formula

```text
cost_usd = input_tokens / 1_000_000 * 0.10
         + output_tokens / 1_000_000 * 0.30
```

Planning profiles:

| Profile | Input tokens/msg | Output tokens/msg | Cost/msg |
| --- | ---: | ---: | ---: |
| Normal onboarding/chat | 2,000 | 1,000 | $0.0005 |
| Heavy marketing/chat | 8,000 | 2,000 | $0.0014 |
| Extreme fair-use guardrail | 16,000 | 4,000 | $0.0028 |

Recommended plan baseline:

| Plan | Messages | Normal cost | Heavy cost | Extreme cost | Cost cap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Starter | 300 | $0.15 | $0.42 | $0.84 | $1.00 |
| Pro | 1,500 | $0.75 | $2.10 | $4.20 | $4.50 |
| Business | 5,000 | $2.50 | $7.00 | $14.00 | $15.00 |

## Accounting Invariants

- Count at least one usage event per accepted chat completion request.
- Update period counters only after entitlement and token validation pass.
- If Workers AI returns a provider error after quota was reserved, record a
  failed usage event but do not count it as a successful included message unless
  the product explicitly decides otherwise.
- Enforce `message_limit` and `cost_cap_usd`; either cap can stop usage.
- Store full token text nowhere. Store token hash and display prefix only.
- Token/cost counters must be period-scoped and tied to subscription period.
- Refund/dispute/cancel/past_due must block the proxy even if local period
  counters still have balance.
- Grant credits are runway. Do not hide COGS or sell unlimited behavior because
  a grant exists.
- Host AI fallback usage consumes the same included quota and cost cap as direct
  Host AI usage.

## D1 Tables To Expect

```text
host_ai_periods
host_ai_tokens
host_ai_usage_events
```

If implementation adds different table names, reviewers must confirm the same
facts are still queryable: user, sandbox, subscription, tier, period, limits,
usage counters, token prefix/hash, status, and timestamps.
