import json
from pathlib import Path
from datetime import datetime
import streamlit as st

from components.header import render_header
from utils.pdf_utils import render_flipbook
from utils.config import get_setting
from services.rag_engine import create_vector_store
from services.groq_service import answer_from_brochure
from services.lead_service import save_lead

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
DEFAULT_PDF = ASSETS / "pragyanai_ai_engineering_brochure.pdf"
DEFAULT_FLYER = ASSETS / "pragyanai_program_flyer.png"
LINKEDIN_PROFILE = "https://www.linkedin.com/in/sateesh-ambesange-3020185/"
LINKEDIN_COMPANY = "https://www.linkedin.com/company/pragyan-smartai-technology-llp/"

st.set_page_config(page_title="PragyanAI | AI Engineering Program",
                   page_icon="🤖", layout="wide")
render_header()

with st.sidebar:
    st.markdown("### Program portal")
    uploaded_pdf = st.file_uploader("Upload / replace program PDF", type=["pdf"])
    uploaded_flyer = st.file_uploader("Upload / replace flyer", type=["png","jpg","jpeg"])
    st.markdown("---")
    st.markdown("**Contact PragyanAI**")
    st.write("☎ +91 97410 07422")
    st.write("✉ sateesh.ambesange@pragyanai.com")
    st.write("🌐 pragyanai.com")

pdf_bytes = uploaded_pdf.getvalue() if uploaded_pdf else DEFAULT_PDF.read_bytes()
with st.spinner("Preparing the program knowledge base…"):
    vector_store = create_vector_store(pdf_bytes)

# Keep the navigation order exactly as requested.
tabs = st.tabs([
    "1. Flyer & Introduction",
    "2. Program Flipbook",
    "3. Ask Chatbot",
    "4. Expression of Interest",
    "5. What Customers Say"
])

# 1. Flyer / program introduction / founder profile
with tabs[0]:
    st.markdown('<div class="section-title">Engineering the Complete AI Professional</div>',
                unsafe_allow_html=True)
    flyer = uploaded_flyer if uploaded_flyer else DEFAULT_FLYER
    if flyer:
        st.image(flyer, use_container_width=True)
    st.markdown("### Program introduction")
    st.write(
        "PragyanAI’s 6-Month Industry-Integrated AI Engineering Program is an online, "
        "live instructor-led, project-based learning program designed to help engineering "
        "students build practical AI engineering capabilities."
    )
    metrics = st.columns(4)
    for col, val, label in zip(metrics, ["6 Months","216","72","40"],
                               ["Program duration","Live training hours","Live sessions","Projects"]):
        col.markdown(f'<div class="metric"><strong>{val}</strong>{label}</div>',
                     unsafe_allow_html=True)
    st.markdown("### Key program highlights")
    highlights = [
        "24 active teaching weeks and 216 live online training hours",
        "Eight technical skill areas, from Python and Data Engineering to Agentic AI and MLOps",
        "40 projects: 32 guided and 8 independent",
        "Three research papers and one integrated AI product",
        "20% concepts and architecture + 80% practical implementation",
        "Build real-world applications, deploy AI solutions and develop a GitHub portfolio"
    ]
    for h in highlights:
        st.markdown(f"- {h}")
    st.markdown("---")
    st.markdown("### Sateesh Ambesange | Founder & CEO, PragyanAI")
    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown("**NITK Alumni**")
        st.markdown("**25+ Years**")
        st.caption("Product experience · Technology leadership · Serial entrepreneurship")
    with col2:
        st.write(
            "Stanford Ignite / Seed Spark · IIMA – Business Strategy Communication · SLP Fellow. "
            "Industry experience includes Intel, Samsung, Philips and SanDisk."
        )
        st.link_button("View Sateesh Ambesange on LinkedIn", LINKEDIN_PROFILE)
        st.link_button("Visit PragyanAI LinkedIn Company Page", LINKEDIN_COMPANY)
    st.caption("Contact: +91 97410 07422 · sateesh.ambesange@pragyanai.com · pragyanai.com")

# 2. Flipbook
with tabs[1]:
    st.markdown('<div class="section-title">View the Complete Program Brochure</div>',
                unsafe_allow_html=True)
    st.caption("Browse the brochure using the page-turn controls.")
    render_flipbook(pdf_bytes)

# 3. Chatbot: FAQ shortcuts and free-text questions
with tabs[2]:
    st.markdown('<div class="section-title">Ask PragyanAI – Program Assistant</div>',
                unsafe_allow_html=True)
    st.write("Ask a basic question or type your own question about the program.")
    faq_path = ROOT / "data" / "faq.json"
    faq_items = json.loads(faq_path.read_text(encoding="utf-8"))
    with st.expander("Basic frequently asked questions", expanded=True):
        for idx, item in enumerate(faq_items):
            with st.expander(item["q"]):
                st.write(item["a"])
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    question = st.chat_input("Type your own question about fees, eligibility, skills, projects…")
    if question:
        st.session_state.messages.append({"role":"user","content":question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching the program brochure…"):
                try:
                    reply = answer_from_brochure(question, vector_store)
                except Exception as exc:
                    reply = f"Unable to generate an answer right now. Please check the API configuration. ({exc})"
            st.markdown(reply)
        st.session_state.messages.append({"role":"assistant","content":reply})
    if st.button("Clear chat history"):
        st.session_state.messages = []
        st.rerun()

# 4. EOI
with tabs[3]:
    st.markdown('<div class="section-title">Expression of Interest – Student Registration</div>',
                unsafe_allow_html=True)
    st.write("Submit your details and the PragyanAI team can contact you about the program.")
    with st.form("student_eoi", clear_on_submit=True):
        c1,c2 = st.columns(2)
        name = c1.text_input("Full name *")
        email = c2.text_input("Email address *")
        phone = c1.text_input("Mobile number *")
        college = c2.text_input("College / University")
        branch = c1.selectbox("Engineering branch", ["Select","CSE","AI & ML","AI & DS","ISE","ECE","EEE","Other"])
        year = c2.selectbox("Current year", ["Select","Pre-final year","Final year","Recent graduate","Other"])
        cgpa = c1.text_input("CGPA / Percentage")
        program = c2.selectbox("Program of interest", [
            "6-Month Online AI Engineering Program",
            "Data Science & AI",
            "Generative AI & Agentic AI",
            "Other / Need counselling"
        ])
        message = st.text_area("Your question / preferred time to contact")
        consent = st.checkbox("I agree that PragyanAI may contact me about this enquiry. *")
        submit = st.form_submit_button("Submit Expression of Interest", type="primary",
                                       use_container_width=True)
    if submit:
        if not name.strip() or not email.strip() or not phone.strip() or not consent:
            st.error("Please complete all required fields and provide consent.")
        elif "@" not in email or len(phone.strip()) < 8:
            st.error("Please enter a valid email address and mobile number.")
        else:
            lead = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "name":name.strip(),"email":email.strip(),"phone":phone.strip(),
                "college":college.strip(),"branch":branch,"year":year,"cgpa":cgpa.strip(),
                "program":program,"message":message.strip(),"consent":"Yes"
            }
            destination = save_lead(lead)
            st.success(f"Thank you, {name}. Your enquiry has been submitted.")
            st.caption(f"Lead saved to: {destination}")
    google_form = get_setting("GOOGLE_FORM_URL")
    if google_form:
        st.markdown("Or submit through the [PragyanAI Google Form](" + google_form + ").")

# 5. Testimonials and Google review links
with tabs[4]:
    st.markdown('<div class="section-title">What Customers & Students Say</div>',
                unsafe_allow_html=True)
    st.write("Selected feedback reproduced from the PragyanAI program brochure.")
    st.markdown("#### Student feedback")
    with st.container(border=True):
        st.markdown("**Akshata – ECE background, Lingraj Appa Engineering College, Bidar**")
        st.write(
            "Akshata describes completing the 10-month online course covering Python, machine learning, "
            "deep learning and data visualization, and credits the structured practical learning and "
            "mentorship with helping her secure a Junior AI Engineer position at SynthLinx."
        )
    with st.container(border=True):
        st.markdown("**Isharani – Guru Nanak Dev Engineering College, Bidar**")
        st.write(
            "Isharani describes training in Python, machine learning, deep learning and web development "
            "using Streamlit, along with hands-on projects and internship experience. She reports securing "
            "a Junior AI Engineer position at SynthLinx Private Limited."
        )
    st.markdown("#### Industry feedback")
    with st.container(border=True):
        st.markdown("**SynthLinx – Letter of Appreciation**")
        st.write(
            "The brochure includes a company appreciation letter recognizing PragyanAI graduates’ "
            "training and contribution in Data Science, Machine Learning, Deep Learning and Generative AI."
        )
    st.caption("Source: PragyanAI program brochure, student testimonials and company feedback pages.")
    review_url = get_setting("GOOGLE_REVIEW_URL")
    business_url = get_setting("GOOGLE_BUSINESS_PROFILE_URL")
    if review_url:
        st.link_button("Read PragyanAI Google Reviews", review_url)
    else:
        st.info("Google Review link has not been configured yet. Add GOOGLE_REVIEW_URL in Streamlit Secrets.")
    if business_url:
        st.link_button("Open PragyanAI Google Business Profile", business_url)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#6b6280;font-size:13px'>"
    "© PragyanAI · Pragyan SmartAI Technology LLP · Grow with Gyan · "
    "<a href='https://pragyanai.com' target='_blank'>pragyanai.com</a></div>",
    unsafe_allow_html=True
)