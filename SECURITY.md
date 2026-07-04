# SECURITY — AI Brain · USA

## Reporting a vulnerability

If you discover a security vulnerability in AI Brain — USA, please report it via **GitHub Security Advisories** at the repository:

https://github.com/Wolfgangrush/ai-law-firm-usa/security/advisories/new

Or via private email to: advrushikeshravindramahajan@gmail.com (private channel — please do NOT post vulnerabilities to public GitHub Issues).

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested mitigation

We aim to acknowledge reports within 72 hours and provide an initial assessment within 7 days.

## Scope

Vulnerabilities in scope:
- Code-execution vulnerabilities (path traversal · command injection · pickle deserialization · etc.)
- Sensitive-data exposure (config-file world-readable · credentials in logs · etc.)
- Local privilege escalation via tool usage
- Cryptographic weaknesses in any signing or encryption layer

Out of scope:
- Vulnerabilities in upstream dependencies — report to those projects directly
- Vulnerabilities in cloud AI vendors — report to those vendors directly
- Social-engineering attacks against users
- Physical access attacks against the user's laptop

## Disclosure policy

We follow **coordinated disclosure**:
- We will not disclose the vulnerability publicly until a fix is released or 90 days pass, whichever is sooner
- We will credit the reporter in the CHANGELOG and security advisory (unless they prefer anonymity)
- We do NOT offer bug bounties at this time

## CVE policy

For confirmed vulnerabilities meeting NIST severity criteria, we request a CVE through GitHub's CNA. Credit to the reporter (unless anonymity requested).

## Security hygiene practices

- Dependencies pinned in `requirements.txt`
- Quarterly `pip-audit` review
- No `eval` · no `exec` in code
- All user input filtered before crossing tool/OS boundary
- File paths normalized to prevent path traversal
- Subprocess calls audited and use explicit argument lists (never shell=True with user input)

## Past advisories

(None as of v0.1)

---

*This document references LEGAL_EXPOSURE_PLAYBOOK §3.V11 (Security Vulnerability). Playbook version: v0.1.*
