# PragyanAI Interactive AI Program Portal

## Main navigation (requested order)
1. Flyer & Introduction — program intro, key highlights, Sateesh Ambesange profile and LinkedIn links.
2. Program Flipbook — interactive page-turn view of the supplied program PDF.
3. Ask Chatbot — basic FAQ plus free-text RAG questions using LangChain, FAISS and Groq.
4. Expression of Interest — student enquiry form with optional Google Sheets persistence.
5. What Customers Say — selected brochure testimonials and configurable Google Review links.

## Structure
```text
pragyanai-interactive-ai-program/
├── .streamlit/
│   └── secrets.toml.example
├── assets/
│   ├── pragyanai_ai_engineering_brochure.pdf
│   └── pragyanai_program_flyer.png
├── components/
│   ├── __init__.py
│   └── header.py
├── data/
│   └── faq.json
├── services/
│   ├── __init__.py
│   ├── groq_service.py
│   ├── lead_service.py
│   └── rag_engine.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   └── pdf_utils.py
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```
Set `GROQ_API_KEY` in `.env`, then run:
```bash
streamlit run app.py
```

## Streamlit Cloud secrets
```toml
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "llama-3.3-70b-versatile"
GOOGLE_FORM_URL = ""
GOOGLE_REVIEW_URL = ""
GOOGLE_BUSINESS_PROFILE_URL = ""
```

For persistent leads, configure `GOOGLE_SHEET_ID` and `GOOGLE_SERVICE_ACCOUNT_JSON`.
Without Google Sheets, local development saves leads to `leads.csv`; Streamlit Cloud local storage is ephemeral.

## Links already configured
- Sateesh Ambesange LinkedIn: https://www.linkedin.com/in/sateesh-ambesange-3020185/
- PragyanAI LinkedIn company page: https://www.linkedin.com/company/pragyan-smartai-technology-llp/

## Google Reviews
The exact PragyanAI Google review URL was not present in the supplied materials. Add it as `GOOGLE_REVIEW_URL` in Streamlit Secrets; the app will show the review button when configured.
