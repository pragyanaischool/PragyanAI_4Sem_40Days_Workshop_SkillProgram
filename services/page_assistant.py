
"""
PragyanAI - Page Assistant
=================================================
AI-powered PDF page assistant.

Features:
1. Translate extracted PDF page text.
2. Generate educational explanations.
3. Generate concise page summaries.
4. Support multiple languages.
5. Integrate with Groq API.

Used by:
    utils/pdf_utils.py

Required configuration:
    GROQ_API_KEY
    GROQ_MODEL

Streamlit secrets:
    .streamlit/secrets.toml
"""

import os
import streamlit as st

from groq import Groq


# =================================================
# 1. CONFIGURATION
# =================================================

DEFAULT_MODEL = "llama-3.3-70b-versatile"

DEFAULT_MAX_TOKENS = 4000

MAX_INPUT_CHARACTERS = 18000

TRANSLATION_TEMPERATURE = 0.2

EXPLANATION_TEMPERATURE = 0.4

SUMMARY_TEMPERATURE = 0.2


# =================================================
# 2. SUPPORTED LANGUAGES
# =================================================

SUPPORTED_LANGUAGES = {
    "English": "English",
    "Hindi": "Hindi",
    "Kannada": "Kannada",
    "Telugu": "Telugu",
    "Tamil": "Tamil",
    "Malayalam": "Malayalam",
    "Marathi": "Marathi",
    "Bengali": "Bengali",
    "Gujarati": "Gujarati",
    "Punjabi": "Punjabi",
    "Urdu": "Urdu",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Arabic": "Arabic",
    "Japanese": "Japanese",
    "Chinese (Mandarin)": "Chinese (Mandarin)",
}


# =================================================
# 3. SETTINGS MANAGEMENT
# =================================================

def get_setting(key, default=None):
    """
    Retrieve a configuration value.

    Priority:
        1. Streamlit secrets
        2. Environment variables
        3. Default value
    """

    try:
        value = st.secrets.get(key)

        if value is not None and str(value).strip():
            return value

    except Exception:
        pass

    return os.getenv(key, default)


def get_groq_api_key():
    """
    Retrieve Groq API key.
    """

    api_key = get_setting("GROQ_API_KEY")

    if not api_key:

        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Configure it in .streamlit/secrets.toml "
            "or your environment variables."
        )

    return api_key


def get_groq_model():
    """
    Retrieve configured Groq model.
    """

    return get_setting(
        "GROQ_MODEL",
        DEFAULT_MODEL
    )


# =================================================
# 4. GROQ CLIENT
# =================================================

def get_groq_client():
    """
    Initialize and cache Groq client.

    Cache is cleared automatically when the Streamlit
    application restarts.
    """

    return _get_cached_groq_client(
        get_groq_api_key()
    )


@st.cache_resource(show_spinner=False)
def _get_cached_groq_client(api_key):
    """
    Create a cached Groq client.

    The API key is a cache argument, so changing
    the key creates a new client.
    """

    return Groq(
        api_key=api_key
    )


# =================================================
# 5. TEXT VALIDATION
# =================================================

def validate_page_text(page_text):
    """
    Validate and clean extracted PDF text.

    Args:
        page_text: Text extracted from PDF.

    Returns:
        str: Cleaned page text.
    """

    if page_text is None:

        raise ValueError(
            "Page text is empty."
        )

    if not isinstance(page_text, str):

        raise ValueError(
            "Page text must be a string."
        )

    cleaned_text = page_text.strip()

    if not cleaned_text:

        raise ValueError(
            "No text was extracted from this PDF page."
        )

    if len(cleaned_text) > MAX_INPUT_CHARACTERS:

        cleaned_text = (
            cleaned_text[:MAX_INPUT_CHARACTERS]
            + "\n\n[Remaining content omitted due to length.]"
        )

    return cleaned_text


# =================================================
# 6. COMMON GROQ RESPONSE GENERATOR
# =================================================

def generate_ai_response(
    system_prompt,
    user_prompt,
    temperature=0.3,
    max_tokens=DEFAULT_MAX_TOKENS
):
    """
    Generate an AI response using Groq.

    Args:
        system_prompt: System instructions.
        user_prompt: User request and source content.
        temperature: Model temperature.
        max_tokens: Maximum response tokens.

    Returns:
        str: AI-generated response.
    """

    if not system_prompt or not user_prompt:

        raise ValueError(
            "System prompt and user prompt are required."
        )

    client = get_groq_client()

    model = get_groq_model()

    try:

        response = client.chat.completions.create(

            model=model,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=temperature,

            max_tokens=max_tokens

        )

        if not response.choices:

            raise RuntimeError(
                "Groq returned no response choices."
            )

        result = response.choices[0].message.content

        if not result:

            raise RuntimeError(
                "Groq returned an empty response."
            )

        return result.strip()

    except Exception as error:

        raise RuntimeError(
            f"Groq API request failed: {error}"
        ) from error


# =================================================
# 7. PAGE TRANSLATION
# =================================================

def translate_page_text(
    page_text,
    language="English"
):
    """
    Translate selected PDF page content.

    Args:
        page_text: Extracted PDF page text.
        language: Target language.

    Returns:
        str: Translated page content.
    """

    if language not in SUPPORTED_LANGUAGES.values():

        raise ValueError(
            f"Unsupported language: {language}"
        )

    cleaned_text = validate_page_text(
        page_text
    )

    system_prompt = f"""
You are a professional multilingual translator
working for PragyanAI.

Translate educational and technical PDF content
into {language}.

TRANSLATION INSTRUCTIONS:

1. Translate the complete supplied content.
2. Preserve the original meaning.
3. Maintain technical accuracy.
4. Preserve headings and subheadings.
5. Preserve numbered lists and bullet points.
6. Preserve mathematical equations and formulas.
7. Keep programming languages unchanged.
8. Keep software names and framework names unchanged.
9. Preserve product names and organization names.
10. Do not add unsupported information.
11. Do not summarize the source content.
12. Do not omit important details.
13. Use natural and readable {language}.

TECHNICAL TERMINOLOGY:

Retain commonly used English technical terminology
where translating it would reduce clarity.

Return only the translated content in {language}.
"""

    user_prompt = f"""
Translate the following PDF page into {language}.

SOURCE PAGE CONTENT:

{cleaned_text}

END OF SOURCE CONTENT.
"""

    return generate_ai_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=TRANSLATION_TEMPERATURE,
        max_tokens=DEFAULT_MAX_TOKENS
    )


# =================================================
# 8. EDUCATIONAL PAGE EXPLANATION
# =================================================

def explain_page(
    page_text,
    language="English"
):
    """
    Generate an educational explanation of a PDF page.

    The explanation is intended for:
        1. Students
        2. Working professionals
        3. Audio Book playback

    Args:
        page_text: Extracted PDF page text.
        language: Explanation language.

    Returns:
        str: Detailed educational explanation.
    """

    if language not in SUPPORTED_LANGUAGES.values():

        raise ValueError(
            f"Unsupported language: {language}"
        )

    cleaned_text = validate_page_text(
        page_text
    )

    system_prompt = f"""
You are an experienced AI Engineering educator
and technical instructor at PragyanAI.

Your responsibility is to explain educational
content to engineering students and professionals.

Explain the supplied PDF page in {language}.

FOLLOW THESE INSTRUCTIONS:

1. Begin with a short introduction.
2. Explain the main topic.
3. Explain important concepts.
4. Explain technical terminology.
5. Explain tools and frameworks mentioned.
6. Explain workflows when supported by the source.
7. Give practical examples where useful.
8. Explain why the topic is important.
9. Finish with a short key takeaway.

SOURCE ACCURACY:

1. Follow the supplied page content.
2. Do not invent program features.
3. Do not invent fees or placement claims.
4. Do not invent partnerships or certifications.
5. Do not introduce unsupported facts.
6. Clearly distinguish general examples from source facts.

AUDIO BOOK STYLE:

1. Write in natural spoken language.
2. Use short, understandable sentences.
3. Avoid Markdown tables.
4. Avoid excessive symbols.
5. Use clear transitions between topics.
6. Expand abbreviations when appropriate.
7. Make the explanation suitable for listening.

Write the entire explanation in {language}.
"""

    user_prompt = f"""
Explain the following selected page from the
PragyanAI AI Engineering Program brochure.

The explanation will be used as an educational
audio lesson for students.

PAGE CONTENT:

{cleaned_text}

END OF PAGE CONTENT.
"""

    return generate_ai_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=EXPLANATION_TEMPERATURE,
        max_tokens=3000
    )


# =================================================
# 9. PAGE SUMMARY
# =================================================

def summarize_page(
    page_text,
    language="English"
):
    """
    Generate a concise summary of a selected PDF page.

    Args:
        page_text: Extracted PDF page text.
        language: Summary language.

    Returns:
        str: Page summary.
    """

    if language not in SUPPORTED_LANGUAGES.values():

        raise ValueError(
            f"Unsupported language: {language}"
        )

    cleaned_text = validate_page_text(
        page_text
    )

    system_prompt = f"""
You are an educational content summarization assistant.

Summarize the supplied PDF page in {language}.

REQUIREMENTS:

1. Identify the main topic.
2. Include important concepts.
3. Preserve important technical terminology.
4. Use clear bullet points.
5. Keep the summary concise.
6. Do not invent information.
7. Do not change the meaning of the source.
8. Do not introduce unrelated topics.

Return the summary in {language}.
"""

    user_prompt = f"""
Summarize the following PDF page:

{cleaned_text}
"""

    return generate_ai_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=SUMMARY_TEMPERATURE,
        max_tokens=1200
    )


# =================================================
# 10. STREAMLIT ERROR HANDLING
# =================================================

def safe_translate_page_text(
    page_text,
    language="English"
):
    """
    Translate page content with Streamlit error handling.

    Returns:
        str or None
    """

    try:

        with st.spinner(
            f"Translating page into {language}..."
        ):

            return translate_page_text(
                page_text,
                language
            )

    except Exception as error:

        st.error(
            f"Translation failed: {error}"
        )

        return None


def safe_explain_page(
    page_text,
    language="English"
):
    """
    Generate page explanation with error handling.

    Returns:
        str or None
    """

    try:

        with st.spinner(
            "Generating AI page explanation..."
        ):

            return explain_page(
                page_text,
                language
            )

    except Exception as error:

        st.error(
            f"Explanation generation failed: {error}"
        )

        return None


def safe_summarize_page(
    page_text,
    language="English"
):
    """
    Generate page summary with error handling.

    Returns:
        str or None
    """

    try:

        with st.spinner(
            "Generating page summary..."
        ):

            return summarize_page(
                page_text,
                language
            )

    except Exception as error:

        st.error(
            f"Summary generation failed: {error}"
        )

        return None


# =================================================
# 11. API CONNECTION TEST
# =================================================

def test_groq_connection():
    """
    Test Groq API connectivity.

    Returns:
        tuple: (success, message)
    """

    try:

        response = generate_ai_response(

            system_prompt=(
                "You are a helpful assistant. "
                "Respond briefly."
            ),

            user_prompt=(
                "Reply with: PragyanAI Groq connection successful."
            ),

            temperature=0.1,

            max_tokens=50
        )

        return True, response

    except Exception as error:

        return False, str(error)


# =================================================
# 12. AVAILABLE LANGUAGE HELPER
# =================================================

def get_supported_languages():
    """
    Return supported language names for UI dropdowns.
    """

    return list(
        SUPPORTED_LANGUAGES.keys()
    )
