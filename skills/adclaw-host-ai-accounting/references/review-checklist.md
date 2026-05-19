# Review Checklist

Use this checklist for implementation PRs and architecture/doc audits.

## Architecture

- Host Worker owns Workers AI access through `env.AI`.
- Sandbox receives only synthetic Host AI token and customer-scoped Citedy key.
- Hosted path is separated from self-hosted/Railway/GitHub/local installs.
- Host AI remains the managed default/fallback provider after user adds BYO
  providers.
- AdClaw provider bootstrap writes to `ADCLAW_SECRET_DIR`, not only legacy
  `WORKING_DIR/providers.json`.
- Citedy key provisioning is server-to-server for hosted auto-provisioning.

## Accounting

- D1 period/token/event rows are idempotent per subscription period.
- Both message and cost caps are enforced.
- Usage event is recorded for success and meaningful failure states.
- No quota bypass on wake, restore, token rotation, or sandbox restart.
- Fallback to Host AI consumes the same quota/cost cap as direct Host AI calls.
- Usage digest can report top spend-risk accounts without starting sandboxes.

## Entitlement

- Active subscription required at launch and at every Host AI proxy call.
- Cancel, refund, dispute, past_due, and admin suspension revoke or block use.
- Repeat-abuse tracking has evidence without collecting sensitive key material.

## Security

- Full tokens and keys are redacted everywhere.
- R2 backup handling treats `/workspace/working.secret` as secret-bearing.
- Logs include prefixes/ids only.
- Sentry payloads are sanitized.
- Service-to-service Citedy endpoint cannot be called from browser origins.

## UX

- First chat after paid launch needs no key setup.
- Limit reached message is friendly and actionable.
- User provider outage falls back to Host AI while included quota remains.
- BYO provider remains available.
- Customer does not see Cloudflare internals.
- Copy distinguishes included Host AI messages from Citedy credits.

## Tests

- Unit tests for quota math and status mapping.
- Integration test for proxy auth and D1 usage write.
- Sandbox bootstrap test for provider/env secret files.
- Redaction test with sentinel fake secrets.
- Paid/staging smoke with quota set to `1`.
