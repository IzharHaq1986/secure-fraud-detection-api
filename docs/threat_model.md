# Threat Model (v1)

## Primary threats
1. Credential theft / API key leakage -> unauthorized inference access
2. API abuse (brute force / scraping) -> service disruption / cost spike
3. Data exfiltration via logs -> leakage of sensitive attributes
4. Log tampering -> inability to prove decisions for audit
5. Model poisoning (artifact replacement) -> malicious decisions
6. Dependency compromise -> supply chain attack

## Mitigation themes
- Strong auth + rate limiting
- Least-privilege roles
- Secrets out of repo, rotated
- Append-only audit logs + integrity checks
- Signed/versioned model artifacts
- Dependency pinning + SCA scanning
