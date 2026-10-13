# M0 reviewer baseline

Input: a synthetic package name, ecosystem, and version. Output: source evidence
or an explicit source failure, never a security or compliance verdict.
Machine-readable cases: `tests/fixtures/assessment_cases.json`.

| Reviewer scenario | Desired wording | Required evidence | Prohibited claims | Usefulness criterion |
| --- | --- | --- | --- | --- |
| A reviewer receives findings for example / PyPI / 1.0 | Vulnerabilities returned by this source. | Queried identity, OSV endpoint, unique returned IDs and OSV record links | Proven exploitability, organizational noncompliance, invented severity or remediation | Reviewer can identify which source records to inspect before deciding a next step |
| A reviewer receives no matches | No vulnerabilities returned by this source; this is not proof that the package is secure. | Queried identity, source endpoint, empty findings, explicit uncertainty | Secure, safe, compliant, vulnerability-free | Reviewer understands the source returned no matches and further evidence may be needed |
| A reviewer encounters an unavailable or malformed source | Assessment unavailable from this source; no security conclusion can be drawn. | Specific timeout, HTTP status, transport error, or validation failure; no fabricated findings | Successful empty assessment, security verdict, invented source records | Reviewer can distinguish missing evidence from no returned matches and investigate or retry later |

Deterministic checks: input validity, request method/path/payload, result schema,
unique IDs/links, exact status/message, failure classification, and CLI exit code.
Human review: whether evidence and uncertainty support a useful next step in the
reviewer's context. Compliance decisions require separate policy and an authorized
reviewer. No model-assisted assessment is needed for M0/M1.

Ownership: OSV supplies source records; client code validates and normalizes them;
CLI code reports observations and failures. The reviewer owns interpretation and
any action. No model inference or remediation action exists in this increment.

Acceptance: all three scenarios have explicit evidence and prohibited claims;
offline tests exercise each result and failure category; ordinary and failure
traces identify responsible code; live verification is recorded separately.

Decision: use Python 3.12 standard-library HTTP and unittest fixtures for a small,
dependency-free boundary. No retries, persistence, orchestration, or deployment.
Mocked transport makes the contract tests repeatable but does not prove real
network/TLS behavior; the separate live check covers that when access permits.
