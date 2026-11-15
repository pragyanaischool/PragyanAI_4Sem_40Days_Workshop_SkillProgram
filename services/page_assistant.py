"""
PragyanAI - Page Assistant
=================================================
AI-powered PDF page assistant using the Groq API.

Features:
1. Translate extracted PDF page text.
2. Generate educational explanations.
3. Generate concise page summaries.
4. Support multiple languages.
5. Use Groq model configured through Streamlit Secrets or environment variables.
6. Support openai/gpt-oss-120b with model-appropriate request parameters.
7. Provide clear API-key, model, rate-limit and connectivity errors.

Used by:
    utils/pdf_utils.py
    services/speech_service.py

Required configuration:
    GROQ_API_KEY
    GROQ_MODEL

Recommended Streamlit secrets (.streamlit/secrets.toml):
    GROQ_API_KEY = "gsk_your_actual_key"
    GROQ_MODEL = "openai/gpt-oss-120b"
"""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    GROQ_IMPORT_ERROR = None
except Exception as import_error:
    Groq = None
    GROQ_AVAILABLE = False
    GROQ_IMPORT_ERROR = str(import_error)


# =================================================
# 1. CONFIGURATION
# =================================================

DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_MAX_TOKENS = 4000
MAX_INPUT_CHARACTERS = 18000

TRANSLATION_TEMPERATURE = 0.2
EXPLANATION_TEMPERATURE = 0.4
SUMMARY_TEMPERATURE = 0.2

DEFAULT_GROQ_TIMEOUT = 90
DEFAULT_GROQ_MAX_RETRIES = 2
DEFAULT_REASONING_EFFORT = "low"


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

def get_setting(key: str, default=None):
    """
    Read a setting in this order:
        1. Streamlit secrets
        2. Environment variables
        3. Supplied default

    Streamlit secrets may not exist during local development, so that
    lookup is deliberately protected.
    """
    try:
        value = st.secrets.get(key)
        if value is not None and str(value).strip():
            return value
    except Exception:
        pass

    value = os.getenv(key)
    if value is not None and str(value).strip():
        return value

    return default


def get_groq_api_key() -> str:
    """Retrieve and validate the Groq API key without exposing it."""
    api_key = get_setting("GROQ_API_KEY")

    if not api_key or not str(api_key).strip():
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to Streamlit Cloud → "
            "Manage app → Settings → Secrets, or set it as an environment "
            "variable for local development."
        )

    return str(api_key).strip()


def get_groq_model() -> str:
    """Return the configured Groq model, defaulting to GPT-OSS-120B."""
    model = get_setting("GROQ_MODEL", DEFAULT_MODEL)
    model = str(model).strip() if model is not None else DEFAULT_MODEL

    if not model:
        return DEFAULT_MODEL

    return model


def get_groq_reasoning_effort() -> str:
    """Return the reasoning effort used by compatible reasoning models."""
    effort = str(
        get_setting("GROQ_REASONING_EFFORT", DEFAULT_REASONING_EFFORT)
    ).strip().lower()

    if effort not in {"low", "medium", "high"}:
        return DEFAULT_REASONING_EFFORT

    return effort


# =================================================
# 4. GROQ CLIENT
# =================================================

def get_groq_client():
    """
    Initialize a cached Groq client.

    The API key is passed as a cache argument. If the key changes, Streamlit
    creates a new client. The key is never displayed in the UI or logs here.
    """
    if not GROQ_AVAILABLE:
        raise ImportError(
            "The Groq Python package is not installed. Add 'groq' to "
            "requirements.txt and redeploy. "
            f"Import details: {GROQ_IMPORT_ERROR}"
        )

    return _get_cached_groq_client(get_groq_api_key())


@st.cache_resource(show_spinner=False)
def _get_cached_groq_client(api_key: str):
    """Create the cached Groq client."""
    if not GROQ_AVAILABLE:
        raise ImportError(
            f"Groq package is unavailable: {GROQ_IMPORT_ERROR}"
        )

    return Groq(
        api_key=api_key,
        timeout=DEFAULT_GROQ_TIMEOUT,
        max_retries=DEFAULT_GROQ_MAX_RETRIES,
    )


# =================================================
# 5. TEXT VALIDATION
# =================================================

def validate_page_text(page_text: str) -> str:
    """
    Validate and clean extracted PDF text.

    Text longer than MAX_INPUT_CHARACTERS is truncated to protect the API
    request size. The marker makes that truncation visible to the model.
    """
    if page_text is None:
        raise ValueError("Page text is empty.")

    if not isinstance(page_text, str):
        raise ValueError("Page text must be a string.")

    cleaned_text = page_text.strip()

    if not cleaned_text:
        raise ValueError(
            "No text was extracted from this PDF page. "
            "The page may contain scanned images and require OCR."
        )

    if len(cleaned_text) > MAX_INPUT_CHARACTERS:
        marker = "\n\n[Remaining content omitted due to length.]"
        cleaned_text = (
            cleaned_text[: MAX_INPUT_CHARACTERS - len(marker)] + marker
        )

    return cleaned_text


def validate_language(language: str) -> str:
    """Validate a language name and return its display value."""
    if language not in SUPPORTED_LANGUAGES.values():
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.values())}"
        )
    return language


# =================================================
# 6. GROQ ERROR HANDLING
# =================================================

def _format_groq_error(error: Exception) -> str:
    """
    Convert common Groq API failures into actionable messages.

    The original error is retained in the message for debugging, but API
    credentials are never included.
    """
    message = str(error)
    lowered = message.lower()

    status_code = getattr(error, "status_code", None)

    if status_code == 401 or "invalid_api_key" in lowered or "invalid api key" in lowered:
        return (
            "Groq authentication failed (401: invalid API key). Verify that "
            "GROQ_API_KEY in Streamlit Secrets is a valid, active key from "
            "https://console.groq.com/keys. Do not put the key in source code. "
            f"Provider details: {message}"
        )

    if status_code == 403 or "permission" in lowered or "not authorized" in lowered:
        return (
            "Groq rejected the request because the key or account does not "
            "have permission to use this model. Check model access and "
            f"account status. Provider details: {message}"
        )

    if status_code == 404 or "model_not_found" in lowered or "model not found" in lowered:
        return (
            f"The configured Groq model '{get_groq_model()}' was not found "
            "or is unavailable to this account. Check GROQ_MODEL and the "
            f"Groq model catalogue. Provider details: {message}"
        )

    if status_code == 429 or "rate_limit" in lowered or "rate limit" in lowered:
        return (
            "Groq rate limit or quota reached. Wait before retrying, or check "
            f"your Groq usage and limits. Provider details: {message}"
        )

    if "timeout" in lowered or "timed out" in lowered:
        return (
            "The Groq request timed out. Try again, or reduce the amount of "
            f"PDF text being processed. Provider details: {message}"
        )

    if "max_completion_tokens" in lowered or "max_tokens" in lowered:
        return (
            "The Groq model rejected the token-limit parameter. Check that "
            "the configured model supports the request parameters. "
            f"Provider details: {message}"
        )

    return f"Groq API request failed: {message}"


# =================================================
# 7. COMMON GROQ RESPONSE GENERATOR
# =================================================

def generate_ai_response(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    model: Optional[str] = None,
) -> str:
    """
    Generate a response using Groq Chat Completions.

    GPT-OSS models use max_completion_tokens and reasoning_effort. The
    temperature parameter is intentionally omitted for GPT-OSS requests
    to avoid sending sampling controls that may not be supported by the
    selected reasoning model.

    Other configured Groq models receive temperature and
    max_completion_tokens.

    Args:
        system_prompt: System instructions.
        user_prompt: User request and source content.
        temperature: Sampling temperature for non-GPT-OSS models.
        max_tokens: Requested maximum completion token budget.
        model: Optional model override. Defaults to GROQ_MODEL.

    Returns:
        The generated response text.
    """
    if not isinstance(system_prompt, str) or not system_prompt.strip():
        raise ValueError("A non-empty system prompt is required.")

    if not isinstance(user_prompt, str) or not user_prompt.strip():
        raise ValueError("A non-empty user prompt is required.")

    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("max_tokens must be a positive integer.")

    client = get_groq_client()
    selected_model = str(model or get_groq_model()).strip()

    if not selected_model:
        raise ValueError("GROQ_MODEL is empty. Configure a valid Groq model.")

    request_args = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        # max_completion_tokens is the current completion token limit
        # parameter used for Groq Chat Completions.
        "max_completion_tokens": max_tokens,
    }

    if "gpt-oss" in selected_model.lower():
        request_args["reasoning_effort"] = get_groq_reasoning_effort()
    else:
        request_args["temperature"] = temperature

    try:
        response = client.chat.completions.create(**request_args)

        if not getattr(response, "choices", None):
            raise RuntimeError("Groq returned no response choices.")

        message = response.choices[0].message
        result = getattr(message, "content", None)

        if isinstance(result, list):
            # Some compatible APIs may return structured content blocks.
            result = "\n".join(
                str(block.get("text", ""))
                for block in result
                if isinstance(block, dict) and block.get("text")
            )

        if not result or not str(result).strip():
            finish_reason = getattr(response.choices[0], "finish_reason", None)
            raise RuntimeError(
                "Groq returned an empty response. "
                f"Finish reason: {finish_reason or 'not provided'}. "
                "If the response was cut off, increase the completion token "
                "budget or reduce the source text."
            )

        return str(result).strip()

    except Exception as error:
        raise RuntimeError(_format_groq_error(error)) from error


# =================================================
# 8. PAGE TRANSLATION
# =================================================

def translate_page_text(page_text: str, language: str = "English") -> str:
    """Translate selected PDF page content into the requested language."""
    validate_language(language)
    cleaned_text = validate_page_text(page_text)

    system_prompt = f"""
You are a professional multilingual translator working for PragyanAI.

Translate educational and technical PDF content into {language}.

TRANSLATION INSTRUCTIONS:
1. Translate all supplied content that fits within the source text.
2. Preserve the original meaning and technical accuracy.
3. Maintain headings and subheadings.
4. Preserve numbered lists and bullet points.
5. Preserve mathematical equations and formulas.
6. Keep programming languages, code, software names and framework names unchanged.
7. Preserve product names and organization names.
8. Do not add unsupported information.
9. Do not summarize the source content.
10. Do not omit important details.
11. Use natural and readable {language}.
12. Retain commonly used English technical terminology where translating it
    would reduce clarity.
13. Return only the translated content in {language}.
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
        max_tokens=DEFAULT_MAX_TOKENS,
    )


# =================================================
# 9. EDUCATIONAL PAGE EXPLANATION
# =================================================

def explain_page(page_text: str, language: str = "English") -> str:
    """
    Generate an educational explanation of a PDF page.

    The explanation is suitable for students, working professionals and
    audio narration.
    """
    validate_language(language)
    cleaned_text = validate_page_text(page_text)

    system_prompt = f"""
You are an experienced AI Engineering educator and technical instructor
at PragyanAI.

Explain the supplied PDF page in {language} for engineering students
and working professionals.

FOLLOW THESE INSTRUCTIONS:
1. Begin with a short introduction.
2. Explain the main topic.
3. Explain important concepts and technical terminology.
4. Explain tools and frameworks mentioned in the source.
5. Explain workflows when supported by the source.
6. Give practical examples where useful. Clearly label illustrative
   examples as examples, not as facts from the PDF.
7. Explain why the topic is important.
8. Finish with a short key takeaway.

SOURCE ACCURACY:
1. Follow the supplied page content.
2. Do not invent program features, fees, placement claims, partnerships
   or certifications.
3. Do not introduce unsupported facts.
4. Clearly distinguish general examples from source facts.

AUDIO-FRIENDLY STYLE:
1. Write in natural spoken language.
2. Use short, understandable sentences.
3. Avoid Markdown tables and excessive symbols.
4. Use clear transitions between topics.
5. Expand abbreviations when appropriate.
6. Make the explanation suitable for listening.

Write the entire explanation in {language}.
"""

    user_prompt = f"""
Explain the following selected page from the PragyanAI AI Engineering
Program brochure. The explanation will be used as an educational
audio lesson for students.

PAGE CONTENT:
{cleaned_text}

END OF PAGE CONTENT.
"""

    return generate_ai_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=EXPLANATION_TEMPERATURE,
        max_tokens=3000,
    )


# =================================================
# 10. PAGE SUMMARY
# =================================================

def summarize_page(page_text: str, language: str = "English") -> str:
    """Generate a concise summary of a selected PDF page."""
    validate_language(language)
    cleaned_text = validate_page_text(page_text)

    system_prompt = f"""
You are an educational content summarization assistant.

Summarize the supplied PDF page in {language}.

REQUIREMENTS:
1. Identify the main topic.
2. Include the important concepts.
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
        max_tokens=1200,
    )


# =================================================
# 11. STREAMLIT SAFE FUNCTIONS
# =================================================

def safe_translate_page_text(page_text: str, language: str = "English"):
    """Translate page content with Streamlit error handling; return text or None."""
    try:
        with st.spinner(f"Translating page into {language}..."):
            return translate_page_text(page_text, language)
    except Exception as error:
        st.error(f"Translation failed: {error}")
        return None


def safe_explain_page(page_text: str, language: str = "English"):
    """Generate a page explanation with Streamlit error handling."""
    try:
        with st.spinner("Generating AI page explanation..."):
            return explain_page(page_text, language)
    except Exception as error:
        st.error(f"Explanation generation failed: {error}")
        return None


def safe_summarize_page(page_text: str, language: str = "English"):
    """Generate a page summary with Streamlit error handling."""
    try:
        with st.spinner("Generating page summary..."):
            return summarize_page(page_text, language)
    except Exception as error:
        st.error(f"Summary generation failed: {error}")
        return None


# =================================================
# 12. API CONNECTION TEST
# =================================================

def test_groq_connection():
    """
    Test Groq connectivity and model access.

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        response = generate_ai_response(
            system_prompt="You are a helpful assistant. Respond briefly.",
            user_prompt="Reply with: PragyanAI Groq connection successful.",
            temperature=0.1,
            max_tokens=100,
        )
        return True, response
    except Exception as error:
        return False, str(error)


# =================================================
# 13. AVAILABLE LANGUAGE HELPER
# =================================================

def get_supported_languages():
    """Return supported language names for UI dropdowns."""
    return list(SUPPORTED_LANGUAGES.keys())

