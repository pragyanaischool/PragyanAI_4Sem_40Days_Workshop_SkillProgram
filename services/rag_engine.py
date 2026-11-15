import streamlit as st
import fitz
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

FLYER_KNOWLEDGE = """
PRAGYANAI 6-MONTH INDUSTRY-INTEGRATED AI ENGINEERING PROGRAM.
Project-Based Learning, Online Live Instructor-Led.
Duration 6 months (24 active weeks), 216 live training hours, 72 sessions.
Eight technical skill areas: Python and Data Engineering; Data Science and Business Intelligence;
Advanced Machine Learning; Deep Learning and Computer Vision; Natural Language Processing;
Generative AI, LLMs and RAG; Agentic AI and Multi-Agent Systems; MLOps and AI Product Engineering.
40 projects (32 guided and 8 independent), 3 research papers and 1 integrated AI product.
Learning methodology: 20% concepts and architecture, 80% practical implementation.
Eligibility: pre-final-year and final-year engineering students, basic Python knowledge, CGPA 7+.
Flyer pricing: ₹15,000 per candidate for 50+ enrolments; ₹25,000 per candidate for fewer than 50.
Contact: +91 97410 07422; sateesh.ambesange@pragyanai.com; pragyanai.com.
Founder & CEO Sateesh Ambesange: NITK alumnus; 25+ years product experience, technology leadership
and serial entrepreneurship; Stanford Ignite / Seed Spark; IIMA Business Strategy Communication;
SLP Fellow; industry experience includes Intel, Samsung, Philips and SanDisk.
"""

@st.cache_resource(show_spinner="Preparing the brochure knowledge base…")
def create_vector_store(pdf_bytes):
    docs = []
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page_no, page in enumerate(pdf, start=1):
        page_text = page.get_text("text").strip()
        if page_text:
            docs.append(Document(page_content=page_text,
                                 metadata={"source": "Program brochure", "page": page_no}))
    pdf.close()
    docs.append(Document(page_content=FLYER_KNOWLEDGE,
                         metadata={"source": "Program flyer", "page": "Flyer"}))
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=140)
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    return FAISS.from_documents(chunks, embeddings)