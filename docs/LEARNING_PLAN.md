# Learning plan and evidence ledger

## Goal

Become capable of designing and defending an applied AI system: choose a useful problem, decide where a model helps, integrate data and APIs, control actions, evaluate uncertain outputs, and operate the result. Coding assistants can implement; the learner must predict, inspect, verify, and explain behavior.

The first case is a public, synthetic **dependency assessment assistant** backed by the [OSV API](https://google.github.io/osv.dev/). A user supplies package, ecosystem, and version. The system retrieves vulnerability records, presents evidence and uncertainty, and later proposes a reviewer action. A public vulnerability source alone cannot determine organizational compliance or guarantee that software is safe. An organization's policy and authorized reviewer would be separate inputs in a real deployment.

## Milestones

Current evidence: M0 baseline is implemented in `docs/M0_BASELINE.md` and
`tests/fixtures/assessment_cases.json`. M1 is implemented with offline verification
in `tests/test_osv.py`. Live OSV verification is blocked by workspace networking.
Learner review is pending. M2–M6 are not implemented.

### M0 — Problem and evaluation baseline

- Write three synthetic reviewer scenarios: a query with returned vulnerabilities, one with none returned, and an unavailable or malformed source.
- Specify the desired answer, evidence requirements, prohibited claims, and how a reviewer would judge usefulness.
- Decide which checks are deterministic and which require human or model-assisted assessment.

### M1 — External API boundary

- Implement a Python client for OSV package/version queries, a configurable base URL, response validation, timeouts, and distinct errors.
- Use fixtures or a fake endpoint for repeatable tests. Run a separate live smoke check when network access permits.
- Inspect one request and response trace. Record the difference between an empty result, a request failure, and a trustworthy conclusion.

### M2 — Model boundary

- Add one configured model call that receives a normalized result and produces a structured assessment with source references and explicit uncertainty.
- Validate the output in application code; record token usage, latency, and failures where available.
- Evaluate both supported and unsupported claims with the M0 cases.

### M3 — Agency and control

- Compare a fixed workflow with model-selected tool calling on the same cases.
- Bound steps, arguments, destinations, and outputs. Observe a tool error and a deliberately misleading external response.
- Explain what the model proposes and what the application actually executes.

### M4 — Knowledge and memory

- Add policy documents or a separate policy source only when the decision requires them. Compare direct context, API access, keyword retrieval, and RAG.
- Keep source attribution, freshness, access scope, and evidence quality visible.
- Add conversation state and longer-lived memory only for a defined need; test isolation and deletion behavior.

### M5 — Enterprise controls and operations

- Introduce identity, scoped permissions, approvals, audit records, redaction, retries, idempotency, cancellation, durable/background execution, tracing, metering, and budgets in context.
- Test partial failure and uncertain outcomes. Distinguish a proposed action from a completed action.
- Deploy to an approved environment with CI/CD, monitoring, incident response, and measured cost/latency.

### M6 — Architecture comparison and transfer

- Compare direct code, workflow, ReAct, MCP-backed tools, specialist agents, and a multi-agent design against the same task and evaluation set.
- Record where complexity improved outcomes and where it raised cost or risk.
- Apply the reasoning to a second domain to check transfer of learning.

These are milestones, not a mandate to add every component to one production design. Revise them using observed results.

## Learning Studio coverage

Source: [Agentic Architect · Connected Learning Studio](https://attention-learning-studio.polinati-86.chatgpt.site/). It has eight areas. Maintain the lesson-level checklist in the studio and record evidence here as work lands.

| Area | Planned practical evidence | Current status |
| --- | --- | --- |
| 01 · How a model becomes part of an agent | Token/context experiments, model boundary, inference traces, deterministic controls | Previously studied conceptually; project evidence pending |
| 02 · Knowledge, context, retrieval, and memory | API versus documents, grounding, RAG experiment, memory isolation | Pending |
| 03 · Tools, workflows, and agency | OSV tool, bounded execution, fallbacks, action boundary | Pending |
| 04 · Single-agent and multi-agent designs | Same-case architecture comparison with measurements | Pending |
| 05 · Computer-science and distributed-system foundations in context | State, concurrency, queues, timeout/retry, duplicate effect experiments | Pending |
| 06 · Quality, safety, and operations | Evaluations, traces, prompt-injection cases, audit and incident exercise | Pending |
| 07 · Cloud-native realization | Approved deployment, identity, secrets, observability, scaling and cost | Pending |
| 08 · Architecture synthesis across domains | Decision records, review presentation, second-domain transfer | Pending |

Some model internals, training, and distributed-system principles require focused labs because an API call or a local demo cannot expose or prove them.

## DeepLearning.AI skills map coverage

Source: [AI Engineering Skills Map](https://www.deeplearning.ai/resources/ai-engineering-skills), last seen October 2026. It names four pillars and 20 skills. Use them as a breadth check rather than a second sequential course.

| Pillar | Exact skill names from the map | How we practice |
| --- | --- | --- |
| Building and deploying AI applications | LLM foundations; Grounding models with data; Building agentic systems; Evaluation-driven development; Operating in production; Machine learning foundations | Model/data/agent experiments, eval loop, operations, and separate ML labs |
| Software engineering fundamentals | Building full-stack applications; Managing data; Designing system architectures; Making systems secure and reliable; Scaling and operating in production | API and UI boundaries, state/data decisions, failure tests, deployment and architecture notes |
| Using coding agents | Directing the workflow; Enabling agent autonomy; Reviewing the work; Customizing the agent and its environment; Coding agent foundations | Scoped Codex/Claude tasks, review evidence, AGENTS.md, context and permission management |
| Shaping the build | Driving the build loop; Making product decisions; Communicating and leading; High agency ownership | Reviewer scenarios, success measures, stakeholder-style design explanation, iterative decisions |

## Review record template

For each completed increment, append a dated note with:

- **User need and expected behavior:**
- **Architecture and owner of each decision:**
- **Ordinary execution trace:**
- **Failure or adversarial trace:**
- **Tests/evals and observed results:**
- **Cost/latency/usage evidence, if available:**
- **What the learner can explain now:**
- **Open questions and next experiment:**

Status terms: **explained** = can describe mechanism; **implemented/experimented** = observed a running example; **verified** = behavior supported by tests/traces; **reviewed** = can defend choice and tradeoff. None of these is implied by code generation alone.

## Initial decision notes

- Python 3.12 is the starting runtime because it supports compact API and agent experiments and is familiar to the learner. Reassess only for a concrete requirement.
- OSV supplies public vulnerability data. Internal compliance policy, credentials, and corporate network access are outside this public repository.
- Build an evaluation baseline before the first LLM call. Keep API tests deterministic and live checks separate.
- RAG, MCP, skills, and multi-agent orchestration are topics to evaluate as requirements arise. A skill may mean a prompt instruction, a code-backed capability, or a collection of tools; state the intended meaning in each design.

## Review record — 2026-10-12 — M0/M1

- **User need and expected behavior:** Given package/ecosystem/version, report
  OSV findings, no returned matches, or source failure with evidence and uncertainty.
  Reviewer scenarios and prohibited claims are in `M0_BASELINE.md`.
- **Architecture and owner of each decision:** OSV owns source records;
  `OSVClient.query` owns validated requests and normalized evidence;
  CLI `main` owns output and exit codes. A reviewer owns interpretation.
  Python standard-library HTTP and fixture tests keep this boundary small.
- **Ordinary execution trace:** `test_request_and_validated_result` →
  `Package.__post_init__` → `OSVClient.query` → POST `/v1/query` → fixture
  JSON validation → deduplicated IDs/links → `QueryResult.to_dict`.
- **Failure trace:** CLI case test → `main` → `OSVClient.query` → malformed
  fixture ID 42 → `OSVMalformedResponse` → source_failure JSON on stderr, exit 1.
- **Tests/evals and observed results:** 10 offline tests passed under Python 3.12;
  `git diff --check` passed. Timeout, HTTP 400/429/500, transport failure,
  malformed JSON/schema, empty and omitted lists exercised. Live check exited 1:
  `OSVTransportError`, `[Errno 1] Operation not permitted`; live API not verified.
- **Cost/latency/usage evidence:** No model usage. Offline suite completed in
  approximately 0.03 seconds on this workspace; no live latency claim.
- **What the learner can explain now:** Evidence supports tracing request
  construction, response validation, and failure reporting. Learner understanding
  and architecture defense remain unreviewed.
- **Open questions and next experiment:** Review M0 usefulness criteria and M1
  traces with the learner; repeat the live check when OSV network access permits.
  No later milestone started.
- **Checkout limitation:** Local branch work at initial commit aa4100b lacked
  the instruction documents. Fetch failed because proxy port 8080 was unreachable.
  Documents were read/copied from GitHub main through the connector; existing
  uncommitted work was retained. This was not a Git merge or verified full sync.

## Review record — 2026-10-13 — M0/M1 checkpoint and network diagnosis

- Checkpoint commit: `c07f3fe` preserves the entire existing increment.
- Reviewed the three cases against `M0_BASELINE.md`: findings carry IDs/links;
  empty results explicitly disclaim security; failures carry a distinct category
  and never become empty success. This is a code/evidence review, not proof of
  learner understanding or an organizational compliance decision.
- Reviewed request trace: `OSVClient.query` validates `Package`, builds JSON,
  calls `urlopen`, validates IDs, and returns `QueryResult`; the fixture test
  captures the actual Request object and checks method, path, body, and timeout.
- Reviewed malformed trace: ID 42 is rejected by `OSVClient.query`; CLI `main`
  catches `OSVMalformedResponse` and reports source_failure, exit 1.
- Exact offline command: `.venv/bin/python -m unittest discover -s tests -v`;
  ten tests passed in 0.022 seconds. `git diff --check` passed.
- Actual live attempt command: `.venv/bin/python -m security_assessment.live_smoke`.
  Intended request: POST `https://api.osv.dev/v1/query`, JSON
  `{"package":{"name":"lodash","ecosystem":"npm"},"version":"4.17.20"}`,
  timeout 15 seconds. `live_smoke.main` calls `OSVClient.query`; `urlopen` fails
  with `[Errno 1] Operation not permitted`; client raises `OSVTransportError`;
  smoke reports the error and exits 1. No HTTP status, response, or IDs received.
  The request was attempted, not confirmed delivered to OSV.
- Environment status: restricted, enforced revision 13; GitHub permitted,
  api.osv.dev absent. Configured proxy is proxy:8080; TCP reachability checks to
  that proxy fail with PermissionError. Git fetch also reports proxy connection
  failure. Destination-policy denial and proxy reachability are separate issues.
  No proxy bypass, policy-file edits, credential reads, or route changes attempted.
- Save/republish is blocked: only a read-only environment-status tool is exposed.
  Requested the user update the allowlist and republish via environment settings.
- `git fetch origin main` failed; upstream README, AGENTS.md, and learning plan
  read through the GitHub connector. Remote main observed at cac363950edb6dc874f004196c19a9afb8f55ff0.
  Restored full upstream README guidance and retained implementation commands;
  AGENTS.md is unchanged from main; ledger retains upstream roadmap plus evidence.
- Remaining verification: successful live OSV request after approved republish,
  and learner review. M2 remains out of scope.
