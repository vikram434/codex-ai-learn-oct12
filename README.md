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

## Current state

The repository began with only this README. The first implementation task is the OSV API client. As code lands, update this section with actual run commands and results rather than anticipated ones.
