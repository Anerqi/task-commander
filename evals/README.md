# Task Commander × skill-up

Automated port of the six manual scenarios in `tests/behavioral-smoke.md`.

- Fixtures are **reused in place** (`context.repo_fixture: tests/fixtures/behavioral-smoke/<case>/project`), so `input.md` and the fixture tree stay the single source.
- The installed Skill **excludes `tests/`**, which enforces the "do not look at criteria / sibling fixtures / results" rule physically instead of by prompt.
- Each case has two independent judges on one agent run:
  - `disk` (script): deterministic checks on what the agent left on disk — typo fixed with a minimal diff, three sections with facts from `facts.md`, `truncate()` behaviour incl. `max_len=0` and negatives, round-1 receipt and product files untouched by hash, task row not accepted, etc.
  - `behavior` (agent_judge): the rubric items only an LLM can grade — role preservation, dispatch prompt shape, self-check/receipt wording, exact state labels.
- `max_retries: 0`: a provider error stays INCOMPLETE and the failed attempt is kept, matching the smoke protocol.

## Run

```bash
skill-up validate evals/eval.yaml
# provider/model are supplied per run so no host/model identity is committed
export EVAL_PROVIDER=<provider> EVAL_MODEL=<model> EVAL_BASE_URL=<openai-compatible-url>
export EVAL_JUDGE_MODEL=<provider>/<model> <PROVIDER>_API_KEY=<key>
skill-up run evals/eval.yaml                         # OpenCode by default
skill-up run evals/eval.yaml --engine codex          # same cases on another host
skill-up run evals/eval.yaml --include-case-name "0[36]-*"   # just the two Commander cases
skill-up run evals/eval.yaml --baseline              # with vs without the Skill
```

`environment.type: none` runs on the current machine with full write access to the case workspace; run inside a container locally.

## Mapping to the old report template

| Old field | skill-up |
|---|---|
| Observed Verdict | case status in `result.json` / JUnit |
| Artifact / Transcript Pointer | `<output-dir>/<case>/…/outputs/` (transcript + collected workspace files) |
| Model / Host version | recorded in the report header |
| unmeasured (tokens, latency) | now measured per case |

## Known gaps

- "Read the brief before editing" (05) and "did not run the tests itself" (06) are judged from the transcript by the LLM judge; no deterministic tool-order assertion yet.
- 02/03/06 disk checks pass on an untouched workspace by design (the correct action there is mostly *not* writing); the verdict for those cases leans on the `behavior` judge.
- CI needs repository variables `EVAL_PROVIDER`, `EVAL_MODEL`, `EVAL_BASE_URL`, `EVAL_JUDGE_MODEL` and secret `EVAL_API_KEY`.
- A judge model different from the model under test gives a more independent grade.
