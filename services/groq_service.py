
"""
PragyanAI - Groq LLM Service
-----------------------------
Handles Groq API integration for the PragyanAI
AI Engineering Program brochure chatbot.

Main functions:
    get_groq_client()
    generate_response()
    answer_from_brochure()
    answer_with_history()

The service can work with retrieved brochure context
provided by rag_engine.py.
"""

import os
import streamlit as st

from groq import Groq


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

DEFAULT_MODEL = "llama-3.3-70b-versatile"

DEFAULT_TEMPERATURE = 0.3

DEFAULT_MAX_TOKENS = 2000

MAX_CONTEXT_CHARACTERS = 25000

MAX_HISTORY_MESSAGES = 10


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

def get_setting(key, default=None):
    """
    Read settings from Streamlit secrets first,
    then environment variables.
    """

    try:
        value = st.secrets.get(key)

        if value is not None and str(value).strip():
            return value

    except Exception:
        pass

    return os.getenv(key, default)


def get_api_key():
    """
    Retrieve Groq API key.
    """

    api_key = get_setting("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Configure it in .streamlit/secrets.toml "
            "or as an environment variable."
        )

    return api_key


def get_model_name():
    """
    Retrieve configured Groq model.
    """

    return get_setting(
        "GROQ_MODEL",
        DEFAULT_MODEL
    )


# ---------------------------------------------------------
# GROQ CLIENT
# ---------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_groq_client():
    """
    Initialize and cache the Groq client.

    Streamlit caches the client so it does not need
    to be recreated for every chatbot interaction.
    """

    return Groq(
        api_key=get_api_key()
    )


# ---------------------------------------------------------
# TEXT VALIDATION
# ---------------------------------------------------------

def validate_question(question):
    """
    Validate chatbot question.
    """

    if not isinstance(question, str):
        raise ValueError(
            "Question must be a string."
        )

    question = question.strip()

    if not question:
        raise ValueError(
            "Please enter a question."
        )

    return question


def prepare_context(context):
    """
    Prepare retrieved brochure context.
    """

    if context is None:
        return ""

    if isinstance(context, list):
        context = "\n\n".join(
            str(item) for item in context
        )

    elif not isinstance(context, str):
        context = str(context)

    context = context.strip()

    if len(context) > MAX_CONTEXT_CHARACTERS:
        context = context[:MAX_CONTEXT_CHARACTERS]

    return context


# ---------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------

def get_system_prompt():
    """
    System instructions for the PragyanAI chatbot.
    """

    return """
You are the official AI Program Information Assistant
for PragyanAI.

You help prospective students, parents, working
professionals and academic institutions understand
the PragyanAI AI Engineering Program.

YOUR RESPONSIBILITIES:

1. Answer questions about the program using the
   supplied brochure context.
2. Explain the curriculum, modules, projects,
   learning methodology and program structure.
3. Explain technical concepts in a student-friendly way.
4. Help users understand eligibility and program details.
5. Answer questions about PragyanAI and its founder
   only when supported by the supplied context.
6. Provide clear and professional responses.

SOURCE ACCURACY RULES:

1. Treat the supplied brochure context as the primary
   source of truth.
2. Do not invent fees, discounts, placement guarantees,
   salaries, job offers, admission deadlines or eligibility.
3. If the requested information is not available in the
   supplied context, clearly say that it is not specified
   in the available brochure information.
4. Do not make unsupported promises.
5. Do not claim that a student is guaranteed a job.
6. Do not invent company partnerships or accreditation.
7. Distinguish information stated in the brochure from
   general educational explanations.

RESPONSE STYLE:

1. Use simple, professional language.
2. Use headings and bullet points when useful.
3. Explain technical topics with practical examples.
4. Avoid unnecessarily long answers.
5. Be helpful and conversational.
6. Do not repeat the same information unnecessarily.

PROGRAM IDENTITY:

Organization: PragyanAI
Program: AI Engineering Program
Website: https://pragyanai.com

If a user asks for additional information that is not
available in the brochure, suggest contacting PragyanAI
through its official website.
"""


# ---------------------------------------------------------
# CORE GROQ RESPONSE GENERATOR
# ---------------------------------------------------------

def generate_response(
    question,
    context="",
    chat_history=None,
    temperature=DEFAULT_TEMPERATURE,
    max_tokens=DEFAULT_MAX_TOKENS
):
    """
    Generate a response using Groq.

    Args:
        question: User's question.
        context: Retrieved brochure content.
        chat_history: Previous conversation messages.
        temperature: LLM temperature.
        max_tokens: Maximum output tokens.

    Returns:
        str: Generated answer.
    """

    question = validate_question(question)

    context = prepare_context(context)

    client = get_groq_client()

    model = get_model_name()

    system_prompt = get_system_prompt()

    if context:

        context_message = f"""
The following information was retrieved from
the PragyanAI program brochure.

Use this information as the primary source
for answering the user's question.

<BROCHURE_CONTEXT>
{context}
</BROCHURE_CONTEXT>

Important:
If the answer is not present in the brochure context,
do not guess or fabricate it.
"""

    else:

        context_message = """
No brochure context was supplied.

Do not claim that you have verified any specific
program details from the brochure.

You may explain general AI and technology concepts,
but clearly distinguish general knowledge from
PragyanAI-specific information.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "system",
            "content": context_message
        }
    ]

    # -----------------------------------------------------
    # ADD CONVERSATION HISTORY
    # -----------------------------------------------------

    if chat_history:

        history = chat_history[
            -MAX_HISTORY_MESSAGES:
        ]

        for item in history:

            if not isinstance(item, dict):
                continue

            role = item.get("role")

            content = item.get("content")

            if (
                role in ["user", "assistant"]
                and isinstance(content, str)
                and content.strip()
            ):

                messages.append({
                    "role": role,
                    "content": content.strip()
                })

    # -----------------------------------------------------
    # ADD CURRENT QUESTION
    # -----------------------------------------------------

    messages.append({
        "role": "user",
        "content": question
    })

    # -----------------------------------------------------
    # GROQ API REQUEST
    # -----------------------------------------------------

    try:

        response = client.chat.completions.create(

            model=model,

            messages=messages,

            temperature=temperature,

            max_tokens=max_tokens

        )

        answer = (
            response.choices[0]
            .message.content
        )

        if not answer:
            raise RuntimeError(
                "Groq returned an empty response."
            )

        return answer.strip()

    except Exception as error:

        raise RuntimeError(
            f"Groq response generation failed: {error}"
        ) from error


# ---------------------------------------------------------
# BROCHURE QUESTION ANSWERING
# ---------------------------------------------------------

def answer_from_brochure(
    question,
    vector_store=None,
    chat_history=None
):
    """
    Answer a user question using brochure context.

    Args:
        question: User question.
        vector_store: FAISS or compatible LangChain vector store.
        chat_history: Previous conversation messages.

    Returns:
        str: AI-generated answer.

    Note:
        If vector_store is None, the response is generated
        without retrieved brochure context.
    """

    question = validate_question(question)

    retrieved_context = ""

    # -----------------------------------------------------
    # RETRIEVE BROCHURE INFORMATION
    # -----------------------------------------------------

    if vector_store is not None:

        try:

            documents = vector_store.similarity_search(
                question,
                k=5
            )

            retrieved_context = "\n\n".join(
                document.page_content
                for document in documents
                if getattr(document, "page_content", None)
            )

        except Exception as error:

            raise RuntimeError(
                f"Brochure information retrieval failed: {error}"
            ) from error

    # -----------------------------------------------------
    # GENERATE ANSWER
    # -----------------------------------------------------

    return generate_response(
        question=question,
        context=retrieved_context,
        chat_history=chat_history,
        temperature=DEFAULT_TEMPERATURE,
        max_tokens=DEFAULT_MAX_TOKENS
    )


# ---------------------------------------------------------
# CHAT WITH EXPLICIT RETRIEVED CONTEXT
# ---------------------------------------------------------

def answer_with_context(
    question,
    context,
    chat_history=None
):
    """
    Generate an answer from explicitly supplied context.

    Useful when rag_engine.py performs retrieval separately.
    """

    return generate_response(
        question=question,
        context=context,
        chat_history=chat_history
    )


# ---------------------------------------------------------
# CONVERSATION HISTORY HELPER
# ---------------------------------------------------------

def add_message_to_history(
    role,
    content
):
    """
    Add a conversation message to Streamlit session state.
    """

    if role not in ["user", "assistant"]:
        raise ValueError(
            "Role must be user or assistant."
        )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.session_state.chat_history.append({
        "role": role,
        "content": content
    })

    # Keep recent messages only.
    st.session_state.chat_history = (
        st.session_state.chat_history[
            -MAX_HISTORY_MESSAGES:
        ]
    )


# ---------------------------------------------------------
# RESET CHAT HISTORY
# ---------------------------------------------------------

def clear_chat_history():
    """
    Clear chatbot conversation history.
    """

    st.session_state.chat_history = []


# ---------------------------------------------------------
# STREAMLIT CHAT INTERFACE HELPER
# ---------------------------------------------------------

def get_chat_history():
    """
    Return existing chat history.
    """

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    return st.session_state.chat_history
