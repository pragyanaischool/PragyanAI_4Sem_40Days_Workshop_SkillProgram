import fitz
import base64
import streamlit as st

def pdf_to_text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append(f"[Brochure page {i+1}]\n{text}")
    doc.close()
    return "\n\n".join(pages)

def render_flipbook(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(1.1, 1.1), alpha=False)
        encoded = base64.b64encode(pix.tobytes("jpg")).decode("utf-8")
        pages.append(f'<div class="page"><img src="data:image/jpeg;base64,{encoded}" /></div>')
    doc.close()
    page_count = len(pages)
    html_pages = "\n".join(pages)
    component_html = f"""
    <div id="flipbook-shell">
      <div class="toolbar">
        <button id="prev">← Previous</button>
        <span id="counter">Page 1 / {page_count}</span>
        <button id="next">Next →</button>
      </div>
      <div id="flipbook">{html_pages}</div>
      <div class="hint">Use Previous / Next or swipe to turn pages.</div>
    </div>
    <style>
      #flipbook-shell{{font-family:Arial,sans-serif;background:#f3efff;border-radius:16px;padding:14px;}}
      .toolbar{{display:flex;justify-content:center;align-items:center;gap:18px;margin-bottom:12px;}}
      .toolbar button{{border:0;background:#43118a;color:#fff;border-radius:9px;padding:9px 16px;font-weight:700;cursor:pointer;}}
      #counter{{font-weight:700;color:#32106e;}}
      .page{{background:white;display:flex;align-items:center;justify-content:center;overflow:hidden;}}
      .page img{{width:100%;height:100%;object-fit:contain;}}
      .hint{{text-align:center;color:#5b5570;font-size:12px;margin-top:9px;}}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.min.js"></script>
    <script>
      const bookEl=document.getElementById('flipbook');
      const pageNodes=Array.from(bookEl.children);
      const width=Math.min(460, Math.floor(window.innerWidth*0.42));
      const pageFlip=new St.PageFlip(bookEl,{{
        width:width,height:Math.round(width*1.414),size:'stretch',
        minWidth:280,maxWidth:600,minHeight:390,maxHeight:850,
        maxShadowOpacity:0.35,showCover:true,mobileScrollSupport:false,usePortrait:true
      }});
      pageFlip.loadFromHTML(pageNodes);
      const counter=document.getElementById('counter');
      function update(){{counter.textContent='Page '+(pageFlip.getCurrentPageIndex()+1)+' / {page_count}';}}
      pageFlip.on('flip',update);
      document.getElementById('prev').onclick=()=>pageFlip.flipPrev();
      document.getElementById('next').onclick=()=>pageFlip.flipNext();
      update();
    </script>
    """
    st.components.v1.html(component_html, height=720, scrolling=False)