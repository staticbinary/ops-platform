# Security Event Correlation

## Trace Search

{service=~".*asset.*|.*auth.*"} |= "trace_id"

---

## Authentication Failures

{service="auth-service"} |= "auth.failed"

---

## Invalid Tokens

{service="auth-service"} |= "token.invalid"

---

## Permission Denied

{service="auth-service"} |= "permission.denied"

---

## Rate Limit Events

{service="asset-service"} |= "rate_limit.exceeded"

---

## Trace Correlation

{service=~".*asset.*|.*auth.*"} |= "<trace_id>"