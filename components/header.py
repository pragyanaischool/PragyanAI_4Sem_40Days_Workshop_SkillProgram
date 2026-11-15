import streamlit as st

def render_header():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: Inter, sans-serif; }
    .block-container { padding-top: 1.2rem; max-width: 1400px; }
    .hero { background:linear-gradient(115deg,#17094c,#3d087d 58%,#101c65); color:white;
            border-radius:22px; padding:28px 30px; border:1px solid #6d42bd; }
    .hero h1 {font-size:2.15rem; margin:0 0 8px 0; font-weight:800;}
    .hero p {font-size:1.08rem; margin:0; opacity:.95;}
    .pill {display:inline-block;background:#ff6b00;color:white;padding:6px 12px;
           border-radius:20px;font-weight:700;margin:8px 6px 0 0;font-size:.85rem;}
    .metric {background:#f7f4ff;border:1px solid #e2d6ff;padding:14px;border-radius:14px;text-align:center;}
    .metric strong {display:block;font-size:1.7rem;color:#4a1289;}
    .section-title {font-size:1.45rem;font-weight:800;color:#32106e;margin:10px 0;}
    </style>
    <div class="hero">
      <h1>PRAGYAN AI · Grow with Gyan</h1>
      <p>Engineering the Complete AI Professional</p>
      <span class="pill">6-Month AI Engineering Program</span>
      <span class="pill">Project-Based Learning</span>
      <span class="pill">Online Live Instructor-Led</span>
    </div>
    """, unsafe_allow_html=True)