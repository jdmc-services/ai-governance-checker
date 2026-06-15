import streamlit as st
import anthropic
import json

st.set_page_config(
    page_title="AI Governance Readiness Checker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0A0F1E; }
.main { background-color: #0A0F1E; }

.hero {
    background: linear-gradient(135deg, #1B3A6B 0%, #0D7680 100%);
    padding: 36px 40px;
    border-radius: 16px;
    margin-bottom: 28px;
    border: 1px solid rgba(13,118,128,0.3);
}
.hero h1 { color: #FFFFFF; font-size: 30px; font-weight: 700; margin: 0 0 8px 0; }
.hero p { color: rgba(255,255,255,0.75); font-size: 14px; margin: 0; line-height: 1.6; }
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    color: #FFD700;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 12px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

.domain-card {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.domain-title {
    font-size: 15px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 4px;
}
.domain-desc {
    font-size: 12px;
    color: #6B7280;
    margin-bottom: 16px;
    line-height: 1.5;
}

.score-card {
    border-radius: 16px;
    padding: 28px;
    text-align: center;
    margin-bottom: 20px;
}
.score-number {
    font-size: 72px;
    font-weight: 700;
    line-height: 1;
    margin: 8px 0;
}
.score-label {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 8px;
}

.domain-result {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 10px;
}
.domain-result-title {
    font-size: 13px;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 8px;
}
.score-bar-bg {
    background: #1F2937;
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
    margin-bottom: 4px;
}
.gap-card {
    background: #1A0808;
    border: 1px solid #7F1D1D;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 10px;
}
.gap-title {
    font-size: 13px;
    font-weight: 700;
    color: #FCA5A5;
    margin-bottom: 6px;
}
.gap-fix {
    font-size: 12px;
    color: #9CA3AF;
    line-height: 1.6;
}
.ai-rec {
    background: linear-gradient(135deg, #0D1F3C, #0A2540);
    border: 1px solid #0D7680;
    border-radius: 12px;
    padding: 24px;
    margin-top: 16px;
}
.ai-rec-header {
    font-size: 12px;
    font-weight: 700;
    color: #0D7680;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 12px;
}
.verdict-banner {
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 20px 0;
}
.disclaimer {
    background: #1F1010;
    border: 1px solid #7F1D1D;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 11px;
    color: #FCA5A5;
    margin-top: 24px;
}
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label {
    color: #D1D5DB !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #0D7680, #1B3A6B);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 15px;
    padding: 12px 24px;
    width: 100%;
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #0A9AA6, #1E3F7A);
}
.stTabs [data-baseweb="tab-list"] {
    background-color: #111827;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #6B7280;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background-color: #1B3A6B !important;
    color: #FFFFFF !important;
}
footer { display: none; }
#MainMenu { display: none; }
</style>
""", unsafe_allow_html=True)

# ── API key from secrets ──────────────────────────────────
api_key = st.secrets.get("ANTHROPIC_API_KEY", "")

# ── Hero ─────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">🛡️ Free Assessment Tool — No Login Required</div>
    <h1>AI Governance Readiness Checker</h1>
    <p>Answer 12 questions about your organization's AI governance posture. Get an instant score, 
    gap analysis, and a Claude AI-powered remediation recommendation — built on the responsible AI 
    framework used in healthcare contact center modernization.</p>
</div>
""", unsafe_allow_html=True)

# ── Questions ─────────────────────────────────────────────
DOMAINS = {
    "Data Governance": {
        "desc": "How your organization classifies, protects, and controls data used by AI systems",
        "icon": "🗂️",
        "questions": [
            "Does your organization have a data classification policy that specifically addresses AI tools and inputs?",
            "Are staff trained to identify and handle sensitive data (PHI, PII, credentials) when using AI tools?",
        ]
    },
    "HIPAA & Compliance": {
        "desc": "Your organization's compliance posture specific to AI deployment in regulated environments",
        "icon": "⚕️",
        "questions": [
            "Have you conducted a formal HIPAA risk analysis for AI tool deployment per 45 CFR 164.308?",
            "Do all AI vendors have executed Business Associate Agreements (BAAs) before accessing any data?",
        ]
    },
    "Vendor Governance": {
        "desc": "How you evaluate, monitor, and control AI vendors and their subprocessors",
        "icon": "📄",
        "questions": [
            "Do you review AI vendor model cards and subprocessor chains before deployment?",
            "Do vendor contracts include right-to-audit clauses and annual risk assessment requirements?",
        ]
    },
    "Access Controls": {
        "desc": "Role-based access, authentication, and output visibility controls for AI systems",
        "icon": "🔒",
        "questions": [
            "Is role-based access control (RBAC) enforced on all AI-generated outputs and summaries?",
            "Is multi-factor authentication (MFA) required for all staff accessing AI tools?",
        ]
    },
    "Audit & Logging": {
        "desc": "Your organization's ability to track, review, and retain AI interaction records",
        "icon": "📋",
        "questions": [
            "Are all AI model inputs, outputs, and escalations logged to an immutable audit trail?",
            "Are AI interaction logs retained for the HIPAA minimum 6-year standard?",
        ]
    },
    "Human Oversight": {
        "desc": "Human-in-the-loop controls that ensure AI outputs are reviewed before consequential actions",
        "icon": "👤",
        "questions": [
            "Are human-in-the-loop (HITL) controls in place for any AI interaction involving clinical adjacency?",
            "Are escalation rules defined and tested for AI outputs below confidence thresholds or involving patient safety?",
        ]
    }
}

OPTIONS = ["Yes — fully in place", "Partially — in progress", "No — not yet addressed", "Unknown"]
SCORES = {"Yes — fully in place": 100, "Partially — in progress": 50, "No — not yet addressed": 0, "Unknown": 10}
OPTION_SHORT = {"Yes — fully in place": "Yes", "Partially — in progress": "Partial", "No — not yet addressed": "No", "Unknown": "Unknown"}

# ── Assessment form ───────────────────────────────────────
st.markdown('<div style="color:#FFFFFF;font-size:18px;font-weight:700;margin:20px 0 16px 0;padding-bottom:8px;border-bottom:2px solid #0D7680">📋 Assessment Questions</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#6B7280;font-size:13px;margin-bottom:20px">Answer honestly based on your current state — not your aspirational state. Partial credit is given for in-progress items.</div>', unsafe_allow_html=True)

answers = {}
org_type = st.selectbox(
    "Organization Type (for context-specific recommendations)",
    ["Healthcare System / Hospital", "Health Plan / Payer", "Healthcare IT Vendor",
     "Ambulatory / Clinic", "Government / Public Health", "Other Healthcare Organization"],
    help="Used to tailor AI recommendations to your specific regulatory environment"
)

st.markdown("<br>", unsafe_allow_html=True)

for domain, info in DOMAINS.items():
    st.markdown(f"""
    <div class="domain-card">
        <div class="domain-title">{info['icon']}  {domain}</div>
        <div class="domain-desc">{info['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    for q in info["questions"]:
        answers[f"{domain}::{q}"] = st.selectbox(
            q,
            OPTIONS,
            key=f"{domain}::{q}",
            index=3
        )
    st.markdown("<br>", unsafe_allow_html=True)

# ── Submit ────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run = st.button("🛡️ Generate My Governance Score", use_container_width=True)

# ── Results ───────────────────────────────────────────────
if run:
    # Check all answered
    unanswered = [k for k, v in answers.items() if v == "Unknown"]

    # Calculate scores
    domain_scores = {}
    for domain in DOMAINS:
        qs = [k for k in answers if k.startswith(domain + "::")]
        if qs:
            domain_scores[domain] = sum(SCORES[answers[q]] for q in qs) / len(qs)

    overall = sum(domain_scores.values()) / len(domain_scores) if domain_scores else 0

    # Verdict
    if overall >= 80:
        verdict = "STRONG GOVERNANCE"
        verdict_color = "#10B981"
        verdict_bg = "#064E3B"
        verdict_border = "#10B981"
        verdict_desc = "Your governance posture is strong. You are ready to proceed with structured AI deployment with ongoing monitoring."
    elif overall >= 60:
        verdict = "MODERATE — GAPS EXIST"
        verdict_color = "#F59E0B"
        verdict_bg = "#78350F"
        verdict_border = "#F59E0B"
        verdict_desc = "You have a foundational governance posture but critical gaps need to be addressed before scaling AI deployment."
    elif overall >= 35:
        verdict = "HIGH RISK — REMEDIATION REQUIRED"
        verdict_color = "#EF4444"
        verdict_bg = "#7F1D1D"
        verdict_border = "#EF4444"
        verdict_desc = "Significant governance gaps exist. AI deployment without remediation creates substantial compliance and operational risk."
    else:
        verdict = "CRITICAL — NOT READY FOR AI"
        verdict_color = "#DC2626"
        verdict_bg = "#450A0A"
        verdict_border = "#DC2626"
        verdict_desc = "Your organization is not yet ready for AI deployment. Foundational governance controls must be established first."

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="color:#FFFFFF;font-size:18px;font-weight:700;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #0D7680">📊 Your Governance Readiness Results</div>', unsafe_allow_html=True)

    # Score + verdict
    col_score, col_verdict = st.columns([1, 2])
    with col_score:
        score_color = verdict_color
        st.markdown(f"""
        <div class="score-card" style="background:{verdict_bg};border:2px solid {verdict_border}">
            <div style="color:{score_color};font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px">Overall Score</div>
            <div class="score-number" style="color:{score_color}">{int(overall)}</div>
            <div style="color:#9CA3AF;font-size:12px">out of 100</div>
            <div class="score-label" style="color:{score_color}">{verdict}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_verdict:
        st.markdown(f"""
        <div style="background:{verdict_bg};border:1px solid {verdict_border};border-radius:12px;padding:20px;height:100%">
            <div style="color:{verdict_color};font-size:14px;font-weight:700;margin-bottom:10px">{verdict}</div>
            <div style="color:#D1D5DB;font-size:13px;line-height:1.7;margin-bottom:14px">{verdict_desc}</div>
            <div style="color:#6B7280;font-size:11px">Organization Type: {org_type}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Domain breakdown
    st.markdown('<div style="color:#FFFFFF;font-size:15px;font-weight:700;margin-bottom:12px">Domain-by-Domain Breakdown</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    for i, (domain, score) in enumerate(domain_scores.items()):
        col = cols[i % 2]
        bar_color = "#10B981" if score >= 80 else "#F59E0B" if score >= 50 else "#EF4444"
        icon = DOMAINS[domain]["icon"]
        with col:
            st.markdown(f"""
            <div class="domain-result">
                <div class="domain-result-title">{icon}  {domain}</div>
                <div class="score-bar-bg">
                    <div style="height:8px;width:{score}%;background:{bar_color};border-radius:4px"></div>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:4px">
                    <div style="font-size:11px;color:#6B7280">
                        {"✅ Strong" if score >= 80 else "⚠️ Partial" if score >= 50 else "❌ Gap"}
                    </div>
                    <div style="font-size:12px;font-weight:700;color:{bar_color}">{int(score)} / 100</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Top gaps
    gaps = [(domain, score) for domain, score in domain_scores.items() if score < 80]
    gaps.sort(key=lambda x: x[1])

    gap_fixes = {
        "Data Governance": "Develop a data classification standard that explicitly covers AI tool inputs. Define Restricted, Sensitive, Internal, and Public tiers with AI-specific guidance. Train all staff with scenario-based examples before any AI tool goes live.",
        "HIPAA & Compliance": "Conduct a formal HIPAA risk analysis for AI deployment per 45 CFR 164.308 before any vendor accesses data. Execute BAAs with all AI vendors and review annually. Document your compliance posture in writing.",
        "Vendor Governance": "Review AI vendor model cards, subprocessor chains, and data handling practices before contract execution. Add right-to-audit clauses to all AI vendor contracts. Conduct annual vendor risk assessments.",
        "Access Controls": "Implement RBAC on all AI-generated outputs — only assigned roles should see AI summaries, scores, or recommendations. Enforce MFA on all AI tool access. Review access logs quarterly.",
        "Audit & Logging": "Configure immutable audit logging for all AI interactions — inputs, outputs, confidence scores, and escalations. Retain logs for HIPAA minimum 6 years. Set anomaly detection alerts for unusual access patterns.",
        "Human Oversight": "Define hard-coded escalation triggers for clinical adjacency, patient safety, and low-confidence outputs. Assign a named human reviewer for all AI outputs affecting patient care workflows. Test escalation paths quarterly."
    }

    if gaps:
        st.markdown('<div style="color:#FFFFFF;font-size:15px;font-weight:700;margin-bottom:12px">🔍 Top Governance Gaps to Address</div>', unsafe_allow_html=True)
        for domain, score in gaps[:3]:
            st.markdown(f"""
            <div class="gap-card">
                <div class="gap-title">{DOMAINS[domain]['icon']}  {domain} — Score: {int(score)}/100</div>
                <div class="gap-fix">{gap_fixes.get(domain, 'Review and strengthen controls in this domain.')}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Claude AI recommendation
    if api_key:
        with st.spinner("Generating your personalized AI governance recommendation..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)

                gap_summary = "\n".join([f"- {d}: {int(s)}/100" for d, s in domain_scores.items()])
                answers_summary = "\n".join([
                    f"- {k.split('::')[1]}: {OPTION_SHORT.get(v, v)}"
                    for k, v in answers.items()
                ])

                prompt = f"""You are a senior responsible AI governance advisor for healthcare organizations.

Organization type: {org_type}
Overall governance score: {int(overall)}/100
Verdict: {verdict}

Domain scores:
{gap_summary}

Question answers:
{answers_summary}

Provide a personalized governance recommendation in this exact JSON format:
{{
  "priority_action": "The single most important governance action to take this week — specific and actionable",
  "30_day_plan": "Three specific actions to complete in the next 30 days",
  "biggest_risk": "The most significant compliance or operational risk given their current posture",
  "quick_win": "One governance improvement they can implement in 24 hours with no budget",
  "readiness_path": "How long it will realistically take to reach governance readiness for AI deployment",
  "executive_message": "A one-sentence message they can bring to their CIO or CISO to get governance work prioritized"
}}

Be specific to healthcare and their organization type. Use plain language. No jargon."""

                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )

                raw = response.content[0].text.strip()
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0].strip()
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0].strip()
                start = raw.find("{"); end = raw.rfind("}") + 1
                if start != -1 and end > start:
                    raw = raw[start:end]
                raw = raw.replace("\u2019","'").replace("\u2018","'").replace("\u201c",'"').replace("\u201d",'"').replace("\u2013","-").replace("\u2014","-")

                r = json.loads(raw)

                st.markdown(f"""
                <div class="ai-rec">
                    <div class="ai-rec-header">🤖 Claude AI — Personalized Governance Recommendation</div>

                    <div style="background:#0A0F1E;border-radius:8px;padding:14px;margin-bottom:12px">
                        <div style="color:#0D7680;font-size:11px;font-weight:700;text-transform:uppercase;margin-bottom:6px">⚡ Priority Action This Week</div>
                        <div style="color:#FFFFFF;font-size:14px;font-weight:600">{r.get('priority_action','—')}</div>
                    </div>

                    <div style="background:#0A0F1E;border-radius:8px;padding:14px;margin-bottom:12px">
                        <div style="color:#0D7680;font-size:11px;font-weight:700;text-transform:uppercase;margin-bottom:6px">📅 30-Day Plan</div>
                        <div style="color:#D1D5DB;font-size:13px;line-height:1.7">{r.get('30_day_plan','—')}</div>
                    </div>

                    <div style="display:flex;gap:12px;margin-bottom:12px">
                        <div style="flex:1;background:#1A0808;border:1px solid #7F1D1D;border-radius:8px;padding:14px">
                            <div style="color:#FCA5A5;font-size:11px;font-weight:700;text-transform:uppercase;margin-bottom:6px">⚠️ Biggest Risk</div>
                            <div style="color:#D1D5DB;font-size:12px;line-height:1.6">{r.get('biggest_risk','—')}</div>
                        </div>
                        <div style="flex:1;background:#064E3B;border:1px solid #10B981;border-radius:8px;padding:14px">
                            <div style="color:#6EE7B7;font-size:11px;font-weight:700;text-transform:uppercase;margin-bottom:6px">✅ Quick Win (24 hrs)</div>
                            <div style="color:#D1D5DB;font-size:12px;line-height:1.6">{r.get('quick_win','—')}</div>
                        </div>
                    </div>

                    <div style="background:#0A0F1E;border-radius:8px;padding:14px;margin-bottom:12px">
                        <div style="color:#0D7680;font-size:11px;font-weight:700;text-transform:uppercase;margin-bottom:6px">🗓️ Realistic Readiness Timeline</div>
                        <div style="color:#D1D5DB;font-size:13px">{r.get('readiness_path','—')}</div>
                    </div>

                    <div style="background:#1B3A6B;border-radius:8px;padding:14px">
                        <div style="color:#AABBDD;font-size:11px;font-weight:700;text-transform:uppercase;margin-bottom:6px">📢 Message for Your CIO / CISO</div>
                        <div style="color:#FFFFFF;font-size:14px;font-weight:600;font-style:italic">"{r.get('executive_message','—')}"</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"AI recommendation unavailable: {str(e)}")
    else:
        st.markdown("""
        <div style="background:#111827;border:1px dashed #374151;border-radius:10px;padding:20px;text-align:center">
            <div style="color:#6B7280;font-size:13px">AI-powered personalized recommendation requires API configuration.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
    ⚠️ This assessment is for educational and portfolio demonstration purposes only. Results are not legal or compliance advice.
    No PHI or confidential organizational data is collected or stored. All responses are processed in-session only.
    </div>
    """, unsafe_allow_html=True)

# ── Footer CTA ────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="background:linear-gradient(135deg,#1B3A6B,#0D7680);border-radius:12px;padding:24px;text-align:center;margin-top:20px">
    <div style="color:#FFFFFF;font-size:16px;font-weight:700;margin-bottom:8px">Want a full AI Contact Center Readiness Assessment?</div>
    <div style="color:rgba(255,255,255,0.75);font-size:13px;margin-bottom:16px">James D. McClain, MBA — Healthcare IT Leader | AI Contact Center Modernization | Responsible AI Governance</div>
    <a href="https://ai-cc-intelligence.streamlit.app" target="_blank"
       style="background:rgba(255,255,255,0.15);color:#FFFFFF;padding:10px 24px;border-radius:8px;
              text-decoration:none;font-weight:600;font-size:13px;border:1px solid rgba(255,255,255,0.3)">
        Try the Full AI Intelligence Hub →
    </a>
    <div style="margin-top:12px">
        <a href="https://www.linkedin.com/in/jdmcclain/" target="_blank"
           style="color:rgba(255,255,255,0.6);font-size:12px;text-decoration:none">
            Connect on LinkedIn
        </a>
    </div>
</div>
""", unsafe_allow_html=True)
