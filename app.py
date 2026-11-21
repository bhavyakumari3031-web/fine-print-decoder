import os
import json
import html
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

BASE_DIR = Path(__file__).parent
SAMPLES_DIR = BASE_DIR / "samples"
load_dotenv(BASE_DIR / ".env")
MODEL = "openai/gpt-oss-120b"


def get_key():
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


client = Groq(api_key=get_key())

PROMPT = """You are a financial document checker for Indian students and families.
Read the document and reply with ONLY valid JSON (no markdown, no extra text) in this exact shape:
{
  "document_type": "loan | insurance | credit card | other",
  "risk_rating": "Low | Medium | High",
  "risk_reason": "one short sentence in simple Hinglish",
  "clauses": [
    {"quote": "exact line from the document",
     "severity": "High | Medium | Low",
     "explanation": "1-2 sentences in simple Hinglish, plain text, no markdown"}
  ],
  "questions_to_ask": ["3 to 5 short questions in simple Hinglish the person should ask the provider before signing"],
    "faq": [{"question": "a question a normal borrower would ask about this document", "answer": "short answer based only on the document, in simple Hinglish"}],
  "loan_details": {
    "amount": number or null,
    "tenure_months": number or null,
    "interest_rate_percent": number or null,
    "rate_period": "month" or "year" or null,
    "interest_type": "flat" or "reducing" or null,
    "processing_fee_percent": number or null
  }
}
Rules: quote lines exactly as written. Only list real risks. Use null for anything not in the document.Give 4 to 5 faq items.

Document:
"""

CSS = """
<style>
.stApp {background: radial-gradient(circle at top, #14203a 0%, #0b0f1a 55%); color:#e6edf7;}
.stApp p, .stApp label {color:#e6edf7;}
.stApp p.tag {color:#94a3b8;}
.stApp .card p {color:#cbd5e1;}
h1, h2, h3 {color:#f1f5f9;}
.hero {text-align:center; padding-top:10px;}
.hero h1 {font-size:2.4rem; margin-bottom:0;}
.accent {color:#4ade80 !important;}
.tag {text-align:center; margin-bottom:1.5rem;}
.badge {text-align:center; font-size:1.6rem; font-weight:800; padding:14px; border-radius:14px; margin:12px 0;}
.badge small {display:block; font-size:0.95rem; font-weight:400; margin-top:4px;}
.badge-High {background:rgba(248,113,113,.12); color:#f87171; border:1px solid #f87171;}
.badge-Medium {background:rgba(251,191,36,.12); color:#fbbf24; border:1px solid #fbbf24;}
.badge-Low {background:rgba(74,222,128,.12); color:#4ade80; border:1px solid #4ade80;}
.card {background:#131a2b; border-radius:12px; padding:14px 16px; margin:10px 0; border-left:5px solid #4ade80;}
.card-High {border-left-color:#f87171;}
.card-Medium {border-left-color:#fbbf24;}
.card-Low {border-left-color:#4ade80;}
.sev {font-size:0.75rem; font-weight:700; letter-spacing:1px; margin-bottom:6px;}
.sev-High {color:#f87171;}
.sev-Medium {color:#fbbf24;}
.sev-Low {color:#4ade80;}
.quote {font-family:Consolas, monospace; font-size:0.9rem; color:#e2e8f0; background:#0b0f1a; padding:8px 10px; border-radius:8px;}
.stButton>button {background:#4ade80; color:#0b0f1a; font-weight:700; border:0; border-radius:10px; padding:0.5rem 1.4rem;}
.stButton>button:hover {background:#86efac; color:#0b0f1a;}
[data-testid="stFileUploader"] section, textarea {background:#131a2b !important; color:#e6edf7 !important; border-radius:12px;}
[data-testid="stMetric"] {background:#131a2b; padding:14px; border-radius:12px; border:1px solid #1f2a44;}
[data-testid="stMetricValue"] {color:#4ade80;}
header[data-testid="stHeader"] {background:transparent;}
</style>
"""


def parse_json(raw):
    start, end = raw.find("{"), raw.rfind("}")
    return json.loads(raw[start:end + 1])


def analyse(text):
    response = client.chat.completions.create(
        model=MODEL,
                messages=[{"role": "user", "content": PROMPT.replace("simple Hinglish", "simple " + lang) + text}],
        temperature=0.2,
    )
    return parse_json(response.choices[0].message.content)


def read_upload(f):
    if f.name.lower().endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(f)
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    return f.getvalue().decode("utf-8", errors="ignore")


def num(x, default):
    try:
        return float(x) if x is not None else default
    except (TypeError, ValueError):
        return default


def solve_monthly_rate(net, emi, n):
    if net >= emi * n:
        return 0.0
    lo, hi = 1e-9, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        pv = emi * (1 - (1 + mid) ** -n) / mid
        if pv > net:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def show_results(result):
    rating = result.get("risk_rating", "Medium")
    if rating not in ("Low", "Medium", "High"):
        rating = "Medium"
    reason = html.escape(str(result.get("risk_reason", "")))
    st.markdown(
        f'<div class="badge badge-{rating}">{rating.upper()} RISK<small>{reason}</small></div>',
        unsafe_allow_html=True,
    )
    clauses = result.get("clauses", [])
    st.subheader(f"⚠️ {len(clauses)} risky clauses found")
    for c in clauses:
        sev = c.get("severity", "Medium")
        if sev not in ("Low", "Medium", "High"):
            sev = "Medium"
        quote = html.escape(str(c.get("quote", "")))
        why = html.escape(str(c.get("explanation", "")))
        st.markdown(
            f'''<div class="card card-{sev}">
<div class="sev sev-{sev}">{sev.upper()}</div>
<div class="quote">{quote}</div>
<p style="margin:10px 0 0 0;">{why}</p>
</div>''',
            unsafe_allow_html=True,
        )
    questions = result.get("questions_to_ask") or []
    if questions:
        st.subheader("✅ Ask before you sign")
        for q in questions:
            st.markdown(f"- {q}")
    faq = result.get("faq") or []
    if faq:
        st.subheader("❓ Common questions")
        for item in faq:
            with st.expander(str(item.get("question", ""))):
                st.write(item.get("answer", ""))


def calculator(d, run_id):
    st.subheader("🧮 Real cost calculator")
    st.caption("Auto-filled from your document. Change any number if it is wrong.")
    c1, c2 = st.columns(2)
    amount = c1.number_input("Loan amount (₹)", min_value=0.0, value=num(d.get("amount"), 50000.0), step=1000.0, key=f"amt{run_id}")
    months = c2.number_input("Tenure (months)", min_value=1, value=max(1, int(num(d.get("tenure_months"), 12))), step=1, key=f"ten{run_id}")
    c3, c4 = st.columns(2)
    rate = c3.number_input("Interest rate (%)", min_value=0.0, value=num(d.get("interest_rate_percent"), 12.0), step=0.1, key=f"rate{run_id}")
    period = c4.selectbox("Rate is per", ["month", "year"], index=0 if d.get("rate_period") == "month" else 1, key=f"per{run_id}")
    c5, c6 = st.columns(2)
    kind = c5.selectbox("Interest type", ["flat", "reducing"], index=1 if d.get("interest_type") == "reducing" else 0, key=f"kind{run_id}")
    fee_pct = c6.number_input("Processing fee (%)", min_value=0.0, value=num(d.get("processing_fee_percent"), 0.0), step=0.5, key=f"fee{run_id}")

    n = int(months)
    monthly_rate = (rate if period == "month" else rate / 12) / 100
    if kind == "flat":
        interest = amount * monthly_rate * n
        emi = (amount + interest) / n
    elif monthly_rate > 0:
        emi = amount * monthly_rate * (1 + monthly_rate) ** n / ((1 + monthly_rate) ** n - 1)
    else:
        emi = amount / n
    total = emi * n
    fee = amount * fee_pct / 100
    received = amount - fee - fee * 0.18
    extra = total - received
    apr = solve_monthly_rate(received, emi, n) * 12 * 100 if received > 0 else 0.0

    m1, m2 = st.columns(2)
    m1.metric("You actually receive", f"₹{received:,.0f}")
    m2.metric("Total you repay", f"₹{total:,.0f}")
    m3, m4 = st.columns(2)
    m3.metric("Extra you pay", f"₹{extra:,.0f}")
    m4.metric("True yearly cost (APR)", f"{apr:.1f}%")
    st.caption(f"Monthly EMI ≈ ₹{emi:,.0f}. Processing fee includes 18% GST. For learning only, not financial advice.")


st.set_page_config(page_title="Fine-Print Decoder", page_icon="🔍")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🔍 Fine-Print <span class="accent">Decoder</span></h1></div>', unsafe_allow_html=True)
st.markdown('<p class="tag">Upload a loan, insurance or credit card document. AI finds the hidden traps, in simple Hinglish.</p>', unsafe_allow_html=True)

lang = st.radio("Explain in", ["English", "Hinglish"], horizontal=True)

if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.run_id = 0

uploaded = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
text = st.text_area("...or paste the document here", height=180)
if uploaded:
    try:
        text = read_upload(uploaded)
    except Exception:
        text = ""
        st.error("Could not read that file. Try pasting the text instead.")
st.caption("🔒 Use sample or invented documents only. Don't upload real personal data.")

analyse_clicked = st.button("Analyse", type="primary")

st.markdown("**Or try a sample:**")
s1, s2, s3 = st.columns(3)
sample = None
if s1.button("🏦 Loan"):
    sample = "loan_agreement.txt"
if s2.button("🛡️ Insurance"):
    sample = "insurance_policy.txt"
if s3.button("💳 Credit card"):
    sample = "credit_card_terms.txt"

to_analyse = None
if sample:
    to_analyse = (SAMPLES_DIR / sample).read_text(encoding="utf-8")
elif analyse_clicked:
    if not text.strip():
        st.warning("No readable text found. Upload a file or paste the document. For scanned PDFs, paste the text instead.")
    else:
        to_analyse = text

if to_analyse:
    with st.spinner("Reading the fine print..."):
        try:
            st.session_state.result = analyse(to_analyse)
            st.session_state.doc_text = to_analyse
            st.session_state.qa_answer = None
            st.session_state.run_id += 1
        except Exception as e:
            st.session_state.result = None
            st.error(f"Something went wrong: {e}")

result = st.session_state.result
if result:
    show_results(result)
    details = result.get("loan_details") or {}
    if details.get("amount"):
        calculator(details, st.session_state.run_id)

if result and st.session_state.get("doc_text"):
    st.subheader("💬 Ask your own question")
    q = st.text_input("For example: What happens if I pay late?", key="qa_input")
    if st.button("Ask") and q.strip():
        with st.spinner("Checking the document..."):
            try:
                r = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content":
                        "Answer ONLY from the document below, in simple " + lang + ". "
                        "Quote the exact line that supports your answer. "
                        "If the answer is not in the document, say so.\n\nDocument:\n"
                        + st.session_state.doc_text + "\n\nQuestion: " + q}],
                    temperature=0.2,
                )
                st.session_state.qa_answer = r.choices[0].message.content
            except Exception as e:
                st.error(f"Something went wrong: {e}")
    if st.session_state.get("qa_answer"):
        st.markdown(st.session_state.qa_answer)