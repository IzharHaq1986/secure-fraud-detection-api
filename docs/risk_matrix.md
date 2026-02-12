# Risk Matrix (v1)

| Risk | Impact | Likelihood | Mitigation | Evidence artifact |
|------|--------|------------|------------|------------------|
| Unauthorized API access | High | Medium | Auth + key rotation + RBAC | auth design + tests |
| Log leakage of sensitive data | High | Medium | Log minimization + redaction | logging policy + tests |
| Log tampering | High | Low/Med | Append-only + integrity checks | audit logger module |
| Model artifact replacement | High | Low | Versioning + checksum/signing | model artifact policy |
| API abuse / DoS | Med/High | Medium | Rate limiting + timeouts | Nginx + middleware |
| Dependency compromise | High | Medium | Pin deps + scanning | CI workflow |
