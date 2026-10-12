import html
import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

from backend.services.document_export import format_docx, format_pdf, format_txt
from backend.services.text_utils import format_html_preview

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "LegalEase")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title=APP_NAME, page_icon="⚖️", layout="wide")

st.markdown("""
<style>
.hero { padding: 1.2rem 1.5rem; border-radius: 18px; background: linear-gradient(135deg,#101827,#24324a); color:white; margin-bottom:1rem; }
.hero h1 { margin:0; font-size:2.2rem; }
.hero p { margin:.4rem 0 0; color:#d7deea; }
.preview { background:#10141c; color:#edf2f7; border:1px solid #2e3a4d; border-radius:14px; padding:1.25rem; max-height:620px; overflow:auto; line-height:1.65; }
.small { color:#718096; font-size:.85rem; }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="hero"><h1>⚖️ {html.escape(APP_NAME)}</h1><p>AI-powered legal document drafting, editing and export.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Document settings")
    document_type = st.selectbox("Document type", [
        "Employment Contract", "Non-Disclosure Agreement", "Lease Agreement",
        "Employment Offer Letter", "Freelance Work Contract", "Service Agreement", "Custom Agreement"
    ])
    effective_date = st.date_input("Effective date", value=date.today()).isoformat()
    jurisdiction = st.text_input("Jurisdiction (optional)", placeholder="e.g. Tamil Nadu, India")
    st.caption("For real Gemini generation, set GEMINI_API_KEY in .env.")

col1, col2 = st.columns(2)
with col1:
    parties = st.text_area("Parties involved", height=130, placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)")
with col2:
    terms = st.text_area("Terms & conditions", height=130, placeholder="Payment within 30 days; confidentiality must be maintained; either party may terminate with 15 days notice")

uploaded_logo = st.file_uploader("Optional logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

if "document" not in st.session_state:
    st.session_state.document = ""
if "model" not in st.session_state:
    st.session_state.model = ""
if "fallback" not in st.session_state:
    st.session_state.fallback = False

if st.button("✨ Generate Document", type="primary", use_container_width=True):
    if not parties.strip() or not terms.strip():
        st.error("Please enter the parties and at least one term.")
    else:
        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
            "jurisdiction": jurisdiction,
        }
        try:
            with st.spinner("Generating document..."):
                response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=90)
            if response.ok:
                data = response.json()
                st.session_state.document = data["content"]
                st.session_state.model = data["model"]
                st.session_state.fallback = data.get("fallback", False)
            else:
                detail = response.json().get("detail", response.text)
                st.error(f"Backend error: {detail}")
        except requests.RequestException as exc:
            st.error(f"Could not connect to FastAPI at {BACKEND_URL}. Start the backend first. Details: {exc}")

if st.session_state.document:
    st.divider()
    st.subheader("Document preview")
    if st.session_state.fallback:
        st.info("Demo mode: no Gemini API key was detected. The app generated a local fallback draft so the UI and exports can still be tested.")
    else:
        st.success(f"Generated with {st.session_state.model}")

    st.markdown(f'<div class="preview">{format_html_preview(st.session_state.document)}</div>', unsafe_allow_html=True)
    st.subheader("Edit document")
    edited = st.text_area("Editable document", value=st.session_state.document, height=500, label_visibility="collapsed")
    st.session_state.document = edited

    logo_path = None
    if uploaded_logo is not None:
        import tempfile
        suffix = os.path.splitext(uploaded_logo.name)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(uploaded_logo.getvalue())
        tmp.close()
        logo_path = tmp.name

    d1, d2, d3 = st.columns(3)
    base = document_type.lower().replace(" ", "_")
    with d1:
        st.download_button("⬇️ Download TXT", data=format_txt(edited), file_name=f"{base}.txt", mime="text/plain", use_container_width=True)
    with d2:
        st.download_button("⬇️ Download DOCX", data=format_docx(edited, document_type, terms, logo_path), file_name=f"{base}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    with d3:
        st.download_button("⬇️ Download PDF", data=format_pdf(edited, document_type, logo_path), file_name=f"{base}.pdf", mime="application/pdf", use_container_width=True)

st.caption("LegalEase is a drafting aid and does not replace advice from a qualified legal professional.")
