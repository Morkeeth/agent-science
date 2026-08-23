# RECEIPT — Agent Builder on the default path

**Date:** 2026-08-23 · **Status:** proved LOCALLY in the hosted shape. **Not yet on the
hosted URL** — `deploy.sh` is Oscar's click and this run did not take it.

## What was wrong

`cloud/agent.py` built an ADK `Agent` and nothing called it. `POST /clear` went
straight to `agent_science.clear_script`. So the integration existed as a module and
not as a runtime, which is the exact shape of a claim that survives review because
nobody runs it. `SUBMISSION.md` was honest about this: `⬜ not proved on default
hosted path`.

## What changed

- `cloud/agent.py` gained `run_clearance()` — an `InMemoryRunner` drives the agent, and
  the gap report is lifted out of the tool's own `function_response`, never out of the
  model's prose. If the agent answers without calling `clear_script_tool`, it raises.
  Serving a model's summary as a clearance would be the failure this product exists to
  catch.
- `cloud/service.py` `POST /clear` now runs through the agent by default and stamps
  `engine: "adk" | "direct"` on every report. `GET /health` reports `agent_builder`,
  `adk_version`, and `engine_default`.
- The fallback still serves a clearance if ADK fails, but stamps `engine: "direct"` and
  carries `adk_error`. A silent fallback would let the submission claim Agent Builder on
  a path that had stopped using it.
- `requirements.txt` (new, `google-adk==2.7.1`) + `Dockerfile` installs it.

## The defect found on the way

`_prepare_genai_env()` first pointed google-genai at `GCP_REGION` (`us-central1`) and
every call returned:

    404 NOT_FOUND ... Publisher model
    projects/hack-fleet/locations/us-central1/.../gemini-3.5-flash-lite was not found

`clearance/gemini.py:51` had already recorded the answer in a comment: *"Only the
`global` location publishes these models; every regional endpoint 404s."* The ADK
client needs `GOOGLE_CLOUD_LOCATION=global`, and `deploy.sh` now sets it.

## The receipt — keys stripped, not merely absent

    cd ~/CODE/cleared
    export GCP_PROJECT=hack-fleet GEMINI_MODEL=gemini-3.5-flash PORT=8099
    export PARALLEL_API_KEY="$(cat ~/.config/keys/parallel.key)"
    env -u GEMINI_API_KEY -u GOOGLE_API_KEY .venv-adk/bin/python cloud/service.py

`GET /health`:

    {"ok": true, "service": "agent-science",
     "gemini": true, "gemini_path": "vertex:hack-fleet", "parallel": true,
     "agent_builder": true, "adk_version": "2.7.1", "engine_default": "adk"}

`POST /clear` (`{"script": "The Dust Bowl displaced 2.5 million people from the Great
Plains during the 1930s.", "subject": "dust-bowl"}`):

    engine            adk
    adk_version       2.7.1
    model_routing     vertex:hack-fleet
    adk_tool_calls    ["clear_script_tool"]
    adk_error         null
    ok                true
    claims_extracted  1
    parallel_calls    1

Three integrations on one request, with no Gemini API key in the environment: Vertex
(ADC) answered the model, Parallel made a live search call, and the ADK agent is what
decided to call the tool.

Controls after the change: `python3 tests/test_watch_it_go_red.py` → **72 passed, 0
failed**.

## What is still NOT proved

- **The hosted URL.** `deploy.sh` writes a Secret Manager version, edits IAM and ships a
  billed public revision. Its own header says it is Oscar's click. Until it runs,
  `https://agent-science-568004190078.us-central1.run.app` serves the OLD revision,
  where `engine_default` is absent and Agent Builder is not on the path.
- **The `⬜` in `SUBMISSION.md` stays `⬜`** until `curl <hosted>/health` returns
  `"engine_default": "adk"`. Local is not hosted, and the requirement names the hosted
  path.
- The one-command check when the deploy lands:

      curl -s https://agent-science-568004190078.us-central1.run.app/health \
        | grep -q '"engine_default": "adk"' && echo 3/3 || echo still 2/3
