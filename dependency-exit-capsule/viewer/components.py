import streamlit as st

def badge(text: str, badge_type: str = "observed") -> str:
    """Return HTML for a status or category badge."""
    css_class = f"badge-{badge_type.lower().replace('_', '-')}"
    icon = ""
    if badge_type.lower() == "verified":
        icon = "✓ "
    elif badge_type.lower() == "unverified":
        icon = "⚠ "
    elif badge_type.lower() == "not_testable":
        icon = "○ "
    elif badge_type.lower() == "failed":
        icon = "✕ "
    elif badge_type.lower() == "observed":
        icon = "👁 "
    elif badge_type.lower() == "ai":
        icon = "✦ "
    elif badge_type.lower() == "rule_based":
        icon = "⚙ "
        
    return f'<span class="badge-base {css_class}">{icon}{text.upper()}</span>'

def render_badge(text: str, badge_type: str = "observed"):
    st.markdown(badge(text, badge_type), unsafe_allow_html=True)

def render_stat_card(label: str, value: str | int, subtext: str = ""):
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-num">{value}</div>
            <div class="stat-label">{label}</div>
            {f'<div style="font-size:0.75rem; color:#9AA7B4; margin-top:4px;">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True
    )
