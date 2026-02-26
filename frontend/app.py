import streamlit as st
import requests

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ContractBot — AI Contract Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #0f0f1a 100%);
        color: #e2e8f0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12122a 0%, #1e1e3a 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }

    /* Cards */
    .card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
    }

    .card-title {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #818cf8;
        margin-bottom: 10px;
    }

    .card-content {
        font-size: 15px;
        color: #cbd5e1;
        line-height: 1.7;
    }

    /* Risk badges */
    .badge-high {
        display: inline-block;
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.35);
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-medium {
        display: inline-block;
        background: rgba(234,179,8,0.15);
        color: #fbbf24;
        border: 1px solid rgba(234,179,8,0.35);
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-low {
        display: inline-block;
        background: rgba(34,197,94,0.15);
        color: #4ade80;
        border: 1px solid rgba(34,197,94,0.35);
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Risk card */
    .risk-card {
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid;
    }
    .risk-high  { background: rgba(239,68,68,0.08);  border-color: #ef4444; }
    .risk-medium{ background: rgba(234,179,8,0.08);  border-color: #eab308; }
    .risk-low   { background: rgba(34,197,94,0.08);  border-color: #22c55e; }

    /* Warning clause card */
    .clause-card {
        background: rgba(251,191,36,0.07);
        border: 1px solid rgba(251,191,36,0.25);
        border-left: 4px solid #fbbf24;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }

    /* Summary box */
    .summary-box {
        background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.08));
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 14px;
        padding: 24px;
        font-size: 15px;
        line-height: 1.8;
        color: #e2e8f0;
        margin-bottom: 20px;
    }

    /* Info row */
    .info-row {
        display: flex;
        gap: 12px;
        margin-bottom: 8px;
        align-items: flex-start;
    }
    .info-label {
        font-weight: 600;
        color: #94a3b8;
        min-width: 180px;
        font-size: 13px;
        padding-top: 1px;
    }
    .info-value {
        color: #e2e8f0;
        font-size: 14px;
    }

    /* Divider */
    hr { border-color: rgba(99,102,241,0.15) !important; }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 32px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important;
    }

    /* Tabs */
    [data-testid="stTabs"] button {
        color: #94a3b8 !important;
        font-weight: 500;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #818cf8 !important;
        border-bottom-color: #6366f1 !important;
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: 10px 0 30px;
    }
    .main-header h1 {
        font-size: 2.6em;
        font-weight: 700;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 6px;
    }
    .main-header p {
        color: #64748b;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

BACKEND_URL = "http://localhost:8000"


# ── Helpers ───────────────────────────────────────────────────────────────────

def risk_badge(level: str) -> str:
    level = level.strip().lower()
    if level == "high":
        return '<span class="badge-high">🔴 High</span>'
    elif level == "medium":
        return '<span class="badge-medium">🟡 Medium</span>'
    else:
        return '<span class="badge-low">🟢 Low</span>'


def risk_class(level: str) -> str:
    level = level.strip().lower()
    if level == "high":   return "risk-high"
    if level == "medium": return "risk-medium"
    return "risk-low"


def info_row(label: str, value: str) -> str:
    if not value or value.lower() in ("", "not specified", "not found", "n/a"):
        value = '<span style="color:#475569;font-style:italic;">Not specified</span>'
    return f'''<div class="info-row">
        <span class="info-label">{label}</span>
        <span class="info-value">{value}</span>
    </div>'''


def card(title: str, content: str) -> str:
    return f'''<div class="card">
        <div class="card-title">{title}</div>
        <div class="card-content">{content}</div>
    </div>'''


def call_analyze_text(contract_text: str) -> dict:
    response = requests.post(
        f"{BACKEND_URL}/analyze/text",
        json={"contract_text": contract_text},
        timeout=120
    )
    response.raise_for_status()
    return response.json()


def call_analyze_pdf(pdf_bytes: bytes, filename: str) -> dict:
    response = requests.post(
        f"{BACKEND_URL}/analyze/pdf",
        files={"file": (filename, pdf_bytes, "application/pdf")},
        timeout=120
    )
    response.raise_for_status()
    return response.json()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px;">
        <div style="font-size:48px;">📄</div>
        <div style="font-size:22px; font-weight:700; color:#818cf8; margin-top:8px;">ContractBot</div>
        <div style="font-size:12px; color:#475569; margin-top:4px;">AI Contract Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="color:#94a3b8; font-size:13px; line-height:1.8;">
    <b style="color:#818cf8;">How it works</b><br><br>
    1️⃣ &nbsp;Upload a PDF <b>or</b> paste your contract text<br><br>
    2️⃣ &nbsp;Click <b>Analyze Contract</b><br><br>
    3️⃣ &nbsp;Review the structured analysis, risk flags, and unusual clauses<br><br>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="color:#475569; font-size:12px; line-height:1.6;">
    <b style="color:#64748b;">Powered by</b><br>
    🤖 Gemini AI (Google)<br>
    📑 PyMuPDF (PDF Parsing)<br>
    ⚡ FastAPI Backend<br>
    🎈 Streamlit Frontend
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="color:#ef4444; font-size:11px; line-height:1.5;">
    ⚠️ <b>Disclaimer:</b> This tool is for informational purposes only and does not constitute legal advice. Always consult a qualified legal professional for binding decisions.
    </div>
    """, unsafe_allow_html=True)


# ── Main Header ───────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>📄 ContractBot</h1>
    <p>Instant AI-powered contract analysis — understand risks, terms, and obligations in seconds</p>
</div>
""", unsafe_allow_html=True)


# ── Input Section ─────────────────────────────────────────────────────────────

# Initialize session state
if "contract_text" not in st.session_state:
    st.session_state.contract_text = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

tab_text, tab_pdf = st.tabs(["📝 Paste Contract Text", "📂 Upload PDF"])

contract_text_input = None
pdf_file = None

with tab_text:
    st.markdown(
        '<p style="color:#64748b; font-size:13px; margin-bottom:6px;">Paste the full contract text below</p>',
        unsafe_allow_html=True
    )
    contract_text_input = st.text_area(
        label="Contract Text",
        placeholder="Paste your contract text here...\n\nExample: SERVICE AGREEMENT\nThis Agreement is entered into...",
        height=280,
        label_visibility="collapsed",
        key="contract_text"  # persists across re-runs via session_state
    )

with tab_pdf:
    st.markdown(
        '<p style="color:#64748b; font-size:13px; margin-bottom:6px;">Upload a PDF contract file</p>',
        unsafe_allow_html=True
    )
    pdf_file = st.file_uploader(
        "Upload Contract PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )
    if pdf_file:
        st.success(f"✅ File loaded: **{pdf_file.name}** ({pdf_file.size:,} bytes)")

st.markdown("<br>", unsafe_allow_html=True)
analyze_clicked = st.button("🔍 Analyze Contract", use_container_width=True)


# ── Analysis ──────────────────────────────────────────────────────────────────

if analyze_clicked:
    # Read from session_state in case widget value was not updated this run
    active_text = st.session_state.get("contract_text", "") or ""
    has_text = len(active_text.strip()) > 50
    has_pdf = pdf_file is not None

    if not has_text and not has_pdf:
        st.error("⚠️ Please paste contract text or upload a PDF before analyzing.")
        st.stop()

    with st.spinner("🤖 Claude is reviewing your contract... This may take 15–30 seconds."):
        try:
            if has_pdf:
                result = call_analyze_pdf(pdf_file.read(), pdf_file.name)
            else:
                result = call_analyze_text(active_text)
        except requests.exceptions.ConnectionError:
            st.error(
                "❌ **Cannot connect to the backend.**\n\n"
                "Make sure the FastAPI server is running:\n"
                "```\ncd backend\nuvicorn main:app --reload --port 8000\n```"
            )
            st.stop()
        except requests.exceptions.HTTPError as e:
            try:
                detail = e.response.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            st.error(f"❌ **Backend error:** {detail}")
            st.stop()
        except Exception as e:
            st.error(f"❌ **Unexpected error:** {str(e)}")
            st.stop()

    if not result.get("success"):
        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        st.stop()

    analysis = result.get("analysis", {})

    st.markdown("---")
    st.markdown(
        '<h2 style="color:#818cf8; font-size:22px; font-weight:700; margin-bottom:16px;">📊 Contract Analysis</h2>',
        unsafe_allow_html=True
    )

    # ── Summary ───────────────────────────────────────────────────────────────
    summary = analysis.get("plain_english_summary", "")
    if summary:
        st.markdown(f'<div class="summary-box">📋 <b>Summary</b><br><br>{summary}</div>', unsafe_allow_html=True)

    # ── Two-column layout ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        # Key Parties
        parties = analysis.get("key_parties", {})
        other = parties.get("other_parties", [])
        other_str = ", ".join(other) if other else "None"
        parties_html = (
            info_row("Party 1 (Service Provider)", parties.get("party_1", "")) +
            info_row("Party 2 (Client)", parties.get("party_2", "")) +
            info_row("Other Parties", other_str)
        )
        st.markdown(card("🤝 Key Parties", parties_html), unsafe_allow_html=True)

        # Contract Duration
        duration = analysis.get("contract_duration", {})
        auto_renewal = duration.get("auto_renewal", "Not Found")
        auto_renewal_str = {
            "Yes": "✅ Yes — auto-renews",
            "No": "❌ No — manual renewal required",
        }.get(auto_renewal, "❓ Not specified")
        duration_html = (
            info_row("Start Date", duration.get("start_date", "")) +
            info_row("End Date", duration.get("end_date", "")) +
            info_row("Renewal Terms", duration.get("renewal_terms", "")) +
            info_row("Auto-Renewal", auto_renewal_str)
        )
        st.markdown(card("📅 Contract Duration", duration_html), unsafe_allow_html=True)

        # Confidentiality
        conf = analysis.get("confidentiality_terms", "Not specified")
        st.markdown(card("🔒 Confidentiality", conf), unsafe_allow_html=True)

    with col2:
        # Payment Terms
        payment = analysis.get("payment_terms", {})
        payment_html = (
            info_row("Total Amount", payment.get("amounts", "")) +
            info_row("Payment Schedule", payment.get("payment_schedule", "")) +
            info_row("Late Fees", payment.get("late_fees", "")) +
            info_row("Refund Policy", payment.get("refund_policy", ""))
        )
        st.markdown(card("💰 Payment Terms", payment_html), unsafe_allow_html=True)

        # Termination
        term = analysis.get("termination_clauses", {})
        term_html = (
            info_row("Termination for Convenience", term.get("termination_for_convenience", "")) +
            info_row("Termination for Cause", term.get("termination_for_cause", "")) +
            info_row("Notice Period", term.get("notice_period", "")) +
            info_row("Exit Conditions", term.get("exit_conditions", ""))
        )
        st.markdown(card("🚪 Termination Clauses", term_html), unsafe_allow_html=True)

        # IP Terms
        ip = analysis.get("intellectual_property_terms", "Not specified")
        st.markdown(card("💡 Intellectual Property", ip), unsafe_allow_html=True)

    # ── Liability & Indemnity ─────────────────────────────────────────────────
    liability = analysis.get("liability_and_indemnity", {})
    liability_html = (
        info_row("Liability Cap", liability.get("liability_cap", "")) +
        info_row("Indemnification", liability.get("indemnification_clause", ""))
    )
    st.markdown(card("⚖️ Liability & Indemnity", liability_html), unsafe_allow_html=True)

    # ── Risk Flags ────────────────────────────────────────────────────────────
    st.markdown(
        '<h3 style="color:#818cf8; font-size:18px; font-weight:700; margin: 20px 0 12px;">🚨 Risk Flags</h3>',
        unsafe_allow_html=True
    )
    risk_flags = analysis.get("risk_flags", [])
    if risk_flags:
        # Sort: High → Medium → Low
        order = {"high": 0, "medium": 1, "low": 2}
        risk_flags_sorted = sorted(
            risk_flags,
            key=lambda r: order.get(r.get("risk_level", "low").lower(), 3)
        )
        for flag in risk_flags_sorted:
            level = flag.get("risk_level", "Low")
            css_class = risk_class(level)
            badge = risk_badge(level)
            category = flag.get("category", "Unknown")
            reason = flag.get("reason", "")
            clause_ref = flag.get("clause_reference", "")
            ref_html = f'<br><span style="color:#475569; font-size:12px;">📌 {clause_ref}</span>' if clause_ref else ""
            st.markdown(f"""
            <div class="risk-card {css_class}">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-weight:600; font-size:15px; color:#e2e8f0;">{category}</span>
                    {badge}
                </div>
                <div style="color:#94a3b8; font-size:14px; line-height:1.6;">{reason}{ref_html}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No risk flags identified.")

    # ── Unusual / Risky Clauses ───────────────────────────────────────────────
    unusual = analysis.get("unusual_or_risky_clauses", [])
    if unusual:
        st.markdown(
            '<h3 style="color:#fbbf24; font-size:18px; font-weight:700; margin: 20px 0 12px;">⚠️ Unusual or Risky Clauses</h3>',
            unsafe_allow_html=True
        )
        for item in unusual:
            clause = item.get("clause", "")
            reason = item.get("why_it_is_risky", "")
            st.markdown(f"""
            <div class="clause-card">
                <div style="font-weight:600; color:#fbbf24; margin-bottom:6px;">📌 {clause}</div>
                <div style="color:#d1d5db; font-size:14px; line-height:1.6;">{reason}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Raw JSON expander ─────────────────────────────────────────────────────
    with st.expander("🗂️ View Raw JSON Response"):
        st.json(analysis)

    st.markdown(
        '<p style="color:#374151; font-size:11px; text-align:center; margin-top:24px;">'
        'ContractBot is for informational purposes only. Not legal advice.'
        '</p>',
        unsafe_allow_html=True
    )
