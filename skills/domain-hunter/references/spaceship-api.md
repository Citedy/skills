# Spaceship API Reference

> **Setup:** Get your API key and secret from your Spaceship account dashboard.
> Store them as environment variables: `SPACESHIP_API_KEY` and `SPACESHIP_API_SECRET`.

Base URL: `https://spaceship.dev/api`

## Authentication

All requests require these headers:
```bash
-H "X-Api-Key: $SPACESHIP_API_KEY"
-H "X-Api-Secret: $SPACESHIP_API_SECRET"
```

## Domains API

### List Domains
```bash
curl -s -X GET "https://spaceship.dev/api/v1/domains?take=100&skip=0" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET"
```

### Check Domain Availability (Batch)
```bash
curl -s -X POST "https://spaceship.dev/api/v1/domains/available" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"domains": ["example.com", "test.ai"]}'
```
Response: `result` = "available" | "taken" | "reserved"

### Check Single Domain Availability
```bash
curl -s -X GET "https://spaceship.dev/api/v1/domains/{domain}/available" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET"
```

### Get Domain Info
```bash
curl -s -X GET "https://spaceship.dev/api/v1/domains/{domain}" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET"
```

### Register Domain (Purchase)
```bash
curl -s -X POST "https://spaceship.dev/api/v1/domains/{domain}" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "autoRenew": true,
    "years": 1,
    "privacyProtection": { "level": "high", "userConsent": true },
    "contacts": {
      "registrant": "CONTACT_ID",
      "admin": "CONTACT_ID",
      "tech": "CONTACT_ID",
      "billing": "CONTACT_ID"
    }
  }'
```
**Note:** Returns 202 Accepted, poll async-operations for result

### Update Nameservers
```bash
curl -s -X PUT "https://spaceship.dev/api/v1/domains/{domain}/nameservers" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{ "provider": "custom", "hosts": ["ns1.cloudflare.com", "ns2.cloudflare.com"] }'
```

### Update Auto-Renewal
```bash
curl -s -X PUT "https://spaceship.dev/api/v1/domains/{domain}/autorenew" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"isEnabled": true}'
```

### Renew Domain
```bash
curl -s -X POST "https://spaceship.dev/api/v1/domains/{domain}/renew" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"years": 1}'
```

## DNS Records API

### Get DNS Records
```bash
curl -s -X GET "https://spaceship.dev/api/v1/dns-records/{domain}?take=100&skip=0" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET"
```

### Save DNS Records
```bash
curl -s -X PUT "https://spaceship.dev/api/v1/dns-records/{domain}" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"type": "A", "name": "@", "address": "1.2.3.4", "ttl": 3600},
      {"type": "CNAME", "name": "www", "target": "example.com", "ttl": 3600},
      {"type": "TXT", "name": "@", "content": "v=spf1 ...", "ttl": 3600},
      {"type": "MX", "name": "@", "mailHost": "mail.example.com", "priority": 10, "ttl": 3600}
    ]
  }'
```

## Async Operations

Domain registration, transfer, etc. are async, returning `spaceship-async-operationid` header.

### Get Operation Status
```bash
curl -s -X GET "https://spaceship.dev/api/v1/async-operations/{operationId}" \
  -H "X-Api-Key: $SPACESHIP_API_KEY" \
  -H "X-Api-Secret: $SPACESHIP_API_SECRET"
```
Status: "pending" | "success" | "failed"

## Rate Limits

| Operation | Limit |
|-----------|-------|
| List domains | 300 req / 300s per user |
| Check availability (batch) | 30 req / 30s per user |
| Check availability (single) | 5 req / 300s per domain |
| Register domain | 30 req / 30s per user |
| Update nameservers | 5 req / 300s per domain |

## Common Workflow: Purchase + Cloudflare NS

```bash
# 1. Check availability
curl -s -X GET "https://spaceship.dev/api/v1/domains/example.com/available" ...

# 2. Register domain (returns 202 + operationId)
curl -s -X POST "https://spaceship.dev/api/v1/domains/example.com" ... -d '{...}'

# 3. Poll for completion
curl -s -X GET "https://spaceship.dev/api/v1/async-operations/{operationId}" ...

# 4. Update nameservers to Cloudflare
curl -s -X PUT "https://spaceship.dev/api/v1/domains/example.com/nameservers" \
  ... -d '{"provider": "custom", "hosts": ["ns1.cloudflare.com", "ns2.cloudflare.com"]}'
```
