
import json
from pathlib import Path

import streamlit as st

# --------------------------------------------------
# 1. IMPORT PROJECT MODULES
# --------------------------------------------------

from components.header import render_header
from components.google_form import render_google_eoi_form

from utils.pdf_utils import render_flipbook
from utils.config import get_setting

from services.rag_engine import create_vector_store
from services.groq_service import answer_from_brochure


# --------------------------------------------------
# 2. APPLICATION CONFIGURATION
# --------------------------------------------------

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"

DEFAULT_PDF = (
    ASSETS / "pragyanai_ai_engineering_brochure.pdf"
)

DEFAULT_FLYER = (
    ASSETS / "pragyanai_program_flyer.png"
)

LINKEDIN_PROFILE = (
    "https://www.linkedin.com/in/"
    "sateesh-ambesange-3020185/"
)

LINKEDIN_COMPANY = (
    "https://www.linkedin.com/company/"
    "pragyan-smartai-technology-llp/"
)

st.set_page_config(
    page_title="PragyanAI | AI Engineering Program",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# 3. HEADER
# --------------------------------------------------

render_header()


# --------------------------------------------------
# 4. SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.image(
        str(DEFAULT_FLYER),
        use_container_width=True
    )

    st.markdown("## PragyanAI Program Portal")

    st.markdown("---")

    st.markdown("### Upload Program Materials")

    uploaded_pdf = st.file_uploader(
        "Upload / Replace Program PDF",
        type=["pdf"]
    )

    uploaded_flyer = st.file_uploader(
        "Upload / Replace Program Flyer",
        type=["png", "jpg", "jpeg"]
    )

    st.markdown("---")

    st.markdown("### Contact PragyanAI")

    st.write("☎ +91 97410 07422")

    st.write(
        "✉ sateesh.ambesange@pragyanai.com"
    )

    st.write("🌐 pragyanai.com")

    st.markdown("---")

    st.caption(
        "Pragyan SmartAI Technology LLP"
    )


# --------------------------------------------------
# 5. LOAD PDF
# --------------------------------------------------

if uploaded_pdf:

    pdf_bytes = uploaded_pdf.getvalue()

elif DEFAULT_PDF.exists():

    pdf_bytes = DEFAULT_PDF.read_bytes()

else:

    st.error(
        "Program PDF not found. "
        "Please upload the brochure."
    )

    st.stop()


# --------------------------------------------------
# 6. BUILD RAG KNOWLEDGE BASE
# --------------------------------------------------

with st.spinner(
    "Preparing PragyanAI knowledge base..."
):

    vector_store = create_vector_store(
        pdf_bytes
    )


# --------------------------------------------------
# 7. MAIN NAVIGATION
# --------------------------------------------------

tabs = st.tabs([

    "1. Flyer & Introduction",

    "2. Program Flipbook",

    "3. Ask Chatbot",

    "4. Expression of Interest",

    "5. What Customers Say"

])


# ==================================================
# SECTION 1: FLYER & PROGRAM INTRODUCTION
# ==================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">'
        'Engineering the Complete AI Professional'
        '</div>',
        unsafe_allow_html=True
    )

    # Display flyer

    flyer = (
        uploaded_flyer
        if uploaded_flyer
        else DEFAULT_FLYER
    )

    if uploaded_flyer:

        st.image(
            uploaded_flyer,
            use_container_width=True
        )

    elif DEFAULT_FLYER.exists():

        st.image(
            str(DEFAULT_FLYER),
            use_container_width=True
        )

    st.markdown("---")

    # Program introduction

    st.markdown("## About the Program")

    st.write(
        """
        PragyanAI's 6-Month Industry-Integrated
        AI Engineering Program is an online,
        live instructor-led and project-based
        learning program.

        It is designed to help engineering students
        build practical AI engineering capabilities
        through structured learning, hands-on labs,
        real-world projects and AI product development.
        """
    )

    st.markdown("---")

    # Program metrics

    st.markdown("## Program at a Glance")

    col1, col2, col3, col4 = st.columns(4)

    metrics = [

        ("6 Months", "Program Duration"),

        ("216", "Live Training Hours"),

        ("72", "Live Sessions"),

        ("40", "Projects")

    ]

    for col, (value, label) in zip(
        [col1, col2, col3, col4],
        metrics
    ):

        col.markdown(
            f"""
            <div class="metric">
                <strong>{value}</strong>
                {label}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # Key highlights

    st.markdown("## Key Program Highlights")

    highlights = [

        "6 Months of structured online AI Engineering training",

        "216 hours of live instructor-led training",

        "72 online live sessions",

        "Eight technical skill areas",

        "40 Projects: 32 Guided + 8 Independent",

        "Three Research Papers",

        "One Integrated AI Product",

        "20% Concepts and Architecture + 80% Practical Implementation",

        "GitHub Portfolio and AI Application Development",

        "Real-world AI problem-solving experience"

    ]

    for item in highlights:

        st.markdown(f"✅ {item}")

    st.markdown("---")

    # Eight skill areas

    st.markdown("## Eight Technical Skill Areas")

    skills = [

        "Python & Data Engineering",

        "Data Science & Business Intelligence",

        "Advanced Machine Learning",

        "Deep Learning & Computer Vision",

        "Natural Language Processing",

        "Generative AI, LLMs & RAG",

        "Agentic AI & Multi-Agent Systems",

        "MLOps & AI Product Engineering"

    ]

    skill_columns = st.columns(4)

    for index, skill in enumerate(skills):

        with skill_columns[index % 4]:

            st.info(skill)

    st.markdown("---")

    # Founder profile

    st.markdown(
        "## Sateesh Ambesange"
    )

    st.markdown(
        "### Founder & CEO – PragyanAI"
    )

    col1, col2 = st.columns([1, 2])

    with col1:

        st.markdown("**NITK Alumni**")

        st.markdown("**25+ Years Experience**")

        st.caption(
            "Product Experience | Technology Leadership | Serial Entrepreneur"
        )

    with col2:

        st.write(
            """
            Stanford Ignite / Seed Spark

            IIMA – Business Strategy Communication

            SLP Fellow

            Industry experience includes Intel,
            Samsung, Philips and SanDisk.
            """
        )

        st.link_button(
            "View Sateesh Ambesange LinkedIn Profile",
            LINKEDIN_PROFILE
        )

        st.link_button(
            "Visit PragyanAI LinkedIn Company Page",
            LINKEDIN_COMPANY
        )

    st.markdown("---")

    st.markdown("### Contact PragyanAI")

    st.write("📞 +91 97410 07422")

    st.write(
        "📧 sateesh.ambesange@pragyanai.com"
    )

    st.write("🌐 https://pragyanai.com")


# ==================================================
# SECTION 2: INTERACTIVE PDF FLIPBOOK
# ==================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">'
        'Explore the Complete AI Engineering Program'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        Browse the PragyanAI program brochure
        using the interactive page-turn viewer.
        """
    )

    st.markdown("---")

    render_flipbook(pdf_bytes)


# ==================================================
# SECTION 3: AI CHATBOT + BASIC FAQ + RAG
# ==================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">'
        'Ask PragyanAI – AI Program Assistant'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        Have questions about our AI Engineering Program?

        Ask about curriculum, fees, eligibility,
        projects, training methodology and program details.
        """
    )

    st.markdown("---")

    # Basic FAQ

    st.markdown("## Frequently Asked Questions")

    faq_path = DATA / "faq.json"

    if faq_path.exists():

        with open(
            faq_path,
            "r",
            encoding="utf-8"
        ) as file:

            faq_items = json.load(file)

        for item in faq_items:

            with st.expander(item["q"]):

                st.write(item["a"])

    else:

        st.warning(
            "FAQ file not found: data/faq.json"
        )

    st.markdown("---")

    # RAG chatbot

    st.markdown("## Ask Your Own Question")

    st.caption(
        "Powered by LangChain + Groq + FAISS"
    )

    if "messages" not in st.session_state:

        st.session_state.messages = []

    # Display chat history

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # User question

    question = st.chat_input(
        "Ask anything about the PragyanAI program..."
    )

    if question:

        st.session_state.messages.append({

            "role": "user",

            "content": question

        })

        with st.chat_message("user"):

            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching the brochure..."
            ):

                try:

                    reply = answer_from_brochure(
                        question,
                        vector_store
                    )

                except Exception as error:

                    reply = (
                        "Unable to generate an answer. "
                        "Please check your Groq API configuration. "
                        f"Technical details: {error}"
                    )

            st.markdown(reply)

        st.session_state.messages.append({

            "role": "assistant",

            "content": reply

        })

    if st.button("Clear Chat History"):

        st.session_state.messages = []

        st.rerun()


# ==================================================
# SECTION 4: GOOGLE FORM – EXPRESSION OF INTEREST
# ==================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">'
        'Expression of Interest – Student Registration'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        Interested in becoming an AI Engineer?

        Fill out the PragyanAI Expression of Interest
        Google Form. Our team will contact you
        with program details and admission guidance.
        """
    )

    st.markdown("---")

    # Embedded Google Form component

    render_google_eoi_form()


# ==================================================
# SECTION 5: WHAT CUSTOMERS SAY
# ==================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">'
        'What Customers & Students Say'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        Explore student experiences and industry
        feedback about PragyanAI training programs.
        """
    )

    st.markdown("---")

    # Student testimonial 1

    st.markdown("## Student Testimonials")

    with st.container(border=True):

        st.markdown(
            "### Akshata"
        )

        st.caption(
            "ECE Background | Lingraj Appa Engineering College, Bidar"
        )

        st.write(
            """
            Akshata describes completing the online
            course covering Python, Machine Learning,
            Deep Learning and Data Visualization.

            She credits structured practical learning
            and mentorship with helping her secure
            a Junior AI Engineer position at SynthLinx.
            """
        )

    # Student testimonial 2

    with st.container(border=True):

        st.markdown(
            "### Isharani"
        )

        st.caption(
            "Guru Nanak Dev Engineering College, Bidar"
        )

        st.write(
            """
            Isharani describes training in Python,
            Machine Learning, Deep Learning and
            Web Development using Streamlit.

            She also describes hands-on projects
            and internship experience, and reports
            securing a Junior AI Engineer position
            at SynthLinx Private Limited.
            """
        )

    st.markdown("---")

    # Company feedback

    st.markdown("## Industry Feedback")

    with st.container(border=True):

        st.markdown(
            "### SynthLinx – Letter of Appreciation"
        )

        st.write(
            """
            The PragyanAI brochure includes a company
            appreciation letter recognizing graduates'
            training and contribution in Data Science,
            Machine Learning, Deep Learning and
            Generative AI.
            """
        )

    st.caption(
        "Source: PragyanAI program brochure, student testimonials "
        "and company feedback pages."
    )

    st.markdown("---")

    # Google reviews

    st.markdown("## Google Customer Reviews")

    review_url = get_setting(
        "GOOGLE_REVIEW_URL"
    )

    business_url = get_setting(
        "GOOGLE_BUSINESS_PROFILE_URL"
    )

    if review_url:

        st.link_button(
            "⭐ Read PragyanAI Google Reviews",
            review_url,
            use_container_width=True
        )

    else:

        st.info(
            "Configure GOOGLE_REVIEW_URL in "
            "Streamlit Secrets to display Google Reviews."
        )

    if business_url:

        st.link_button(
            "View PragyanAI Google Business Profile",
            business_url,
            use_container_width=True
        )


# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#6b6280;
        font-size:13px;
        padding:15px;
    ">
        © PragyanAI · Pragyan SmartAI Technology LLP

        <br>

        Grow with Gyan · Engineering the Complete AI Professional

        <br>

        <a href="https://pragyanai.com"
           target="_blank">
            www.pragyanai.com
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
