# Code Review Reference Guide

Supporting reference for the `code-review-agent-team` skill. Each reviewer agent reads this file to apply consistent standards.

---

## Severity Classification Guide

### Critical -- Must fix before merge

Findings that can cause data loss, security breaches, or production outages.

| Category | Examples |
|----------|---------|
| Security | SQL injection, hardcoded secrets, auth bypass, exposed PII |
| Data Loss | Unprotected DELETE/UPDATE without WHERE, missing transaction rollback |
| Production Break | Unhandled null dereference in critical path, infinite loop, missing env var crash |
| Financial | Billing calculation errors, double-charge scenarios, credit leak |

### High -- Should fix before merge

Findings that cause degraded performance, poor user experience, or maintenance burden.

| Category | Examples |
|----------|---------|
| Performance | N+1 queries, unbounded data fetch, memory leak in long-lived component |
| Reliability | Missing error handling on external API call, race condition, no retry logic |
| Test Gap | New API endpoint with zero tests, bug fix without regression test |
| Type Safety | `any` type in public API, missing null checks on nullable fields |

### Medium -- Fix when possible

| Category | Examples |
|----------|---------|
| Maintainability | DRY violation (3+ copies), function exceeding 100 lines, deep nesting |
| Conventions | Inconsistent naming, missing return types, imports not sorted |
| Test Quality | Weak assertions (testing implementation not behavior), flaky test pattern |
| Documentation | Missing JSDoc on exported function, misleading comment |

### Low -- Consider improving

| Category | Examples |
|----------|---------|
| Style | Minor naming preference, redundant else after return |
| Optimization | Micro-optimization with negligible impact |
| Suggestion | Better abstraction available, utility function exists |

---

## Security Review Checklist

### Authentication & Authorization
- [ ] Auth checks present on all protected routes
- [ ] Database-level access controls (RLS, permissions) for new tables/columns
- [ ] Service role keys never exposed to client
- [ ] JWT validation not bypassed
- [ ] Role-based access enforced where needed

### Input Validation
- [ ] All API inputs validated with schema validation (Zod, Joi, etc.)
- [ ] User input sanitized before database queries
- [ ] File upload types and sizes restricted
- [ ] URL parameters validated and typed
- [ ] Request body size limits enforced

### Data Exposure
- [ ] No secrets, API keys, or tokens in code
- [ ] No PII logged (emails, names, IPs in error messages)
- [ ] Error responses do not leak internal details
- [ ] Database queries return only needed columns
- [ ] Sensitive fields excluded from API responses

### Injection Prevention
- [ ] Parameterized queries used (no string concatenation in SQL)
- [ ] XSS prevention (input escaped in rendered output)
- [ ] CSRF tokens validated on mutations
- [ ] No dynamic code execution patterns
- [ ] HTML sanitized when accepting rich text

### Dependencies & Configuration
- [ ] No known vulnerable dependencies added
- [ ] Rate limiting applied to new API endpoints
- [ ] CORS configuration restrictive
- [ ] Environment variables used for all configuration

---

## Performance Review Checklist

### Database & Queries
- [ ] No N+1 query patterns (queries inside loops)
- [ ] Appropriate indexes exist for new query patterns
- [ ] LIMIT/pagination on all list queries
- [ ] Batch operations used where possible
- [ ] No unnecessary JOINs or subqueries

### Memory & Resources
- [ ] Event listeners and subscriptions cleaned up
- [ ] Large objects not held in closure scope unnecessarily
- [ ] Streams used for large data processing
- [ ] Database connections properly released

### React & Frontend
- [ ] Server components used where client interactivity not needed
- [ ] useMemo/useCallback for expensive computations passed as props
- [ ] No unnecessary re-renders
- [ ] Images optimized
- [ ] Code splitting applied for large modules
- [ ] Avoid importing entire libraries when only one function is needed

### Caching
- [ ] Cache considered for frequently accessed data
- [ ] HTTP cache headers set appropriately
- [ ] Cache invalidation strategy defined

### Algorithms
- [ ] No O(n^2) or worse where O(n) or O(n log n) is possible
- [ ] Map/Set used for lookups instead of array.find in loops
- [ ] Debounce/throttle on frequent event handlers

---

## Test Coverage Review Checklist

### New Code Coverage
- [ ] Every new exported function has at least one test
- [ ] Every new API endpoint has integration test
- [ ] Bug fixes include regression test proving the fix

### Edge Cases
- [ ] Null/undefined inputs handled and tested
- [ ] Empty arrays/strings handled and tested
- [ ] Boundary values tested
- [ ] Error paths tested

### Assertion Quality
- [ ] Tests verify behavior, not implementation
- [ ] Assertions are specific
- [ ] Async operations properly awaited

### Test Organization
- [ ] Tests isolated (no shared mutable state)
- [ ] Mocks match real interfaces
- [ ] Test descriptions clearly explain the scenario

---

## Code Quality Review Checklist

### Readability
- [ ] Functions are under 50 lines
- [ ] Nesting depth is 3 or fewer levels
- [ ] No nested ternary operators
- [ ] Complex logic has clear variable names

### Naming Conventions
- [ ] Variables describe what they hold
- [ ] Functions describe what they do (verb + noun)
- [ ] Boolean variables start with is/has/should/can
- [ ] Constants in UPPER_SNAKE_CASE
- [ ] React components in PascalCase

### DRY & SOLID
- [ ] No logic duplicated 3+ times
- [ ] Single Responsibility per function/component
- [ ] Interface Segregation: no God objects

### TypeScript
- [ ] No `any` types (use `unknown` if truly unknown)
- [ ] Explicit return types on exported functions
- [ ] Proper use of union types and discriminated unions

### Error Handling
- [ ] Errors handled at appropriate level (not swallowed silently)
- [ ] Error messages are actionable and descriptive
- [ ] Failed operations do not leave side effects

---

## Standard Finding Format

Each reviewer must return findings in this exact JSON format:

```json
[
  {
    "reviewer": "security|performance|test-coverage|code-quality",
    "severity": "Critical|High|Medium|Low",
    "file": "relative/path/to/file.ts",
    "line": 42,
    "title": "Concise title (under 80 chars)",
    "description": "Detailed explanation with evidence from the diff.",
    "suggestion": "Specific, actionable fix.",
    "category": "see category list per reviewer"
  }
]
```

### Category Values by Reviewer

| Reviewer | Valid Categories |
|----------|----------------|
| security | auth, injection, exposure, config, validation, dependencies |
| performance | n+1, memory, rendering, bundling, caching, algorithm, database |
| test-coverage | missing-test, edge-case, assertion, integration, e2e, mock-quality |
| code-quality | naming, dry, solid, complexity, types, error-handling, style, organization |

### Rules for Findings

1. **Be specific** -- reference the exact file, line, and code snippet from the diff
2. **Be actionable** -- every finding must have a concrete suggestion
3. **Avoid duplicates** -- if two reviewers find the same issue, the more specific one wins
4. **Stay in scope** -- only review code that is part of the diff
5. **No false positives** -- if unsure, mark as Low severity with a note
