import json
import os
import subprocess
import sys
from pathlib import Path
import streamlit as st

# Set page config
st.set_page_config(
    page_title="Dependency Exit Capsule Viewer",
    page_icon="🛡️",
    layout="wide"
)

# Load theme CSS
css_path = Path(__file__).parent / "viewer" / "theme.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

from viewer.data import load_capsules, load_manifest, load_evidence_file
from viewer.components import badge, render_stat_card
from viewer.graph import render_graph_network

# Initialize session state for selected capsule
if "selected_capsule_id" not in st.session_state:
    st.session_state["selected_capsule_id"] = None
if "run_mode" not in st.session_state:
    st.session_state["run_mode"] = "SAVED"

# Load capsules
capsules = load_capsules("assets/capsules")
manifest = load_manifest("assets/manifest.json")

# Header & Run Mode Badge
latest_timestamp = manifest.get("generated_at", "N/A") if manifest else (capsules[0].get("generated_at", "N/A") if capsules else "N/A")
run_badge_label = f"SAVED RUN, {latest_timestamp[:19].replace('T', ' ')}" if st.session_state["run_mode"] == "SAVED" else "LIVE RUN"

col_title, col_mode = st.columns([4, 2])
with col_title:
    st.markdown("<h2 style='margin-bottom:0;'>Dependency Exit Capsule Viewer</h2>", unsafe_allow_html=True)
with col_mode:
    st.markdown(
        f"<div style='text-align:right; margin-top:15px;'><span class='run-mode-badge'>{run_badge_label}</span></div>",
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: #212c3b; margin-top:5px; margin-bottom:15px;'>", unsafe_allow_html=True)

# Navigation tabs
tabs = st.tabs(["Overview", "Capsule", "Blast radius", "Test proof", "Integrity", "About"])

# If no capsules found
if not capsules:
    with tabs[0]:
        st.warning("No capsules found in `assets/capsules`. Run the pipeline first:")
        st.code(
            "python scripts/scan_risk.py --repo <path> --out assets/scan.json\n"
            "python scripts/map_usage.py --repo <path> --dep <name> --out assets/usage_<name>.json\n"
            "python scripts/propose_replacement.py --dep <name> --usage-file assets/usage_<name>.json --provider ollama --out assets/proposal_<name>.json\n"
            "python scripts/run_diff_tests.py --repo <path> --proposal assets/proposal_<name>.json --out assets/diff_<name>.json\n"
            "python scripts/build_capsule.py --dep <name> --out assets/capsules/\n"
            "python scripts/verify_capsule.py assets/manifest.json"
        )
    st.stop()

# Set default selection if none
if st.session_state["selected_capsule_id"] is None and capsules:
    st.session_state["selected_capsule_id"] = capsules[0]["capsule_id"]

# Find currently selected capsule
current_capsule = next((c for c in capsules if c["capsule_id"] == st.session_state["selected_capsule_id"]), capsules[0])

# ==========================================
# TAB 1: OVERVIEW
# ==========================================
with tabs[0]:
    total_capsules = len(capsules)
    verified_count = sum(1 for c in capsules if c.get("status") == "verified")
    unverified_count = sum(1 for c in capsules if c.get("status") == "unverified")
    not_testable_count = sum(1 for c in capsules if c.get("status") == "not_testable")
    failed_count = sum(1 for c in capsules if c.get("status") == "failed")
    scanned_count = max([c["observed"]["scan"]["files_scanned"] for c in capsules] or [0])
    
    # 5 Summary cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_stat_card("Files Scanned", scanned_count)
    with c2:
        render_stat_card("Capsules Built", total_capsules)
    with c3:
        render_stat_card("Verified", verified_count)
    with c4:
        render_stat_card("Unverified", unverified_count)
    with c5:
        render_stat_card("Failed", failed_count)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Scanned Dependencies")
    
    # Overview table
    table_rows = []
    for c in capsules:
        dep_name = c["dependency"]["name"]
        decl_spec = c["dependency"]["declared_specifier"] or "any"
        
        # Risk indicators: days since release
        days_since = "unavailable"
        for r in c["observed"]["risk_indicators"]:
            if r["id"] == "days_since_release":
                days_since = f"{r['value']} days" if isinstance(r['value'], int) else str(r['value'])
                
        usage_count = len(c["observed"]["usage_locations"])
        proposed_change = c["ai_generated"]["proposed_replacement"]["name"]
        prov_type = c["ai_generated"]["provenance"]["provider"]
        prov_label = "RULE-BASED" if "rule_based" in prov_type else f"AI ({c['ai_generated']['provenance']['model_id']})"
        st_badge = badge(c["status"], c["status"])
        
        table_rows.append({
            "capsule_id": c["capsule_id"],
            "name": dep_name,
            "version": decl_spec,
            "days_since": days_since,
            "usages": usage_count,
            "proposal": proposed_change,
            "provenance": prov_label,
            "status_html": st_badge
        })

    # Render interactive selectbox or buttons to open capsule
    dep_options = [c["dependency"]["name"] for c in capsules]
    current_dep_name = current_capsule["dependency"]["name"]
    selected_name = st.selectbox(
        "Select Dependency Capsule to inspect:",
        options=dep_options,
        index=dep_options.index(current_dep_name) if current_dep_name in dep_options else 0
    )
    if selected_name != current_dep_name:
        for c in capsules:
            if c["dependency"]["name"] == selected_name:
                st.session_state["selected_capsule_id"] = c["capsule_id"]
                st.rerun()

    # HTML table
    table_html = """
    <table class="custom-table">
      <thead>
        <tr>
          <th>Dependency</th>
          <th>Declared Version</th>
          <th>Staleness</th>
          <th>AST Usages</th>
          <th>Proposed Change</th>
          <th>Provenance</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
    """
    for r in table_rows:
        table_html += f"""
        <tr>
          <td><strong>{r['name']}</strong></td>
          <td><code>{r['version']}</code></td>
          <td>{r['days_since']}</td>
          <td>{r['usages']} sites</td>
          <td><code>{r['proposal']}</code></td>
          <td>{r['provenance']}</td>
          <td>{r['status_html']}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)


# ==========================================
# TAB 2: CAPSULE
# ==========================================
with tabs[1]:
    dep_meta = current_capsule["dependency"]
    target_repo = current_capsule["target_repo"]
    status_val = current_capsule["status"]
    
    # Header
    st.markdown(
        f"""
        <div style="background-color:#161D26; padding:15px; border-radius:6px; margin-bottom:15px; border:1px solid #283340;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <span style="font-size:1.4rem; font-weight:700;">{dep_meta['name']}</span>
              <span style="color:#9AA7B4; margin-left:10px;">| {current_capsule['capsule_type']}</span>
              <span style="color:#9AA7B4; margin-left:10px;">| <code>{current_capsule['capsule_id']}</code></span>
            </div>
            <div>
              {badge(status_val, status_val)}
            </div>
          </div>
          <div style="margin-top:8px; font-size:0.85rem; color:#9AA7B4;">
            Repository: <code>{target_repo['name']}</code> (SHA: <code>{target_repo['commit_sha'][:8]}</code>) | Saved: {current_capsule['generated_at']}
          </div>
          <div style="margin-top:6px; font-size:0.9rem; color:#E6EDF3;">
            <em>{current_capsule['maintenance_problem']}</em>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Warning banners
    usage_count = len(current_capsule["observed"]["usage_locations"])
    prov_prov = current_capsule["ai_generated"]["provenance"]["provider"]
    if usage_count == 0:
        st.warning("⚠️ Warning: This capsule contains a proposal but has 0 identified usage locations in the repository.")
    if "rule_based" in prov_prov:
        st.info("ℹ️ Note: This proposal was generated by the deterministic rule-based fallback knowledge base, not an AI model.")

    # Two columns: Observed (left) vs AI-generated (right)
    col_obs, col_ai = st.columns(2)
    
    with col_obs:
        st.markdown(
            f"""
            <div class="col-observed">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h4 style="margin:0; color:#2DD4BF;">Observed Evidence</h4>
                {badge('OBSERVED', 'observed')}
              </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("**Risk Indicators**")
        for r in current_capsule["observed"]["risk_indicators"]:
            st.markdown(f"- **{r['id']}**: `{r['value']}` (Fetched: {r['fetched_at'][:19]})")
            st.caption(f"Source: {r['source_url']}")
            
        st.markdown(f"**AST Usage Sites ({len(current_capsule['observed']['usage_locations'])})**")
        if current_capsule["observed"]["usage_locations"]:
            u_html = "<table class='custom-table'><thead><tr><th>File:Line</th><th>Symbol</th><th>Covered</th></tr></thead><tbody>"
            for u in current_capsule["observed"]["usage_locations"]:
                cov_str = "<span style='color:#4ADE80;'>✓ YES</span>" if u["covered_by_tests"] else "<span style='color:#FBBF24;'>○ NO</span>"
                u_html += f"<tr><td><code>{u['file']}:{u['line']}</code></td><td><code>{u['symbol']}</code></td><td>{cov_str}</td></tr>"
            u_html += "</tbody></table>"
            st.markdown(u_html, unsafe_allow_html=True)
        else:
            st.caption("No usage locations recorded.")
            
        st.markdown("**Test Summary**")
        base = current_capsule["observed"]["test_results"]["baseline"]
        cand = current_capsule["observed"]["test_results"]["candidate"]
        st.markdown(f"- Baseline: **{base['passed']}** passed, **{base['failed']}** failed")
        st.markdown(f"- Candidate: **{cand['passed']}** passed, **{cand['failed']}** failed")
        st.markdown(f"- pip check: `{current_capsule['observed']['test_results']['pip_check']['candidate']}`")
        
        st.markdown("**Evidence Files**")
        for ev in current_capsule["observed"]["evidence"]:
            ev_p = ev["path"]
            ev_name = Path(ev_p).name
            st.markdown(f"- `{ev_name}` (`{ev['sha256'][:8]}...`)")
            content = load_evidence_file(ev_p)
            if content:
                with st.expander(f"View {ev_name}"):
                    st.code(content)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_ai:
        st.markdown(
            f"""
            <div class="col-ai">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h4 style="margin:0; color:#A78BFA;">AI-Generated Proposal</h4>
                {badge('AI-GENERATED', 'ai')}
              </div>
            """,
            unsafe_allow_html=True
        )
        
        cand = current_capsule["ai_generated"]["proposed_replacement"]
        st.markdown(f"**Proposed Replacement**: `{cand['name']}` ({cand['type']})")
        
        st.markdown("**Migration Steps**")
        for s in current_capsule["ai_generated"]["migration_steps"]:
            st.markdown(f"1. {s}")
            
        st.markdown("**Suggested Tests**")
        for t in current_capsule["ai_generated"]["suggested_tests"]:
            st.markdown(f"- {t}")
            
        st.markdown("**Gap Analysis**")
        for g in current_capsule["ai_generated"]["gap_analysis"]:
            st.markdown(f"- {g}")
            
        prov = current_capsule["ai_generated"]["provenance"]
        st.markdown("<hr style='border-color:#2d3b4d;'>", unsafe_allow_html=True)
        st.markdown("**Provenance Box**")
        st.markdown(f"- Provider: `{prov['provider']}`")
        st.markdown(f"- Model ID: `{prov['model_id']}`")
        st.markdown(f"- License: `{prov['model_license_name']}`")
        st.markdown(f"- Validation Gate Passed: `{prov['validation']['passed']}`")
        st.markdown(f"- API Coverage: `{int(prov['validation']['api_coverage'] * 100)}%`")
        if prov.get("raw_response_path") and prov["raw_response_path"] != "N/A":
            raw_c = load_evidence_file(prov["raw_response_path"])
            if raw_c:
                with st.expander("View Raw Model Response"):
                    st.code(raw_c)
        st.markdown("</div>", unsafe_allow_html=True)

    # Below: Compatibility gaps and open concerns tagged OBSERVED or AI
    st.markdown("### Compatibility Gaps and Open Concerns")
    for g in current_capsule["ai_generated"]["gap_analysis"]:
        st.markdown(f"- {badge('AI', 'ai')} {g}", unsafe_allow_html=True)
    for lim in current_capsule["limitations"]:
        st.markdown(f"- {badge('OBSERVED', 'observed')} {lim}", unsafe_allow_html=True)
        
    # Raw JSON expander
    with st.expander("View Raw Capsule JSON"):
        st.json(current_capsule)


# ==========================================
# TAB 3: BLAST RADIUS
# ==========================================
with tabs[2]:
    st.markdown("### Dependency Blast Radius & AST Import Graph")
    st.markdown(
        "Shows where the dependency touches repository code directly, and the downstream files that depend on it."
    )
    
    # Check for graph.json in assets
    graph_p = Path("assets/graph.json")
    if not graph_p.exists():
        # Build graph on the fly if needed
        from scripts.graph_builder import build_graph_data
        cov_f = Path(f"assets/evidence/capsule-{current_capsule['dependency']['name']}/baseline_coverage.json")
        graph_data = build_graph_data(Path("."), current_capsule["dependency"]["name"], cov_f if cov_f.exists() else None)
    else:
        graph_data = json.loads(graph_p.read_text(encoding="utf-8"))
        
    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown("#### Graph Metrics")
        st.markdown(f"- Total Project Files: **{graph_data.get('file_count', 0)}**")
        st.markdown(f"- Import Edges: **{graph_data.get('import_edge_count', 0)}**")
        st.markdown(f"- Direct Importers: **{len(graph_data.get('direct_usage_files', []))}**")
        st.markdown(f"- Blast Cone Size: **{len(graph_data.get('blast_cone_files', []))}**")
        
        st.markdown("##### Top Files by In-Degree")
        for tf in graph_data.get("top_files_by_importers", [])[:5]:
            st.markdown(f"- `{tf['label']}`: **{tf['in_degree']}** incoming imports")
            
        st.markdown("##### Direct Usage Files")
        for df in graph_data.get("direct_usage_files", []):
            st.markdown(f"- `{df}`")
            
    with col_right:
        st.markdown("#### Interactive Network View")
        render_graph_network(graph_data, current_capsule["dependency"]["name"])

    # Fallback list view
    with st.expander("Fallback List View (Plain Accessible View)"):
        st.markdown("**All Nodes:**")
        for n in graph_data.get("nodes", []):
            st.markdown(f"- `{n['id']}` ({n['type']}, test status: `{n['test_status']}`)")
        st.markdown("**All Edges:**")
        for e in graph_data.get("edges", []):
            st.markdown(f"- `{e['from']}` → `{e['to']}`")


# ==========================================
# TAB 4: TEST PROOF
# ==========================================
with tabs[3]:
    st.markdown("### Differential Test Proof")
    st.markdown("Evidence behind the verification status comparing baseline against candidate execution.")
    
    diff_file_path = Path(f"assets/diff_{current_capsule['dependency']['name']}.json")
    if diff_file_path.exists():
        diff_data = json.loads(diff_file_path.read_text(encoding="utf-8"))
    else:
        diff_data = {}
        
    base = current_capsule["observed"]["test_results"]["baseline"]
    cand = current_capsule["observed"]["test_results"]["candidate"]
    
    st.markdown(
        f"""
        <table class="custom-table">
          <thead>
            <tr>
              <th>Environment</th>
              <th>Passed</th>
              <th>Failed</th>
              <th>Duration</th>
              <th>pip check</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Baseline (Original)</strong></td>
              <td><span style="color:#4ADE80;">{base.get('passed', 0)}</span></td>
              <td><span style="color:#F87171;">{base.get('failed', 0)}</span></td>
              <td>{diff_data.get('baseline', {}).get('duration', 'N/A')}s</td>
              <td><code>{current_capsule['observed']['test_results']['pip_check']['baseline']}</code></td>
            </tr>
            <tr>
              <td><strong>Candidate (Replacement)</strong></td>
              <td><span style="color:#4ADE80;">{cand.get('passed', 0)}</span></td>
              <td><span style="color:#F87171;">{cand.get('failed', 0)}</span></td>
              <td>{diff_data.get('candidate', {}).get('duration', 'N/A')}s</td>
              <td><code>{current_capsule['observed']['test_results']['pip_check']['candidate']}</code></td>
            </tr>
          </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )
    
    # New Failures
    new_fails = current_capsule["observed"]["test_results"]["new_failures"]
    st.markdown("#### New Failures Attributed to Change")
    if new_fails:
        for nf in new_fails:
            st.error(f"❌ {nf}")
    else:
        st.success("✓ Zero new test failures introduced by candidate replacement.")
        
    # Per-test diff table
    per_test = diff_data.get("per_test_diff", [])
    if per_test:
        st.markdown("#### Per-Test Results Diff")
        pt_html = "<table class='custom-table'><thead><tr><th>Test Name</th><th>Baseline</th><th>Candidate</th><th>Changed</th></tr></thead><tbody>"
        for pt in per_test:
            ch_str = "<span style='color:#F87171;'>YES</span>" if pt["changed"] else "<span style='color:#9AA7B4;'>NO</span>"
            pt_html += f"<tr><td><code>{pt['test_name']}</code></td><td>{pt['baseline']}</td><td>{pt['candidate']}</td><td>{ch_str}</td></tr>"
        pt_html += "</tbody></table>"
        st.markdown(pt_html, unsafe_allow_html=True)


# ==========================================
# TAB 5: INTEGRITY
# ==========================================
with tabs[4]:
    st.markdown("### Cryptographic Integrity Manifest")
    st.markdown(
        "Confirms that capsules and evidence logs have not been altered or tampered with since generation. "
        "Guaranteed by SHA-256 cryptographic hashes."
    )
    
    if st.button("Verify Now (Run verify_capsule.py)"):
        code, out, err = subprocess.run(
            [sys.executable, "scripts/verify_capsule.py", "assets/manifest.json"],
            capture_output=True,
            text=True
        )
        if code == 0:
            st.success("Verification Succeeded: All hashes match.")
        else:
            st.error("Verification Failed: Hash mismatch or integrity breach detected!")
        st.code(out + "\n" + err)
        
    if manifest and "files" in manifest:
        st.markdown("#### Manifest Hashes (`assets/manifest.json`)")
        from scripts.common import compute_sha256_file
        
        m_rows = []
        for fp, exp_hash in manifest["files"].items():
            f_path = Path(fp)
            if f_path.exists():
                cur_hash = compute_sha256_file(f_path)
                match = (cur_hash == exp_hash)
            else:
                cur_hash = "FILE_MISSING"
                match = False
            m_rows.append({
                "file": fp,
                "expected": exp_hash,
                "current": cur_hash,
                "match": match
            })
            
        m_html = "<table class='custom-table'><thead><tr><th>Status</th><th>File</th><th>Expected SHA-256</th><th>Current SHA-256</th></tr></thead><tbody>"
        for mr in m_rows:
            st_str = "<span style='color:#4ADE80;'>✓ MATCH</span>" if mr["match"] else "<span style='color:#F87171;'>✕ MISMATCH</span>"
            m_html += f"<tr><td>{st_str}</td><td><code>{mr['file']}</code></td><td><code>{mr['expected'][:14]}...</code></td><td><code>{mr['current'][:14]}...</code></td></tr>"
        m_html += "</tbody></table>"
        st.markdown(m_html, unsafe_allow_html=True)
    else:
        st.info("No manifest file found at `assets/manifest.json`.")


# ==========================================
# TAB 6: ABOUT AND LIMITS
# ==========================================
with tabs[5]:
    st.markdown("### About and Honest Disclosures")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("#### Model & Architecture Information")
        st.markdown("- **Model Name**: Qwen 2.5 Coder 7B Instruct / Llama 3.1 8B")
        st.markdown("- **Access Method**: Local Ollama (port 11434) / Hosted API")
        st.markdown("- **License**: Apache 2.0 / Llama 3.1 Community License")
        st.markdown("- **Model Card**: [ollama.com/library/qwen2.5-coder](https://ollama.com/library/qwen2.5-coder)")
        
    with col_m2:
        st.markdown("#### Privacy Note")
        st.markdown("- **Local Mode (Default)**: Zero outbound network calls; AST and code snippets never leave your machine.")
        st.markdown("- **Hosted Mode**: Sends prompt and AST usage lines to the configured API provider endpoint.")
        
    st.markdown("<hr style='border-color:#283340;'>", unsafe_allow_html=True)
    st.markdown("#### Implementation Maturity")
    
    st.markdown(
        """
        <table class="custom-table">
          <thead>
            <tr>
              <th>Working (Production Tested)</th>
              <th>Partial</th>
              <th>Not Built / Future</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                • PyPI JSON risk scanning<br>
                • AST call-site & alias detection<br>
                • Dual environment diff test runner<br>
                • Validation gate & sys.stdlib verification<br>
                • SHA-256 tamper-evident manifest<br>
                • Streamlit evidence dashboard
              </td>
              <td>
                • Blast cone transitive traversal<br>
                • Rule-based migration mappings<br>
                • GitHub API token rate limiting
              </td>
              <td>
                • Non-Python languages<br>
                • Auto-git pull request generator<br>
                • Live code editor inside viewer
              </td>
            </tr>
          </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<hr style='border-color:#283340;'>", unsafe_allow_html=True)
    st.markdown("#### Known Limitations")
    st.markdown("1. **Test Suite Scope**: Results strictly cover what the target repo's tests execute. Unexercised call sites remain unverified.")
    st.markdown("2. **Python Only**: Language syntax parsing and execution harnesses are Python-specific.")
    st.markdown("3. **Small Model Quality**: Local open-weight models may suggest incorrect arguments; the validation gate and differential pytest runs decide acceptance, not the model.")
    st.markdown("4. **Viewer Integrity**: The viewer displays sealed saved capsules and manifests; it does not modify code or run unverified migrations.")
