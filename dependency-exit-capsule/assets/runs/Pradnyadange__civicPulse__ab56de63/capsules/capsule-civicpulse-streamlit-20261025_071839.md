# Dependency Exit Capsule: `streamlit`

- **Capsule ID**: `capsule-civicpulse-streamlit-20261025_071839`
- **Generated At**: `2026-10-25T07:18:39.066377+00:00`
- **Status**: **UNVERIFIED**
- **Target Repository**: `civicPulse` (ab56de6)
- **Maintenance Problem**: Dependency 'streamlit' analyzed during static risk triage.

## 1. Observed Evidence

### Risk Indicators
| Indicator | Value | Source | Fetched At |
|---|---|---|---|
| days_since_release | `3` | [https://pypi.org/pypi/streamlit/json](https://pypi.org/pypi/streamlit/json) | 2026-10-25T07:07:15.044448+00:00 |
| yanked | `False` | [https://pypi.org/pypi/streamlit/json](https://pypi.org/pypi/streamlit/json) | 2026-10-25T07:07:15.044448+00:00 |

### Code Usage (174 locations across 15 files)
| File:Line | Kind | Symbol | Covered By Tests |
|---|---|---|---|
| `admin_analytics.py:1` | import | `streamlit` | NO |
| `admin_analytics.py:15` | call | `header` | NO |
| `admin_analytics.py:16` | call | `markdown` | NO |
| `admin_analytics.py:21` | call | `columns` | NO |
| `admin_analytics.py:24` | call | `expander` | NO |
| `admin_analytics.py:26` | call | `markdown` | NO |
| `admin_analytics.py:53` | call | `markdown` | NO |
| `admin_analytics.py:56` | call | `markdown` | NO |
| `admin_analytics.py:63` | call | `columns` | NO |
| `admin_analytics.py:65` | call | `markdown` | NO |
| `admin_analytics.py:72` | call | `markdown` | NO |
| `admin_analytics.py:81` | call | `markdown` | NO |
| `admin_analytics.py:88` | call | `markdown` | NO |
| `admin_analytics.py:89` | call | `markdown` | NO |
| `admin_analytics.py:96` | call | `plotly_chart` | NO |
| `admin_analytics.py:103` | call | `plotly_chart` | NO |
| `admin_analytics.py:113` | call | `plotly_chart` | NO |
| `admin_analytics.py:118` | call | `markdown` | NO |
| `admin_analytics.py:119` | call | `markdown` | NO |
| `admin_analytics.py:129` | call | `button` | NO |
| `admin_analytics.py:130` | call | `spinner` | NO |
| `admin_analytics.py:146` | call | `columns` | NO |
| `admin_analytics.py:149` | call | `container` | NO |
| `admin_analytics.py:150` | call | `markdown` | NO |
| `admin_analytics.py:175` | call | `columns` | NO |
| `admin_analytics.py:177` | call | `button` | NO |
| `admin_analytics.py:179` | call | `rerun` | NO |
| `admin_analytics.py:181` | call | `button` | NO |
| `admin_analytics.py:183` | call | `rerun` | NO |
| `admin_analytics.py:184` | call | `caption` | NO |
| `admin_analytics.py:186` | call | `get` | NO |
| `admin_analytics.py:187` | call | `info` | NO |
| `admin_analytics.py:189` | call | `markdown` | NO |
| `admin_analytics.py:193` | call | `columns` | NO |
| `admin_analytics.py:196` | call | `markdown` | NO |
| `admin_analytics.py:197` | call | `write` | NO |
| `admin_analytics.py:200` | call | `write` | NO |
| `admin_analytics.py:201` | call | `button` | NO |
| `admin_analytics.py:202` | call | `spinner` | NO |
| `admin_analytics.py:205` | call | `success` | NO |
| `admin_analytics.py:206` | call | `rerun` | NO |
| `admin_analytics.py:208` | call | `error` | NO |
| `admin_analytics.py:216` | call | `warning` | NO |
| `admin_analytics.py:231` | call | `columns` | NO |
| `admin_analytics.py:234` | call | `container` | NO |
| `admin_analytics.py:235` | call | `markdown` | NO |
| `admin_analytics.py:263` | call | `columns` | NO |
| `admin_analytics.py:265` | call | `button` | NO |
| `admin_analytics.py:267` | call | `rerun` | NO |
| `admin_analytics.py:269` | call | `button` | NO |
| `admin_analytics.py:271` | call | `rerun` | NO |
| `admin_analytics.py:272` | call | `caption` | NO |
| `admin_analytics.py:274` | call | `error` | NO |
| `admin_analytics.py:276` | call | `warning` | NO |
| `cards_dasboard.py:6` | import | `streamlit` | NO |
| `cards_dasboard.py:11` | call | `cache_data` | NO |
| `cards_dasboard.py:21` | call | `header` | NO |
| `cards_dasboard.py:22` | call | `markdown` | NO |
| `cards_dasboard.py:34` | call | `columns` | NO |
| `cards_dasboard.py:57` | call | `markdown` | NO |
| `cards_dasboard.py:59` | call | `container` | NO |
| `cards_dasboard.py:60` | call | `markdown` | NO |
| `cards_dasboard.py:61` | call | `markdown` | NO |
| `cards_dasboard.py:65` | call | `markdown` | NO |
| `cards_dasboard.py:68` | call | `markdown` | NO |
| `cards_dasboard.py:69` | call | `markdown` | NO |
| `cards_dasboard.py:70` | call | `markdown` | NO |
| `cards_dasboard.py:71` | call | `markdown` | NO |
| `cards_dasboard.py:76` | call | `button` | NO |
| `cards_dasboard.py:83` | call | `expander` | NO |
| `cards_dasboard.py:85` | call | `markdown` | NO |
| `cards_dasboard.py:87` | call | `columns` | NO |
| `cards_dasboard.py:89` | call | `button` | NO |
| `cards_dasboard.py:98` | call | `button` | NO |
| `cards_dasboard.py:106` | call | `markdown` | NO |
| `cards_dasboard.py:109` | call | `columns` | NO |
| `cards_dasboard.py:111` | call | `button` | NO |
| `cards_dasboard.py:113` | call | `rerun` | NO |
| `cards_dasboard.py:115` | call | `button` | NO |
| `cards_dasboard.py:117` | call | `rerun` | NO |
| `cards_dasboard.py:118` | call | `caption` | NO |
| `cards_dasboard.py:121` | call | `markdown` | NO |
| `cards_dasboard.py:123` | call | `container` | NO |
| `cards_dasboard.py:124` | call | `markdown` | NO |
| `cards_dasboard.py:125` | call | `markdown` | NO |
| `cards_dasboard.py:128` | call | `markdown` | NO |
| `cards_dasboard.py:131` | call | `markdown` | NO |
| `cards_dasboard.py:132` | call | `markdown` | NO |
| `cards_dasboard.py:133` | call | `markdown` | NO |
| `cards_dasboard.py:134` | call | `markdown` | NO |
| `cards_dasboard.py:139` | call | `button` | NO |
| `cards_dasboard.py:146` | call | `expander` | NO |
| `cards_dasboard.py:148` | call | `markdown` | NO |
| `cards_dasboard.py:150` | call | `columns` | NO |
| `cards_dasboard.py:152` | call | `button` | NO |
| `cards_dasboard.py:161` | call | `button` | NO |
| `cards_dasboard.py:169` | call | `markdown` | NO |
| `cards_dasboard.py:172` | call | `columns` | NO |
| `cards_dasboard.py:174` | call | `button` | NO |
| `cards_dasboard.py:176` | call | `rerun` | NO |
| `cards_dasboard.py:178` | call | `button` | NO |
| `cards_dasboard.py:180` | call | `rerun` | NO |
| `cards_dasboard.py:181` | call | `caption` | NO |
| `cards_dasboard.py:184` | call | `markdown` | NO |
| `cards_dasboard.py:186` | call | `container` | NO |
| `cards_dasboard.py:187` | call | `markdown` | NO |
| `cards_dasboard.py:188` | call | `markdown` | NO |
| `cards_dasboard.py:191` | call | `markdown` | NO |
| `cards_dasboard.py:194` | call | `markdown` | NO |
| `cards_dasboard.py:195` | call | `markdown` | NO |
| `cards_dasboard.py:196` | call | `markdown` | NO |
| `cards_dasboard.py:197` | call | `markdown` | NO |
| `cards_dasboard.py:202` | call | `button` | NO |
| `cards_dasboard.py:209` | call | `expander` | NO |
| `cards_dasboard.py:211` | call | `markdown` | NO |
| `cards_dasboard.py:213` | call | `columns` | NO |
| `cards_dasboard.py:215` | call | `button` | NO |
| `cards_dasboard.py:224` | call | `button` | NO |
| `cards_dasboard.py:232` | call | `markdown` | NO |
| `cards_dasboard.py:235` | call | `columns` | NO |
| `cards_dasboard.py:237` | call | `button` | NO |
| `cards_dasboard.py:239` | call | `rerun` | NO |
| `cards_dasboard.py:241` | call | `button` | NO |
| `cards_dasboard.py:243` | call | `rerun` | NO |
| `cards_dasboard.py:244` | call | `caption` | NO |
| `cards_dasboard.py:247` | call | `spinner` | NO |
| `cards_dasboard.py:250` | call | `toast` | NO |
| `cards_dasboard.py:251` | call | `rerun` | NO |
| `interface.py:3` | import | `streamlit` | NO |
| `interface.py:6` | call | `set_page_config` | NO |
| `interface.py:14` | call | `markdown` | NO |
| `interface.py:111` | call | `header` | NO |
| `interface.py:112` | call | `markdown` | NO |
| `interface.py:114` | call | `text_area` | NO |
| `interface.py:115` | call | `button` | NO |
| `interface.py:117` | call | `warning` | NO |
| `interface.py:119` | call | `spinner` | NO |
| `interface.py:121` | call | `container` | NO |
| `interface.py:122` | call | `markdown` | NO |
| `interface.py:123` | call | `markdown` | NO |
| `interface.py:133` | call | `markdown` | NO |
| `interface.py:142` | call | `columns` | NO |
| `interface.py:145` | call | `button` | NO |
| `interface.py:152` | call | `button` | NO |
| `interface.py:160` | call | `subheader` | NO |
| `interface.py:162` | call | `text_input` | NO |
| `interface.py:163` | call | `text_input` | NO |
| `interface.py:165` | call | `button` | NO |
| `interface.py:168` | call | `success` | NO |
| `interface.py:169` | call | `rerun` | NO |
| `interface.py:171` | call | `error` | NO |
| `interface.py:179` | call | `title` | NO |
| `interface.py:180` | call | `markdown` | NO |
| `interface.py:187` | call | `button` | NO |
| `interface.py:189` | call | `rerun` | NO |
| `interface.py:193` | call | `get` | NO |
| `interface.py:197` | call | `title` | NO |
| `interface.py:199` | call | `tabs` | NO |
| `interface.py:210` | call | `button` | NO |
| `interface.py:211` | call | `clear` | NO |
| `interface.py:212` | call | `rerun` | NO |
| `report_complaint.py:2` | import | `streamlit` | NO |
| `report_complaint.py:9` | call | `header` | NO |
| `report_complaint.py:10` | call | `markdown` | NO |
| `report_complaint.py:12` | call | `container` | NO |
| `report_complaint.py:13` | call | `columns` | NO |
| `report_complaint.py:15` | call | `text_input` | NO |
| `report_complaint.py:17` | call | `selectbox` | NO |
| `report_complaint.py:25` | call | `text_area` | NO |
| `report_complaint.py:33` | call | `button` | NO |
| `report_complaint.py:35` | call | `spinner` | NO |
| `report_complaint.py:39` | call | `success` | NO |
| `report_complaint.py:41` | call | `error` | NO |
| `report_complaint.py:43` | call | `warning` | NO |

### Test Results Diff
- **Baseline**: 0 passed, 0 failed
- **Candidate**: 0 passed, 0 failed
- **New Failures**: 0
- **pip check**: Tests not run in static analyze mode.

## 2. AI-Generated Proposal
- **Proposed Replacement**: `no_valid_proposal` (stdlib)
- **Provenance**: Provider `ollama` | Model `llama3.1:8b` | License `LLAMA 3.1 COMMUNITY LICENSE AGREEMENT`
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
| `assets/runs/Pradnyadange__civicPulse__ab56de63/evidence/streamlit_raw_model_response.json` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `ollama run llama3.1:8b` | 2026-10-25T07:18:39.066356+00:00 |
