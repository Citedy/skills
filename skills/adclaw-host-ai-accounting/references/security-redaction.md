# Security And Redaction

Use this reference when reviewing Host AI token minting, Citedy key
provisioning, logging, Sentry, backups, or sandbox bootstrap.

## Hard Boundaries

- Never place Cloudflare account tokens, Workers AI upstream credentials, or
  Citedy service credentials inside the sandbox.
- The sandbox may receive only customer-scoped secrets:
  - synthetic Host AI token;
  - `CITEDY_API_KEY` for the customer's `adclaw-host` tenant agent.
- Full tokens and full keys must not appear in logs, Sentry, analytics, audit
  payloads, email, PR comments, screenshots, or normal GET responses.
- R2 backups containing `/workspace/working.secret` are secret-bearing.
- Secret-bearing backups require private ACLs, careful lifecycle policy, and no
  public debug links.

## Token Design Checks

- Host AI token is securely random or securely signed with enough entropy.
- D1 stores hash and prefix, not plaintext.
- Token is scoped by user, sandbox, subscription period, and status.
- Token can be revoked without rebuilding the sandbox.
- Entitlement state is checked on every proxy call, not only at launch.
- Past due, refund, dispute, cancel, and admin suspension all block use.

## Citedy Key Checks

- `adclaw-host` is deterministic as an agent record name, not as key material.
- Key material is securely random and shown/transferred only once.
- Hosted auto-provisioning uses service-to-service auth.
- Browser/manual flow remains fallback/rotation.
- Rotation warnings are explicit because rotation breaks old tasks.

## Redaction Test Cases

Search for full test tokens in:

```text
Worker logs
Sentry event payloads
audit_events payloads
notification ledger
browser network responses
AdClaw app logs
R2 metadata
```

If a test has to include a token, use a fake sentinel value and assert that the
sentinel is absent from every captured log/response.
