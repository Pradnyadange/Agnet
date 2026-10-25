# Dependency Exit Capsule: `fastapi`

- **Capsule ID**: `capsule-gpt-researcher-fastapi-20261024_195655`
- **Generated At**: `2026-10-24T19:56:55.050995+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `gpt-researcher` (47695db)
- **Maintenance Problem**: Dependency 'fastapi' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `1` | [https://pypi.org/pypi/fastapi/json](https://pypi.org/pypi/fastapi/json) | 2026-10-24T19:52:17.528549+00:00 |
| yanked | `False` | [https://pypi.org/pypi/fastapi/json](https://pypi.org/pypi/fastapi/json) | 2026-10-24T19:52:17.528549+00:00 |

### Code Usage (48 locations across 364 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `backend/chat/chat.py:4` | import | `fastapi.WebSocket` | NO |
| `backend/report_type/basic_report/basic_report.py:3` | import | `fastapi.WebSocket` | NO |
| `backend/report_type/deep_research/example.py:2` | import | `fastapi.WebSocket` | NO |
| `backend/report_type/detailed_report/detailed_report.py:5` | import | `fastapi.WebSocket` | NO |
| `backend/server/app.py:9` | import | `fastapi.FastAPI` | NO |
| `backend/server/app.py:9` | import | `fastapi.Request` | NO |
| `backend/server/app.py:9` | import | `fastapi.WebSocket` | NO |
| `backend/server/app.py:9` | import | `fastapi.WebSocketDisconnect` | NO |
| `backend/server/app.py:9` | import | `fastapi.Form` | NO |
| `backend/server/app.py:9` | import | `fastapi.HTTPException` | NO |
| `backend/server/app.py:13` | import | `fastapi.responses.HTMLResponse` | NO |
| `backend/server/app.py:13` | import | `fastapi.responses.RedirectResponse` | NO |
| `backend/server/app.py:13` | import | `fastapi.responses.FileResponse` | NO |
| `backend/server/app.py:14` | import | `fastapi.templating.Jinja2Templates` | NO |
| `backend/server/app.py:23` | call | `FastAPI` | NO |
| `backend/server/app.py:26` | call | `Jinja2Templates` | NO |
| `backend/server/app.py:179` | call | `Form` | NO |
| `backend/server/app.py:191` | call | `RedirectResponse` | NO |
| `backend/server/app.py:196` | call | `RedirectResponse` | NO |
| `backend/server/app.py:201` | call | `RedirectResponse` | NO |
| `backend/server/app.py:206` | call | `RedirectResponse` | NO |
| `backend/server/app.py:221` | call | `HTTPException` | NO |
| `backend/server/app.py:229` | call | `HTTPException` | NO |
| `backend/server/app.py:243` | call | `HTTPException` | NO |
| `backend/server/app.py:299` | call | `HTTPException` | NO |
| `backend/server/app.py:337` | call | `HTTPException` | NO |
| `backend/server/app.py:346` | call | `HTTPException` | NO |
| `backend/server/app.py:431` | call | `HTTPException` | NO |
| `backend/server/app.py:438` | call | `HTTPException` | NO |
| `backend/server/app.py:547` | call | `HTTPException` | NO |
| `backend/server/app.py:556` | call | `HTTPException` | NO |
| `backend/server/app.py:647` | call | `HTTPException` | NO |
| `backend/server/app.py:670` | call | `HTTPException` | NO |
| `backend/server/app.py:692` | call | `HTTPException` | NO |
| `backend/server/app.py:717` | call | `HTTPException` | NO |
| `backend/server/app.py:754` | call | `HTTPException` | NO |
| `backend/server/server_utils.py:3` | import | `fastapi.WebSocket` | NO |
| `backend/server/server_utils.py:3` | import | `fastapi.WebSocketDisconnect` | NO |
| `backend/server/websocket_manager.py:4` | import | `fastapi.WebSocket` | NO |
| `backend/server/websocket_manager.py:4` | import | `fastapi.WebSocketDisconnect` | NO |
| `tests/backend/test_self_hosted_frontend_assets.py:4` | import | `fastapi.testclient.TestClient` | NO |
| `tests/backend/test_self_hosted_frontend_assets.py:33` | call | `TestClient` | NO |
| `tests/backend/test_websocket_disconnect_cleanup.py:6` | import | `fastapi.testclient.TestClient` | NO |
| `tests/backend/test_websocket_disconnect_cleanup.py:25` | call | `TestClient` | NO |
| `tests/test_logging.py:3` | import | `fastapi.WebSocket` | NO |
| `tests/test_logging_output.py:6` | import | `fastapi.WebSocket` | NO |
| `tests/test_security_fix.py:13` | import | `fastapi.HTTPException` | NO |
| `tests/test_security_fix.py:14` | import | `fastapi.responses.JSONResponse` | NO |

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `no_valid_proposal` (stdlib)
- **Provenance**: Provider `ollama` | Model `gemma2:2b` | License `Gemma Terms of Use `
- **API Coverage Gate**: 0%

### Migration Steps

### Suggested Tests

### Compatibility Gaps & Open Concerns
- [AI] Model failed to return valid JSON and no rule-based fallback exists.
- [OBSERVED] Static analysis mode only: test execution not run.
- [OBSERVED] Public repositories and Python projects only.
- [OBSERVED] Small models can propose weak replacements; validation gate determines acceptance.

## 3. Evidence Hashes
| Evidence File | SHA-256 | Command | Captured At |
|---|---|---|---|
| `assets/runs/Pradnyadange__gpt-researcher__47695db3/evidence/fastapi_raw_model_response.json` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `ollama run gemma2:2b` | 2026-10-24T19:56:55.050974+00:00 |
