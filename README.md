# Applied AI Architect Lab

A build-first learning project for designing, testing, and operating enterprise AI agents. The code is written with help from coding agents; the learner owns the problem definition, architecture, controls, verification, and explanation of observed behavior.

## First use case: software dependency assessment

Given a package name, ecosystem, and version, retrieve vulnerability records from the public [OSV API](https://google.github.io/osv.dev/). A later agent will help a reviewer understand the records, cite their sources, express uncertainty, and propose a next step. The application owns validation, permissions, policy enforcement, and any action. An empty OSV result means **no vulnerabilities returned by that source for that query**; it is not proof that a package is secure.

This is a public learning repository. Use synthetic examples. Do not commit company data, internal API details, credentials, personal data, or proprietary policy text. Real internal integrations require an approved environment and separate configuration.

## How we work

1. Define one observable user need and a small, verifiable increment.
2. Predict the request path, responsible components, expected outputs, and likely failures.
3. Let Codex or Claude implement the scoped change.
4. Inspect the diff, run tests, and trace both a successful request and a failure.
5. Record what we learned, which assumptions changed, and the next experiment.

A generated implementation or a passing happy-path demo does not establish understanding or reliability. For each milestone, keep a working example, a trace, a failure case, and a brief architecture decision. Build evaluations early and use errors to choose the next improvement.

## Build sequence

| Stage | Increment | Main architectural question |
| --- | --- | --- |
| 1 | OSV API client and repeatable fixtures | What data did an external source actually return, and how do failures appear? |
| 2 | Evaluation cases and expected behaviors | What counts as a useful, supported assessment? |
| 3 | Model gateway and structured assessment | What may the model infer, and what must the application check? |
| 4 | Controlled tool-calling loop | Who chooses a tool, validates arguments, executes it, and stops the loop? |
| 5 | Evidence grounding and optional RAG | When should context come from an API, documents, or retrieval? |
| 6 | State and memory | What persists during a run or across sessions, for whom, and for how long? |
| 7 | Identity, authorization, approvals, and audit | How are model proposals separated from permitted actions? |
| 8 | Telemetry, metering, evals, and recovery | What happened, what did it cost, and what happens after timeout or crash? |
| 9 | MCP and architectural comparisons | When do MCP, skills, workflows, ReAct, or multiple agents add value? |
| 10 | Deployment and operations | How do we release, monitor, secure, and evolve the system? |

We will add components when a concrete requirement needs them. RAG is optional; it is useful when relevant knowledge lives in documents or search systems. MCP is an integration interface, not a requirement for every tool. Cloud Codex may not reach private corporate APIs; those must be tested in an approved environment.

## Learning and evidence

The [Learning Studio](https://attention-learning-studio.polinati-86.chatgpt.site/) supplies a detailed concept map. [DeepLearning.AI's AI Engineering Skills Map](https://www.deeplearning.ai/resources/ai-engineering-skills) checks broader engineering and product skills. See [docs/LEARNING_PLAN.md](docs/LEARNING_PLAN.md) for the coverage map, milestones, review questions, and evidence rules.

Track each topic as **explained**, **implemented or experimented**, **verified**, or **reviewed**. Keep uncovered topics visible. The project is a practice ground, not a claim that one agent demonstrates every production concern.

## Current state — M0/M1

M0 reviewer acceptance criteria are in `docs/M0_BASELINE.md`. M1 is implemented
and verified with ten offline tests. Live OSV access is not verified; the latest
attempt failed before receiving an HTTP response. No M2 work has started.

First increment: a Python 3.12 read-only client for the OSV vulnerability source.
No LLM, agent loop, service, or telemetry. Uses only the Python standard library;
there are no third-party dependencies to install. Run commands from this repository's root.

## M0: synthetic assessment cases

Cases are recorded in `tests/fixtures/assessment_cases.json` before this increment's
client changes. All use synthetic `example` / `PyPI` / `1.0` package identity.

| Case | Evidence | Expected wording |
| --- | --- | --- |
| OSV returns vulnerabilities | `vulnerabilities.json` | Vulnerabilities returned by this source. |
| OSV returns none | `empty.json` (also tested with `omitted.json`) | No vulnerabilities returned by this source; this is not proof that the package is secure. |
| OSV unavailable or malformed | simulated timeout/HTTP/transport failures or `malformed.json` | Assessment unavailable from this source; no security conclusion can be drawn. |

Failures retain the specific exception name and detail alongside that wording.
The CLI tests check these messages and their exit codes. Empty is never a secure verdict.

## M1: OSV client

API contract: [OSV POST /v1/query documentation](https://google.github.io/osv.dev/post-v1-query/).
Only the package-name/ecosystem/version query is implemented. No LLM calls, RAG,
MCP integration, or deployment are included. The upstream README, `AGENTS.md`,
and `docs/LEARNING_PLAN.md` on main were read through the GitHub connector after
the local fetch failed. Existing uncommitted implementation work was preserved.

## Setup and repeatable tests

```sh
python3.12 -m venv .venv
.venv/bin/python -m unittest discover -s tests -v
```

The tests use synthetic JSON fixtures in `tests/fixtures/` and a mocked HTTP
transport. They require no network and validate the outgoing request, parsing,
deduplication, empty results, malformed responses, timeout, HTTP failure, transport
failure, and invalid inputs. Fixtures are examples, not live OSV recordings.

## Run a query

```sh
.venv/bin/python -m security_assessment lodash npm 4.17.20
.venv/bin/python -m security_assessment lodash npm 4.17.20 --base-url https://api.osv.dev --timeout 15
```

The default base URL is `https://api.osv.dev`; set `OSV_BASE_URL` or pass
`--base-url` to override it. The client appends `/v1/query` to that base URL.
HTTP is supported for local fake servers. Use HTTPS for remote sources.
The client preserves normal proxy settings and TLS certificate verification.

Python usage:

```python
from security_assessment.osv import OSVClient

result = OSVClient(timeout=10).query("lodash", "npm", "4.17.20")
print(result.to_dict())
```

Request path: CLI/Python caller → validated package identity → JSON
`{"package":{"name":"lodash","ecosystem":"npm"},"version":"4.17.20"}`
→ `POST https://api.osv.dev/v1/query` with `Content-Type: application/json`.

Response path: HTTP response → JSON object validation → `vulns` list and ID
validation → immutable `QueryResult` with the queried package identity,
deduplicated vulnerability IDs, canonical `https://osv.dev/vulnerability/<ID>`
source links, and query endpoint. Other OSV metadata is intentionally omitted.

An empty list (or OSV's empty `{}` response) produces status
`no_vulnerabilities_returned` and the message: “No vulnerabilities returned by
this source; this is not proof that the package is secure.” Findings produce
`vulnerabilities_returned`. Neither result is a compliance verdict.

Failures are distinct exceptions: `OSVTimeout`, `OSVHTTPError` (with HTTP status),
`OSVMalformedResponse`, and `OSVTransportError`. Invalid caller input raises
`ValueError` before a request. The CLI prints errors as JSON to stderr and exits
1; valid results exit 0, including findings and empty results. No retries or
pagination are implemented; this client uses the single-package query endpoint.
The timeout applies to blocking socket operations, not a total wall-clock deadline.

## Repeatable request and failure traces

Run `.venv/bin/python -m unittest discover -s tests -v`; the traces below use
the synthetic fixtures and mocked transport, not live OSV findings.

Request trace (`OSVTests.test_request_and_validated_result` in `tests/test_osv.py`):

1. The test calls `OSVClient.query("example", "PyPI", "1.0")` in `security_assessment/osv.py`.
2. `Package.__post_init__` validates identity. `OSVClient.query` builds
   `{"package":{"name":"example","ecosystem":"PyPI"},"version":"1.0"}`.
3. `OSVClient.query` constructs `urllib.request.Request`, method POST, path
   `/v1/query`; the test captures it at mocked `urlopen` and checks URL, headers,
   payload, and timeout.
4. The mock supplies `tests/fixtures/vulnerabilities.json`. `OSVClient.query`
   reads and validates JSON and IDs, deduplicates them, and builds `QueryResult`.
5. `QueryResult.to_dict` returns package identity, source links, and
   `vulnerabilities_returned`. The fixture's duplicate ID is returned once.

Failure trace (`OSVTests.test_recorded_assessment_cases_through_cli`, source_failure case):

1. `security_assessment/__main__.py:main` parses `example PyPI 1.0` and calls
   `OSVClient.query`.
2. Mocked `urlopen` returns `tests/fixtures/malformed.json`, an HTTP 200 response
   containing `{"vulns":[{"id":42}]}`.
3. `OSVClient.query` parses JSON, rejects the non-string ID, and raises
   `OSVMalformedResponse` rather than returning an empty result.
4. `main` catches `OSVError`, emits `source_failure`, error
   `OSVMalformedResponse`, its detail, and the M0 unavailable wording to stderr;
   it returns exit code 1. The test checks that output.

## Separate live smoke check

```sh
.venv/bin/python -m security_assessment.live_smoke
```

This explicitly contacts OSV for `lodash` / `npm` / `4.17.20` and expects at
least one validated finding. It exits 1 on a source failure or an unexpectedly
empty result. It is excluded from the repeatable test suite; live IDs and source
availability can change. Network policy must permit `api.osv.dev`.
