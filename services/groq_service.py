from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.config import get_setting

def build_llm():
    api_key = get_setting("GROQ_API_KEY")
    if not api_key:
        return None
    return ChatGroq(
        api_key=api_key,
        model=get_setting("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=0.2,
        max_tokens=900
    )

def answer_from_brochure(question, vector_store):
    llm = build_llm()
    if llm is None:
        return ("The AI chatbot is not configured yet. Add GROQ_API_KEY in your .env file "
                "or Streamlit Secrets. You can still browse the brochure and FAQs.")
    docs = vector_store.similarity_search(question, k=5)
    context = "\n\n".join(
        f"[{d.metadata.get('source')} | page {d.metadata.get('page')}]\n{d.page_content}"
        for d in docs
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the PragyanAI program information assistant.
Answer using only the supplied brochure and flyer context. Do not invent facts, admission guarantees,
placement promises, fees or schedules. If the context does not specify the answer, say so and direct
the student to +91 97410 07422 or sateesh.ambesange@pragyanai.com.
Mention the brochure page or flyer when useful.
Context:
{context}"""),
        ("human", "{question}")
    ])
    return (prompt | llm | StrOutputParser()).invoke({"context": context, "question": question})