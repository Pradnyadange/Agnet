import hmac
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
import streamlit as st

# Add scripts directory to sys.path so modules like scripts.graph_builder and common resolve uniformly
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

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

# -----------------------------------------------------------------------------
# Access Gate (DEC_ACCESS_CODE)
# -----------------------------------------------------------------------------
access_code_env = os.environ.get("DEC_ACCESS_CODE")
if access_code_env:
    if "dec_authenticated" not in st.session_state:
        st.session_state["dec_authenticated"] = False
    if "dec_attempts" not in st.session_state:
        st.session_state["dec_attempts"] = 0

    if not st.session_state["dec_authenticated"]:
        st.markdown("## 🔒 Access Gate")
        st.caption("This instance is protected by an access code. Please enter the access code to continue.")

        if st.session_state["dec_attempts"] >= 5:
            st.error("Too many failed attempts. Please restart the session.")
            st.stop()

        entered_code = st.text_input("Enter Access Code", type="password")
        if st.button("Unlock Viewer"):
            # Constant-time comparison, no logging of code, small delay
            time.sleep(0.3)
            if hmac.compare_digest(entered_code, access_code_env):
                st.session_state["dec_authenticated"] = True
                st.rerun()
            else:
                st.session_state["dec_attempts"] += 1
                remaining = 5 - st.session_state["dec_attempts"]
                st.error(f"Invalid access code. ({remaining} attempts remaining)")
                st.stop()
        st.stop()

from viewer.data import list_runs, load_capsules_from_run, load_manifest_from_run, load_evidence_file, parse_run_log, get_last_run_summary, count_capsule_statuses, load_run_json
from viewer.components import badge, render_stat_card
from viewer.graph import render_graph_network
from scripts.fetch_repo import validate_github_url

BASE_DIR = Path(__file__).resolve().parent
RUNS_DIR = BASE_DIR / "assets" / "runs"

# Discover all available runs
available_runs = list_runs(RUNS_DIR)

# Initialize session state
if "selected_run_dir" not in st.session_state:
    st.session_state["selected_run_dir"] = str(available_runs[0]["path"]) if available_runs else None
if "live_runs_set" not in st.session_state:
    st.session_state["live_runs_set"] = set()
if "selected_capsule_id" not in st.session_state:
    st.session_state["selected_capsule_id"] = None
if "scan_preview_deps" not in st.session_state:
    st.session_state["scan_preview_deps"] = None

# Pipeline background execution state
if "pipeline_run_id" not in st.session_state:
    st.session_state["pipeline_run_id"] = None
if "pipeline_proc" not in st.session_state:
    st.session_state["pipeline_proc"] = None
if "pipeline_pid" not in st.session_state:
    st.session_state["pipeline_pid"] = None
if "pipeline_log_path" not in st.session_state:
    st.session_state["pipeline_log_path"] = None
if "pipeline_status" not in st.session_state:
    st.session_state["pipeline_status"] = "idle"  # idle | running | complete | error
if "pipeline_error_msg" not in st.session_state:
    st.session_state["pipeline_error_msg"] = None
if "pipeline_exit_code" not in st.session_state:
    st.session_state["pipeline_exit_code"] = None
if "pipeline_stderr" not in st.session_state:
    st.session_state["pipeline_stderr"] = None
if "pipeline_run_dir" not in st.session_state:
    st.session_state["pipeline_run_dir"] = None

# Run selector dropdown in top bar
col_title, col_run_sel, col_mode = st.columns([3, 2, 1.5])
with col_title:
    st.markdown("<h2 style='margin-bottom:0;'>Dependency Exit Capsule Viewer</h2>", unsafe_allow_html=True)

with col_run_sel:
    run_options = [str(r["path"]) for r in available_runs]

    def _make_run_label(r: dict) -> str:
        """Build a human-readable selector label.
        Format: "<repo> | <mode> | N capsules | <UTC time> UTC"
        repo comes exclusively from run.json or capsule metadata — never from folder name.
        """
        repo_url = r.get("repo_url")  # None if not in run.json / capsule
        display_name = r.get("display_name")  # e.g. "LinkWatch, tested run"
        mode = r.get("mode")  # "tested" | "static" | None

        # Derive a short repo label without constructing any URL from the folder name
        if display_name:
            repo_label = display_name
        elif repo_url and repo_url.startswith("https://github.com/"):
            repo_label = repo_url.replace("https://github.com/", "")
        else:
            repo_label = None  # show no link / no repo label

        ts = r["timestamp"]
        ts_display = ts[:19].replace("T", " ") + " UTC" if ts != "N/A" else "saved"
        caps = r["capsules_count"]
        mode_str = mode or "static"

        parts = []
        if repo_label:
            parts.append(repo_label)
        parts.append(mode_str)
        parts.append(f"{caps} capsule{'s' if caps != 1 else ''}")
        parts.append(ts_display)
        return " | ".join(parts)

    run_labels = {str(r["path"]): _make_run_label(r) for r in available_runs}
    if run_options:
        curr_idx = run_options.index(st.session_state["selected_run_dir"]) if st.session_state["selected_run_dir"] in run_options else 0
        selected_run_path_str = st.selectbox(
            "Active Run Selection",
            options=run_options,
            format_func=lambda p: run_labels.get(p, Path(p).name),
            index=curr_idx,
            label_visibility="collapsed"
        )
        if selected_run_path_str != st.session_state["selected_run_dir"]:
            st.session_state["selected_run_dir"] = selected_run_path_str
            st.session_state["selected_capsule_id"] = None
            st.rerun()
    else:
        st.caption("No saved runs available")

# Current run details
current_run_path = Path(st.session_state["selected_run_dir"]) if st.session_state["selected_run_dir"] else None
capsules = load_capsules_from_run(current_run_path) if current_run_path else []
manifest = load_manifest_from_run(current_run_path) if current_run_path else None

# Header Run Mode Badge: LIVE RUN only for run started in this session
is_live_run = (current_run_path and str(current_run_path) in st.session_state["live_runs_set"])
run_ts = manifest.get("generated_at", "N/A") if manifest else (capsules[0].get("generated_at", "N/A") if capsules else "N/A")
run_badge_label = "LIVE RUN" if is_live_run else f"SAVED RUN, {run_ts[:19].replace('T', ' ')}"

with col_mode:
    st.markdown(
        f"<div style='text-align:right; margin-top:8px;'><span class='run-mode-badge'>{run_badge_label}</span></div>",
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: #212c3b; margin-top:5px; margin-bottom:15px;'>", unsafe_allow_html=True)

# Navigation tabs - ANALYZE tab is FIRST
tabs = st.tabs(["Analyze", "Overview", "Capsule", "Blast radius", "Test proof", "Integrity", "About"])

# ==========================================
# TAB 0: ANALYZE (NEW)
# ==========================================
with tabs[0]:
    st.markdown("### Run Repository Analysis")
    st.info("ℹ️ **Notice**: Public repositories only. Python projects only. Tests are not run in this mode (static analysis only).")

    col_input1, col_input2 = st.columns([3, 2])
    with col_input1:
        repo_url_input = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/owner/repository",
            help="Strict regex enforced: Must be https://github.com/owner/repo without user credentials."
        )
        url_valid, url_owner, url_repo = validate_github_url(repo_url_input)
        if repo_url_input and not url_valid:
            st.error("Invalid GitHub URL. Must match `https://github.com/owner/repo` with no credentials or dots-only names.")

    with col_input2:
        zip_upload = st.file_uploader(
            "Or Upload Repository ZIP Archive",
            type=["zip"],
            help="Max upload size 100MB. Symlinks and Zip-Slip paths are rejected during extraction."
        )

    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        top_n = st.slider("Top N stale dependencies to analyze", min_value=1, max_value=10, value=3)

    with col_cfg2:
        # Discover local Ollama models dynamically via `ollama list`
        ollama_models = []
        try:
            res = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                lines = res.stdout.strip().splitlines()
                if len(lines) > 1:
                    for line in lines[1:]:
                        parts = line.split()
                        if parts:
                            ollama_models.append(parts[0])
        except Exception:
            pass

        if not ollama_models:
            ollama_models = ["llama3.1:8b", "llama3.2:3b", "gemma2:2b"]

        # Explicit choice, no default (placeholder)
        model_choice = st.selectbox(
            "Ollama Model (Explicit Choice Required)",
            options=["-- Select an installed Ollama model --"] + ollama_models,
            index=0
        )

    # Dependency Discovery / Scan step
    st.markdown("#### Dependencies Selection")
    col_scan_btn, col_scan_status = st.columns([1.5, 3])
    with col_scan_btn:
        if st.button("Scan Dependencies First"):
            if not repo_url_input and not zip_upload:
                st.error("Please enter a GitHub URL or upload a ZIP archive first.")
            elif repo_url_input and not url_valid:
                st.error("Please provide a valid GitHub repository URL.")
            else:
                with st.spinner("Scanning manifest files..."):
                    # Save zip if uploaded
                    temp_zip_path = None
                    if zip_upload:
                        temp_zip_path = BASE_DIR / "assets" / f"temp_upload_{int(time.time())}.zip"
                        temp_zip_path.write_bytes(zip_upload.getvalue())

                    # Call parse_dependencies via subprocess
                    fetch_cmd = [
                        sys.executable,
                        str(BASE_DIR / "scripts" / "run_pipeline.py"),
                        "--top-n", str(top_n),
                        "--offline"
                    ]
                    if repo_url_input:
                        fetch_cmd.extend(["--repo-url", repo_url_input])
                    elif temp_zip_path:
                        fetch_cmd.extend(["--zip-file", str(temp_zip_path)])

                    # Pre-scan using parse_repository_dependencies directly
                    import tempfile
                    from scripts.fetch_repo import clone_github_repo, extract_zip_repo
                    from scripts.parse_dependencies import parse_repository_dependencies
                    
                    try:
                        with tempfile.TemporaryDirectory() as td:
                            tpath = Path(td)
                            if repo_url_input:
                                repo_info = clone_github_repo(repo_url_input, tpath)
                            else:
                                repo_info = extract_zip_repo(temp_zip_path, tpath)
                            deps_dict, manifests = parse_repository_dependencies(Path(repo_info["target_dir"]))
                            st.session_state["scan_preview_deps"] = list(deps_dict.keys())
                            st.success(f"Discovered {len(deps_dict)} dependencies across manifests: {', '.join(manifests)}")
                    except Exception as e:
                        st.error(f"Scan failed: {e}")
                    finally:
                        if temp_zip_path and temp_zip_path.exists():
                            try:
                                temp_zip_path.unlink()
                            except Exception:
                                pass

    selected_ticked_deps = []
    if st.session_state["scan_preview_deps"]:
        selected_ticked_deps = st.multiselect(
            "Select specific dependencies to guarantee inclusion:",
            options=st.session_state["scan_preview_deps"],
            default=st.session_state["scan_preview_deps"][:top_n]
        )
    else:
        st.caption("Click 'Scan Dependencies First' to preview and selectively tick dependencies.")

    # Execution controls
    st.markdown("<br>", unsafe_allow_html=True)
    col_run_btn, col_tier2_chk = st.columns([2, 3])
    with col_tier2_chk:
        st.checkbox("Run isolated test suites (Tier 2)", value=False, disabled=True, help="Disabled: Tier 2 differential test execution is not built for arbitrary external repos.")
        st.caption("⚠️ Test execution stays disabled for external repositories (static analysis mode only).")

    with col_run_btn:
        run_analysis_clicked = st.button("🚀 Run Analysis", type="primary")

    if run_analysis_clicked:
        if not repo_url_input and not zip_upload:
            st.error("Please enter a GitHub repository URL or upload a ZIP archive.")
        elif repo_url_input and not url_valid:
            st.error("Invalid GitHub URL. Please correct the repository address.")
        elif model_choice == "-- Select an installed Ollama model --":
            st.error("Please select an explicit Ollama model from the dropdown.")
        elif st.session_state["pipeline_status"] == "running":
            st.warning("A pipeline run is already in progress. Please wait for it to complete.")
        else:
            temp_zip_path = None
            if zip_upload:
                temp_zip_path = BASE_DIR / "assets" / f"upload_{int(time.time())}.zip"
                temp_zip_path.write_bytes(zip_upload.getvalue())

            # Prepare run id
            if repo_url_input:
                safe_slug = re.sub(r"[^a-zA-Z0-9_\-]", "_", f"{url_owner}__{url_repo}")
            else:
                safe_slug = f"upload_{int(time.time())}"
            run_id = f"{safe_slug}__{int(time.time())}"

            # Prepare log file path
            log_dir = RUNS_DIR / run_id
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "run.log"
            stderr_file = log_dir / "stderr.log"

            cmd = [
                sys.executable,
                "-u",
                str(BASE_DIR / "scripts" / "run_pipeline.py"),
                "--model-id", model_choice,
                "--top-n", str(top_n),
                "--provider", "ollama",
                "--log-file", str(log_file.resolve()),
                "--out-base", str(RUNS_DIR.resolve())
            ]
            if repo_url_input:
                cmd.extend(["--repo-url", repo_url_input])
            elif temp_zip_path:
                cmd.extend(["--zip-file", str(temp_zip_path.resolve())])

            if selected_ticked_deps:
                cmd.extend(["--selected-deps", ",".join(selected_ticked_deps)])

            # Launch process non-blocking with shell=False
            stderr_fp = open(stderr_file, "w", encoding="utf-8")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=stderr_fp,
                text=True,
                shell=False
            )

            st.session_state["pipeline_run_id"] = run_id
            st.session_state["pipeline_proc"] = proc
            st.session_state["pipeline_pid"] = proc.pid
            st.session_state["pipeline_log_path"] = str(log_file.resolve())
            st.session_state["pipeline_status"] = "running"
            st.session_state["pipeline_error_msg"] = None
            st.session_state["pipeline_exit_code"] = None
            st.session_state["pipeline_stderr"] = None
            st.session_state["pipeline_run_dir"] = None

    # -------------------------------------------------------------------------
    # Render Progress and Result OUTSIDE the button block
    # -------------------------------------------------------------------------
    st.markdown("<hr style='border-color: #212c3b; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("### Execution Progress & Status")

    pipeline_status = st.session_state.get("pipeline_status", "idle")
    proc = st.session_state.get("pipeline_proc")
    log_file_str = st.session_state.get("pipeline_log_path")
    log_file_p = Path(log_file_str) if log_file_str else None

    # Check process completion if currently running
    if pipeline_status == "running" and proc:
        ret = proc.poll()
        if ret is not None:
            # Process ended
            st.session_state["pipeline_exit_code"] = ret
            # Read stderr if any
            stderr_path = log_file_p.parent / "stderr.log" if log_file_p else None
            last_30_stderr = []
            if stderr_path and stderr_path.exists():
                try:
                    err_lines = stderr_path.read_text(encoding="utf-8", errors="replace").splitlines()
                    last_30_stderr = err_lines[-30:]
                except Exception:
                    pass
            st.session_state["pipeline_stderr"] = "\n".join(last_30_stderr)

            # Check log to see final status
            log_data = parse_run_log(log_file_p) if log_file_p else {}
            final_dir = log_data.get("final_run_dir") or (str(log_file_p.parent) if log_file_p else None)

            if ret == 0:
                st.session_state["pipeline_status"] = "complete"
                st.session_state["pipeline_run_dir"] = final_dir
                if final_dir:
                    st.session_state["selected_run_dir"] = str(final_dir)
                    st.session_state["live_runs_set"].add(str(final_dir))
            else:
                st.session_state["pipeline_status"] = "error"
                st.session_state["pipeline_error_msg"] = log_data.get("error_message") or f"Process exited with code {ret}"
                st.session_state["pipeline_run_dir"] = final_dir

    # Display status UI based on session state
    curr_status = st.session_state.get("pipeline_status", "idle")
    if curr_status == "running":
        st.info(f"⏳ **Pipeline is running** (PID: `{st.session_state.get('pipeline_pid')}`, Run ID: `{st.session_state.get('pipeline_run_id')}`).")
        if log_file_p and log_file_p.exists():
            log_data = parse_run_log(log_file_p)
            events = log_data.get("events", [])
            with st.status(f"Running pipeline... ({len(events)} events recorded)", expanded=True):
                for ev in events:
                    step_name = ev.get("step", "info").upper()
                    st_msg = ev.get("message", "")
                    st.write(f"**[{step_name}]** {st_msg}")
        col_poll, _ = st.columns([1.5, 4])
        with col_poll:
            if st.button("🔄 Refresh Progress"):
                st.rerun()

    elif curr_status == "complete":
        final_dir_str = st.session_state.get("pipeline_run_dir")
        st.success(f"✅ **Analysis Complete!** Run directory: `{final_dir_str}`")

        # Load completed capsules to calculate statuses summary
        res_caps = load_capsules_from_run(Path(final_dir_str)) if final_dir_str else []
        all_six_statuses = ["verified", "unverified", "failed", "not_testable", "not_run", "no_valid_proposal"]
        status_counts = {s: 0 for s in all_six_statuses}
        for c in res_caps:
            c_stat = c.get("status", "unverified")
            if c_stat in status_counts:
                status_counts[c_stat] += 1
            else:
                status_counts[c_stat] = 1

        # Summary box
        st.markdown(f"**Total Capsules Generated**: `{len(res_caps)}`")
        stat_cols = st.columns(6)
        for i, s_name in enumerate(all_six_statuses):
            with stat_cols[i]:
                st.metric(s_name.replace("_", " ").title(), status_counts[s_name])

        # Button to open results (sets active run and reruns)
        col_open, col_clear = st.columns([1.5, 3])
        with col_open:
            if st.button("📂 Open Results in Overview"):
                if final_dir_str:
                    st.session_state["selected_run_dir"] = final_dir_str
                    st.session_state["selected_capsule_id"] = None
                st.rerun()

    elif curr_status == "error":
        st.error(f"❌ **Pipeline Execution Failed** (Exit Code: `{st.session_state.get('pipeline_exit_code')}`)")
        if st.session_state.get("pipeline_error_msg"):
            st.error(f"Error: {st.session_state.get('pipeline_error_msg')}")
        if st.session_state.get("pipeline_stderr"):
            st.markdown("#### Stderr (Last 30 lines):")
            st.code(st.session_state["pipeline_stderr"])
        if log_file_p and log_file_p.exists():
            log_data = parse_run_log(log_file_p)
            events = log_data.get("events", [])
            with st.expander(f"View Run Log ({len(events)} events)"):
                for ev in events:
                    st.write(f"**[{ev.get('step', '').upper()}]** {ev.get('message', '')}")

    else:
        st.caption("No analysis currently active in this session. Configure a target repository above and click 'Run Analysis'.")

    # -------------------------------------------------------------------------
    # Last Run Panel (Survives Reloads)
    # -------------------------------------------------------------------------
    st.markdown("<hr style='border-color: #212c3b; margin: 25px 0 15px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 🕒 Last Run Summary (Persisted)")
    last_summary = get_last_run_summary(RUNS_DIR)
    if last_summary:
        l_stat = last_summary["status"]
        stat_badge_color = "#34d399" if l_stat == "complete" else ("#f87171" if l_stat == "failed" else "#fbbf24")
        st.markdown(
            f"<div style='background-color:#161f2e; border:1px solid #212c3b; border-radius:8px; padding:12px 16px; margin-bottom:12px;'>"
            f"<strong>Run ID:</strong> <code>{last_summary['run_id']}</code> &nbsp;|&nbsp; "
            f"<strong>Status:</strong> <span style='color:{stat_badge_color}; font-weight:600;'>{l_stat.upper()}</span> &nbsp;|&nbsp; "
            f"<strong>Capsules:</strong> <code>{last_summary['capsules_count']}</code> &nbsp;|&nbsp; "
            f"<strong>Timestamp:</strong> <code>{last_summary['timestamp']}</code><br>"
            f"<small style='color:#94a3b8;'>Directory: {last_summary['path'].resolve()}</small>"
            f"</div>",
            unsafe_allow_html=True
        )
        col_open_last, _ = st.columns([2, 4])
        with col_open_last:
            if st.button("Load Last Run in Viewer", key="btn_load_last_run"):
                st.session_state["selected_run_dir"] = str(last_summary["path"])
                st.session_state["selected_capsule_id"] = None
                st.rerun()
    else:
        st.caption("No past runs recorded in assets/runs/.")


# ==========================================
# EMPTY STATE CHECK
# ==========================================
if not current_run_path or not capsules:
    with tabs[1]:
        st.warning("No runs yet: paste a GitHub URL in the Analyze tab.")
    with tabs[2]:
        st.warning("No runs yet: paste a GitHub URL in the Analyze tab.")
    with tabs[3]:
        st.warning("No runs yet: paste a GitHub URL in the Analyze tab.")
    with tabs[4]:
        st.warning("No runs yet: paste a GitHub URL in the Analyze tab.")
    with tabs[5]:
        st.warning("No runs yet: paste a GitHub URL in the Analyze tab.")
    st.stop()


# Default selected capsule
if st.session_state["selected_capsule_id"] is None and capsules:
    st.session_state["selected_capsule_id"] = capsules[0]["capsule_id"]

current_capsule = next((c for c in capsules if c["capsule_id"] == st.session_state["selected_capsule_id"]), capsules[0])


# ==========================================
# TAB 1: OVERVIEW
# ==========================================
with tabs[1]:
    total_capsules = len(capsules)
    status_counts = count_capsule_statuses(capsules)
    scanned_count = max([c["observed"]["scan"]["files_scanned"] for c in capsules] or [0])

    # Top summary metrics
    c_meta1, c_meta2 = st.columns(2)
    with c_meta1:
        render_stat_card("Files Scanned", scanned_count)
    with c_meta2:
        render_stat_card("Capsules Built", total_capsules)

    st.markdown("<h4 style='margin-top:15px; margin-bottom:10px;'>Capsule Statuses (Sum: " + str(sum(status_counts.values())) + ")</h4>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_stat_card("Verified", status_counts["verified"])
    with c2:
        render_stat_card("Unverified", status_counts["unverified"])
    with c3:
        render_stat_card("Failed", status_counts["failed"])
    with c4:
        render_stat_card("Not Testable", status_counts["not_testable"])
    with c5:
        render_stat_card("Not Run", status_counts["not_run"])
    with c6:
        render_stat_card("No Proposal", status_counts["no_valid_proposal"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Scanned Dependencies")

    table_rows = []
    for c in capsules:
        dep_name = c["dependency"]["name"]
        decl_spec = c["dependency"]["declared_specifier"] or "any"
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

    rows_html = "".join([
        f"<tr><td><strong>{r['name']}</strong></td><td><code>{r['version']}</code></td><td>{r['days_since']}</td><td>{r['usages']} sites</td><td><code>{r['proposal']}</code></td><td>{r['provenance']}</td><td>{r['status_html']}</td></tr>"
        for r in table_rows
    ])
    table_html = (
        '<table class="custom-table">'
        '<thead><tr><th>Dependency</th><th>Declared Version</th><th>Staleness</th><th>AST Usages</th><th>Proposed Change</th><th>Provenance</th><th>Status</th></tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


# ==========================================
# TAB 2: CAPSULE
# ==========================================
with tabs[2]:
    dep_meta = current_capsule["dependency"]
    target_repo = current_capsule["target_repo"]
    status_val = current_capsule["status"]

    # Build repo link only from target_repo.url — never from folder/run_id
    _tr_url = target_repo.get("url", "")
    _sha_short = target_repo["commit_sha"][:8] if len(target_repo["commit_sha"]) >= 8 else target_repo["commit_sha"]
    if _tr_url.startswith("https://github.com/"):
        _repo_display = f"<a href='{_tr_url}' target='_blank' style='color:#58a6ff;'>{target_repo['name']}</a>"
    else:
        _repo_display = f"<code>{target_repo['name']}</code>"

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
            Repository: {_repo_display} (SHA: <code>{_sha_short}</code>) | Saved: {current_capsule['generated_at']} UTC
          </div>
          <div style="margin-top:6px; font-size:0.9rem; color:#E6EDF3;">
            <em>{current_capsule['maintenance_problem']}</em>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    usage_count = len(current_capsule["observed"]["usage_locations"])
    prov_prov = current_capsule["ai_generated"]["provenance"]["provider"]
    if usage_count == 0:
        st.warning("⚠️ Warning: This capsule contains a proposal but has 0 identified usage locations in the repository.")
    if "rule_based" in prov_prov:
        st.info("ℹ️ Note: This proposal was generated by the deterministic rule-based fallback knowledge base, not an AI model.")

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

        trust_data = current_capsule["observed"].get("trust_check") or current_capsule["ai_generated"]["provenance"].get("trust_check")
        if trust_data:
            st.markdown("**Replacement Trust Check (PyPI Observed)**")
            if trust_data.get("skipped"):
                st.info("ℹ️ Stdlib candidate: PyPI trust check skipped.")
            else:
                rev_flag = trust_data.get("needs_human_review", False)
                flag_color = "#F87171" if rev_flag else "#4ADE80"
                flag_text = "⚠️ NEEDS HUMAN REVIEW" if rev_flag else "✓ CLEAN TRUST CHECK"
                st.markdown(f"<span style='color:{flag_color}; font-weight:700;'>{flag_text}</span>", unsafe_allow_html=True)

                t_cols = st.columns(2)
                with t_cols[0]:
                    st.caption(f"First Release: `{trust_data.get('first_release_date') or 'N/A'}`")
                    st.caption(f"Last Release: `{trust_data.get('last_release_date') or 'N/A'}`")
                    st.caption(f"Total Releases: `{trust_data.get('release_count', 0)}`")
                with t_cols[1]:
                    src_status = "✓ Found" if trust_data.get("has_source_repo_url") else "✕ Missing"
                    st.caption(f"Source Repo URL: `{src_status}`")
                    st.caption(f"Edit Distance to Popular: `{trust_data.get('min_edit_distance_to_popular')} ({trust_data.get('closest_popular_package')})`")

                if trust_data.get("reasons"):
                    st.markdown("*Review Reasons:*")
                    for r in trust_data["reasons"]:
                        st.markdown(f"- ⚠️ {r}")
            st.markdown("<hr style='border-color:#2d3b4d; margin:8px 0;'>", unsafe_allow_html=True)

        redact_count = current_capsule["observed"].get("secret_redactions_count")
        if redact_count is None:
            redact_count = current_capsule["ai_generated"]["provenance"].get("secret_redactions_count", 0)
        st.markdown(f"**Secret Redactions in Prompts**: `{redact_count}` secrets redacted")

        st.markdown("**Risk Indicators**")
        for r in current_capsule["observed"]["risk_indicators"]:
            st.markdown(f"- **{r['id']}**: `{r['value']}` (Fetched: {r['fetched_at'][:19]})")
            st.caption(f"Source: {r['source_url']}")

        st.markdown(f"**AST Usage Sites ({len(current_capsule['observed']['usage_locations'])})**")
        if current_capsule["observed"]["usage_locations"]:
            u_rows = "".join([
                f"<tr><td><code>{u['file']}:{u['line']}</code></td><td><code>{u['symbol']}</code></td><td>{'<span style=\"color:#4ADE80;\">✓ YES</span>' if u['covered_by_tests'] else '<span style=\"color:#FBBF24;\">○ NO</span>'}</td></tr>"
                for u in current_capsule["observed"]["usage_locations"]
            ])
            u_html = f"<table class='custom-table'><thead><tr><th>File:Line</th><th>Symbol</th><th>Covered</th></tr></thead><tbody>{u_rows}</tbody></table>"
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
        st.markdown(f"- Model Card: [{prov['model_card_url']}]({prov['model_card_url']})")
        st.markdown(f"- Prompt SHA-256: `{'N/A' if prov['prompt_sha256'] == 'N/A' else prov['prompt_sha256'][:16] + '...'}`")
        if prov.get("applied_model_run"):
            st.markdown(f"- Selection: `{prov['applied_model_run']}`")

        val = prov["validation"]
        val_badge = "<span style='color:#4ADE80; font-weight:700;'>PASSED</span>" if val["passed"] else "<span style='color:#F87171; font-weight:700;'>REJECTED</span>"
        st.markdown(f"- Gate Status: {val_badge}")
        cov_val = val['api_coverage']
        cov_text = f"{int(cov_val * 100)}%" if (cov_val is not None) else "N/A"
        st.markdown(f"- API Symbol Coverage: `{cov_text}`")
        if val["rejected_candidates"]:
            st.markdown(f"- Rejected Candidates: `{', '.join(val['rejected_candidates'])}`")

        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 3: BLAST RADIUS
# ==========================================
with tabs[3]:
    st.markdown("### Blast Radius: Code Usage & Dependency Graph")
    st.markdown(
        "Interactive dependency blast radius showing direct AST usage call sites and affected modules."
    )

    # Build graph data directly from capsule usage locations or precomputed graph.json
    dep_name_active = current_capsule["dependency"]["name"]
    graph_json_p = current_run_path / "graph.json" if current_run_path else None
    if not graph_json_p or not graph_json_p.exists():
        graph_json_p = BASE_DIR / "assets" / "graph.json"

    graph_data = None
    if graph_json_p.exists():
        try:
            graph_data = json.loads(graph_json_p.read_text(encoding="utf-8"))
        except Exception:
            pass

    if not graph_data or not graph_data.get("nodes"):
        # Construct graph data directly from capsule usage locations
        usage_locs = current_capsule["observed"].get("usage_locations", [])
        nodes_dict = {}
        edges_list = []
        direct_files = set()

        # Add target dependency node
        nodes_dict[dep_name_active] = {
            "id": dep_name_active,
            "label": dep_name_active,
            "type": "package",
            "in_degree": 0,
            "test_status": "covered_and_passing" if current_capsule["status"] == "verified" else "not_covered"
        }

        for u in usage_locs:
            f = u.get("file", "unknown")
            direct_files.add(f)
            if f not in nodes_dict:
                nodes_dict[f] = {
                    "id": f,
                    "label": f,
                    "type": "file",
                    "in_degree": 0,
                    "test_status": "covered_and_passing" if u.get("covered_by_tests") else "not_covered"
                }
            edges_list.append({"from": f, "to": dep_name_active})
            nodes_dict[dep_name_active]["in_degree"] += 1

        graph_data = {
            "file_count": len([n for n in nodes_dict.values() if n["type"] == "file"]),
            "import_edge_count": len(edges_list),
            "target_dependency": dep_name_active,
            "direct_usage_files": list(direct_files),
            "blast_cone_files": list(direct_files),
            "nodes": list(nodes_dict.values()),
            "edges": edges_list
        }

    with st.container():
        st.markdown("#### Interactive Network View")
        render_graph_network(graph_data, dep_name_active)

    with st.expander("Fallback List View (Plain Accessible View)"):
        st.markdown("**All Nodes:**")
        for n in graph_data.get("nodes", []):
            st.markdown(f"- `{n['id']}` ({n.get('type', 'file')}, test status: `{n.get('test_status', 'not_covered')}`)")
        st.markdown("**All Edges:**")
        for e in graph_data.get("edges", []):
            st.markdown(f"- `{e['from']}` → `{e['to']}`")


# ==========================================
# TAB 4: TEST PROOF
# ==========================================
with tabs[4]:
    st.markdown("### Differential Test Proof")
    st.markdown("Evidence behind the verification status comparing baseline against candidate execution.")

    diff_file_path = current_run_path / f"diff_{current_capsule['dependency']['name']}.json"
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

    new_fails = current_capsule["observed"]["test_results"]["new_failures"]
    st.markdown("#### New Failures Attributed to Change")
    if new_fails:
        for nf in new_fails:
            st.error(f"❌ {nf}")
    else:
        st.success("✓ Zero new test failures introduced by candidate replacement.")

    per_test = diff_data.get("per_test_diff", [])
    if per_test:
        st.markdown("#### Per-Test Results Diff")
        pt_html = "<table class='custom-table'><thead><tr><th>Test Name</th><th>Baseline</th><th>Candidate</th><th>Changed</th></tr></thead><tbody>"
        for pt in per_test:
            ch_str = "<span style='color:#F87171;'>YES</span>" if pt["changed"] else "<span style='color:#9AA7B4;'>NO</span>"
            pt_html += f"<tr><td><code>{pt['test_name']}</code></td><td>{pt['baseline']}</td><td>{pt['candidate']}</td><td>{ch_str}</td></tr>"
        pt_html += "</tbody></table>"
        st.markdown(pt_html, unsafe_allow_html=True)

    # Render "Rejected by tests" table for capsules with failing candidates
    cand_results = current_capsule["observed"].get("test_results", {}).get("candidate_results", [])
    failing_cands = [cr for cr in cand_results if cr.get("verdict") == "rejected_by_tests" or cr.get("failed", 0) > 0]
    
    # Also check if the primary candidate itself failed
    if not failing_cands and cand.get("failed", 0) > 0:
        failing_cands = [{
            "candidate_name": current_capsule["ai_generated"]["proposed_replacement"]["name"],
            "passed": cand.get("passed", 0),
            "failed": cand.get("failed", 0),
            "verdict": "rejected_by_tests",
            "rejection_reason": "New test failures introduced by candidate replacement",
            "failing_tests": new_fails,
            "junit_path": cand.get("junit_path", "n/a")
        }]

    if failing_cands:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ❌ Rejected by Tests")
        st.markdown("Candidates that failed execution in differential test suites:")
        rej_html = (
            "<table class='custom-table'><thead><tr>"
            "<th>Candidate / Option</th><th>Passed</th><th>Failed</th><th>Failing Tests</th><th>Failure Reason / Trace</th><th>JUnit XML</th>"
            "</tr></thead><tbody>"
        )
        for fc in failing_cands:
            f_tests = "<br>".join([f"<code>{ft}</code>" for ft in fc.get("failing_tests", [])]) or "<em>None listed</em>"
            reason = fc.get("rejection_reason") or "Test suite failure"
            jpath = fc.get("junit_path") or "n/a"
            rej_html += (
                f"<tr>"
                f"<td><strong>{fc.get('candidate_name')}</strong></td>"
                f"<td><span style='color:#4ADE80;'>{fc.get('passed', 0)}</span></td>"
                f"<td><span style='color:#F87171; font-weight:700;'>{fc.get('failed', 0)}</span></td>"
                f"<td>{f_tests}</td>"
                f"<td><code style='color:#FCA5A5;'>{reason}</code></td>"
                f"<td><code>{jpath}</code></td>"
                f"</tr>"
            )
        rej_html += "</tbody></table>"
        st.markdown(rej_html, unsafe_allow_html=True)


# ==========================================
# TAB 5: INTEGRITY
# ==========================================
with tabs[5]:
    st.markdown("### Cryptographic Integrity Manifest")
    st.markdown(
        "Confirms that capsules and evidence logs have not been altered or tampered with since generation. "
        "Guaranteed by SHA-256 cryptographic hashes."
    )

    manifest_file = current_run_path / "manifest.json" if current_run_path else None
    if st.button("Verify Now (Run verify_capsule.py)"):
        if manifest_file and manifest_file.exists():
            verify_script = BASE_DIR / "scripts" / "verify_capsule.py"
            verify_res = subprocess.run(
                [sys.executable, str(verify_script), str(manifest_file)],
                capture_output=True,
                text=True
            )
            if verify_res.returncode == 0:
                st.success("Verification Succeeded: All hashes match.")
            else:
                st.error("Verification Failed: Hash mismatch or integrity breach detected!")
            st.code((verify_res.stdout or "") + "\n" + (verify_res.stderr or ""))
        else:
            st.warning("No manifest file found in active run directory.")

    if manifest and "files" in manifest:
        st.markdown(f"#### Manifest Hashes (`{manifest_file.as_posix() if manifest_file else 'manifest.json'}`)")
        from scripts.common import compute_sha256_file

        m_rows = []
        for fp, exp_hash in manifest["files"].items():
            f_path = Path(fp)
            if not f_path.is_absolute():
                f_path = BASE_DIR / f_path
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
        st.info("No manifest file found for this run.")


# ==========================================
# TAB 6: ABOUT AND LIMITS
# ==========================================
with tabs[6]:
    st.markdown("### About and Honest Disclosures")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("#### Model & Architecture Information")
        st.markdown("- **Model Name**: Qwen 2.5 Coder 7B Instruct / Llama 3.1 8B")
        st.markdown("- **Access Method**: Local Ollama (port 11434) / Hosted API")
        st.markdown("- **License**: Apache 2.0 / Llama 3.1 Community License")
        st.markdown("- **Model Card**: [ollama.com/library/llama3.1](https://ollama.com/library/llama3.1)")

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
                • Automated Analyze pipeline (fetch, parse, rank)<br>
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
    st.markdown("1. **Test Suite Scope**: Results strictly cover what the target repo's tests execute. In static Analyze mode, test suites are not executed.")
    st.markdown("2. **Python Only**: Language syntax parsing and execution harnesses are Python-specific.")
    st.markdown("3. **Small Model Quality**: Local open-weight models may suggest incorrect arguments; the validation gate and differential pytest runs decide acceptance, not the model.")
    st.markdown("4. **Viewer Integrity**: The viewer displays sealed saved capsules and manifests; it does not modify code or run unverified migrations.")
