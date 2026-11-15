
"""
PragyanAI - Interactive PDF Flipbook
=================================================

Features:
1. View PDF page by page.
2. Previous / Next page navigation.
3. Zoom in and zoom out.
4. Download complete PDF.
5. Extract selected page text.
6. Translate selected page into multiple languages.
7. Generate AI explanation of selected page.
8. Browser-based Audio Book playback.

Dependencies:
    streamlit
    PyMuPDF

Optional AI dependency:
    groq

Required project structure:
    utils/pdf_utils.py
    services/page_assistant.py
"""

import json
import streamlit as st
import fitz


# =========================================================
# 1. OPTIONAL PAGE ASSISTANT IMPORT
# =========================================================

try:
    from services.page_assistant import (
        explain_page,
        translate_page_text
    )

    PAGE_ASSISTANT_AVAILABLE = True
    PAGE_ASSISTANT_ERROR = None

except Exception as import_error:

    PAGE_ASSISTANT_AVAILABLE = False
    PAGE_ASSISTANT_ERROR = str(import_error)

    explain_page = None
    translate_page_text = None


def _show_ai_error(error, task="AI request"):
    """
    Display actionable guidance for common Groq authentication failures.
    Never print or expose the configured API key.
    """
    error_text = str(error)
    lowered = error_text.lower()

    if "401" in lowered or "invalid_api_key" in lowered or "invalid api key" in lowered:
        st.error(f"{task} could not authenticate with Groq: invalid API key.")
        st.markdown(
            """
            **How to fix the Groq API key**

            1. Open your [Groq Console](https://console.groq.com/keys).
            2. Create a valid API key or copy the correct active key.
            3. In Streamlit Cloud, open your app → **Manage app** →
               **Settings** → **Secrets**.
            4. Add or update this setting:

            ```toml
            GROQ_API_KEY = "gsk_your_actual_key_here"
            ```

            5. Save the Secrets and reboot/redeploy the app.

            Do not paste your real API key into chat, GitHub, or source code.
            """
        )
    elif "429" in lowered or "rate_limit" in lowered:
        st.error(f"{task} reached the Groq rate limit. Please wait and try again.")
        with st.expander("Technical details"):
            st.code(error_text)
    else:
        st.error(f"{task} failed. Please check your Groq configuration.")
        with st.expander("Technical details"):
            st.code(error_text)


# =========================================================
# 2. LANGUAGE CONFIGURATION
# =========================================================

LANGUAGES = {
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
    "Chinese (Mandarin)": "Chinese (Mandarin)"
}


LANGUAGE_CODES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Telugu": "te-IN",
    "Tamil": "ta-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    "Bengali": "bn-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN",
    "Urdu": "ur-PK",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Arabic": "ar-SA",
    "Japanese": "ja-JP",
    "Chinese (Mandarin)": "zh-CN"
}


# =========================================================
# 3. PDF VALIDATION
# =========================================================

def validate_pdf(pdf_bytes):
    """
    Validate PDF bytes.

    Returns:
        int: Number of pages.
    """

    if not pdf_bytes:
        raise ValueError(
            "PDF file is empty or not available."
        )

    try:

        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        if document.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        total_pages = len(document)

        document.close()

        if total_pages == 0:
            raise ValueError(
                "PDF does not contain any pages."
            )

        return total_pages

    except Exception as error:

        raise ValueError(
            f"Unable to read PDF: {error}"
        ) from error


# =========================================================
# 4. EXTRACT TEXT FROM ALL PDF PAGES
# =========================================================

def pdf_to_text(pdf_bytes):
    """
    Extract text from all pages of a PDF.

    Returns:
        list: Page number and extracted text.
    """

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    pages = []

    try:

        for page_number, page in enumerate(document):

            page_text = page.get_text("text")

            pages.append({
                "page_number": page_number + 1,
                "text": page_text.strip()
            })

    finally:

        document.close()

    return pages


# =========================================================
# 5. EXTRACT SELECTED PAGE TEXT
# =========================================================

def extract_page_text(pdf_bytes, page_number):
    """
    Extract text from one selected PDF page.

    Args:
        pdf_bytes: PDF file bytes.
        page_number: Zero-based page index.

    Returns:
        str: Extracted page text.
    """

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    try:

        if page_number < 0 or page_number >= len(document):
            return ""

        page = document.load_page(
            page_number
        )

        return page.get_text("text").strip()

    finally:

        document.close()


# =========================================================
# 6. RENDER SELECTED PDF PAGE
# =========================================================

def render_pdf_page(
    pdf_bytes,
    page_number,
    zoom=1.5
):
    """
    Convert selected PDF page into PNG image.

    Args:
        pdf_bytes: PDF bytes.
        page_number: Zero-based page index.
        zoom: Rendering scale.

    Returns:
        bytes: PNG image bytes.
    """

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    try:

        if page_number < 0 or page_number >= len(document):
            return None

        page = document.load_page(
            page_number
        )

        matrix = fitz.Matrix(
            zoom,
            zoom
        )

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        return pixmap.tobytes("png")

    finally:

        document.close()


# =========================================================
# 7. DISPLAY SELECTED PAGE
# =========================================================

def _render_pdf_pages(
    pdf_bytes,
    page_number,
    zoom
):
    """
    Display selected PDF page.
    """

    image_bytes = render_pdf_page(
        pdf_bytes,
        page_number,
        zoom
    )

    if image_bytes is None:

        st.error(
            "Unable to render the selected PDF page."
        )

        return

    st.image(
        image_bytes,
        caption=f"Page {page_number + 1}",
        use_container_width=True
    )


# =========================================================
# 8. DOWNLOAD PDF
# =========================================================

def _render_download_pdf(pdf_bytes):
    """
    Display PDF download option.
    """

    st.subheader(
        "Download Complete Brochure"
    )

    st.write(
        "Download the complete PragyanAI AI Engineering "
        "Program brochure for offline reading."
    )

    st.download_button(
        label="⬇ Download PDF Brochure",
        data=pdf_bytes,
        file_name="PragyanAI_AI_Engineering_Program.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="download_pragyanai_pdf"
    )


# =========================================================
# 9. CHECK AI ASSISTANT
# =========================================================

def _check_page_assistant():
    """
    Check whether the page assistant is available.
    """

    if not PAGE_ASSISTANT_AVAILABLE:

        st.error(
            "AI Page Assistant is not available. "
            "Please check services/page_assistant.py "
            "and its dependencies."
        )

        with st.expander("Technical details"):

            st.code(
                str(PAGE_ASSISTANT_ERROR)
            )

        return False

    return True


# =========================================================
# 10. TRANSLATE SELECTED PAGE
# =========================================================

def _render_translation(
    pdf_bytes,
    page_number,
    language
):
    """
    Extract and translate selected PDF page.
    """

    page_text = extract_page_text(
        pdf_bytes,
        page_number
    )

    if not page_text:

        st.warning(
            "No extractable text was found on this page. "
            "It may contain scanned images rather than text."
        )

        return

    st.subheader(
        "Original Page Text"
    )

    st.text_area(
        "Extracted content",
        value=page_text,
        height=250,
        key=f"original_text_{page_number}"
    )

    if st.button(
        f"Translate into {language}",
        key=f"translate_{page_number}_{language}",
        use_container_width=True
    ):

        if not _check_page_assistant():
            return

        try:

            with st.spinner(
                f"Translating into {language}..."
            ):

                translated_text = translate_page_text(
                    page_text,
                    language
                )

            if translated_text:

                st.session_state[
                    f"translated_{page_number}_{language}"
                ] = translated_text

            else:

                st.error(
                    "Translation returned an empty response."
                )

        except Exception as error:
            _show_ai_error(error, task="Translation")

    translated_key = (
        f"translated_{page_number}_{language}"
    )

    if translated_key in st.session_state:

        st.divider()

        st.subheader(
            f"Translated Content - {language}"
        )

        st.text_area(
            "Translated page",
            value=st.session_state[translated_key],
            height=350,
            key=f"display_translation_{page_number}_{language}"
        )

        st.download_button(
            label="Download Translated Text",
            data=st.session_state[translated_key],
            file_name=f"PragyanAI_Page_{page_number + 1}_{language}.txt",
            mime="text/plain",
            key=f"download_translation_{page_number}_{language}"
        )


# =========================================================
# 11. BROWSER AUDIO BOOK PLAYER
# =========================================================

def _render_audio_player(
    text,
    language="English"
):
    """
    Browser-based text-to-speech player.
    Audio is synthesized by the visitor's browser; no MP3 is generated.
    """

    if not text or not str(text).strip():
        st.info("There is no explanation text available to play.")
        return

    voice_language = LANGUAGE_CODES.get(language, "en-IN")
    safe_text = json.dumps(str(text), ensure_ascii=False)
    safe_language = json.dumps(voice_language, ensure_ascii=False)

    component_html = f"""
    <div style="
        padding: 18px;
        border: 1px solid #dbe3f0;
        border-radius: 14px;
        background: linear-gradient(135deg, #f8fbff, #eef4ff);
        font-family: Arial, sans-serif;
    ">
        <div style="font-size:17px;font-weight:700;color:#172554;margin-bottom:12px;">
            🎧 PragyanAI Audio Book Player
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:9px;">
            <button id="play" style="padding:10px 18px;border:0;border-radius:8px;color:white;background:#1d4ed8;cursor:pointer;">▶ Play</button>
            <button id="pause" style="padding:10px 18px;border:0;border-radius:8px;color:white;background:#475569;cursor:pointer;">⏸ Pause</button>
            <button id="resume" style="padding:10px 18px;border:0;border-radius:8px;color:white;background:#15803d;cursor:pointer;">▶ Resume</button>
            <button id="stop" style="padding:10px 18px;border:0;border-radius:8px;color:white;background:#b91c1c;cursor:pointer;">■ Stop</button>
        </div>
        <div id="status" style="margin-top:12px;color:#475569;font-size:13px;">
            Ready to play · Language: {language}
        </div>
    </div>

    <script>
        const textToSpeak = {safe_text};
        const selectedLanguage = {safe_language};
        const statusElement = document.getElementById("status");
        let speechUtterance = null;

        function stopSpeech() {{
            if ("speechSynthesis" in window) {{
                window.speechSynthesis.cancel();
            }}
        }}

        function playSpeech() {{
            if (!("speechSynthesis" in window)) {{
                statusElement.innerText = "Speech synthesis is not supported in this browser.";
                return;
            }}
            stopSpeech();
            speechUtterance = new SpeechSynthesisUtterance(textToSpeak);
            speechUtterance.lang = selectedLanguage;
            speechUtterance.rate = 0.92;
            speechUtterance.pitch = 1;
            speechUtterance.onstart = function() {{
                statusElement.innerText = "Playing audio...";
            }};
            speechUtterance.onend = function() {{
                statusElement.innerText = "Playback completed.";
            }};
            speechUtterance.onerror = function(event) {{
                statusElement.innerText = "Playback error: " + event.error;
            }};
            window.speechSynthesis.speak(speechUtterance);
        }}

        document.getElementById("play").addEventListener("click", playSpeech);
        document.getElementById("pause").addEventListener("click", function() {{
            if ("speechSynthesis" in window) {{
                window.speechSynthesis.pause();
                statusElement.innerText = "Playback paused.";
            }}
        }});
        document.getElementById("resume").addEventListener("click", function() {{
            if ("speechSynthesis" in window) {{
                window.speechSynthesis.resume();
                statusElement.innerText = "Playback resumed.";
            }}
        }});
        document.getElementById("stop").addEventListener("click", function() {{
            stopSpeech();
            statusElement.innerText = "Playback stopped.";
        }});
    </script>
    """

    st.components.v1.html(
        component_html,
        height=165,
        scrolling=False
    )


# =========================================================
# 12. GENERATE AUDIO BOOK EXPLANATION
# =========================================================

def _render_audio_book(
    pdf_bytes,
    page_number,
    language
):
    """
    Generate an AI explanation and display audio player.
    """

    page_text = extract_page_text(
        pdf_bytes,
        page_number
    )

    if not page_text:

        st.warning(
            "No extractable text was found on this page."
        )

        return

    st.markdown(
        f"### Audio Explanation - Page {page_number + 1}"
    )

    st.write(
        "Generate a simple educational explanation "
        "of the selected brochure page."
    )

    if st.button(
        f"Generate {language} Explanation",
        key=f"explain_{page_number}_{language}",
        use_container_width=True
    ):

        if not _check_page_assistant():
            return

        try:

            with st.spinner(
                "Generating AI explanation..."
            ):

                explanation = explain_page(
                    page_text,
                    language
                )

            if explanation:

                st.session_state[
                    f"explanation_{page_number}_{language}"
                ] = explanation

            else:

                st.error(
                    "AI returned an empty explanation."
                )

        except Exception as error:
            _show_ai_error(error, task="AI explanation generation")

    explanation_key = (
        f"explanation_{page_number}_{language}"
    )

    if explanation_key in st.session_state:

        explanation = st.session_state[
            explanation_key
        ]

        st.divider()

        st.subheader(
            "AI Page Explanation"
        )

        st.markdown(
            explanation
        )

        st.download_button(
            label="Download Explanation",
            data=explanation,
            file_name=(
                f"PragyanAI_Page_{page_number + 1}_"
                f"{language}_Explanation.txt"
            ),
            mime="text/plain",
            key=f"download_explanation_{page_number}_{language}"
        )

        st.divider()

        st.subheader(
            "Listen to Explanation"
        )

        _render_audio_player(
            explanation,
            language
        )


# =========================================================
# 13. MAIN FLIPBOOK FUNCTION
# =========================================================

def render_flipbook(pdf_bytes):
    """
    Main interactive PDF flipbook.

    Menu options:
        1. View
        2. Download PDF
        3. Extract & Translate
        4. Audio Book

    Args:
        pdf_bytes: PDF document as bytes.
    """

    # -----------------------------------------------------
    # Validate PDF
    # -----------------------------------------------------

    try:

        total_pages = validate_pdf(
            pdf_bytes
        )

    except Exception as error:

        st.error(
            f"PDF loading failed: {error}"
        )

        return

    # -----------------------------------------------------
    # Initialize session state
    # -----------------------------------------------------

    if "flipbook_page" not in st.session_state:
        st.session_state.flipbook_page = 0

    if "flipbook_zoom" not in st.session_state:
        st.session_state.flipbook_zoom = 1.5

    # Keep the number_input widget in sync with the navigation buttons.
    if "flipbook_page_selector" not in st.session_state:
        st.session_state.flipbook_page_selector = (
            st.session_state.flipbook_page + 1
        )

    # Validate current page state.

    st.session_state.flipbook_page = max(
        0,
        min(
            st.session_state.flipbook_page,
            total_pages - 1
        )
    )

    # -----------------------------------------------------
    # Flipbook header
    # -----------------------------------------------------

    with st.container(border=True):
        st.markdown("## 📖 PragyanAI Program Flipbook")
        st.caption(
            "Explore the AI Engineering Program brochure page by page. "
            "Navigate, zoom, download, translate and listen to AI explanations."
        )


    # -----------------------------------------------------
    # Main menu
    # -----------------------------------------------------

    st.markdown(
        """
        <style>
        div[data-testid="stTabs"] button[role="tab"] {
            font-weight: 650;
            padding: 0.65rem 1rem;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            border-bottom: 3px solid #6d28d9;
        }
        div[data-testid="stButton"] button {
            border-radius: 10px;
            font-weight: 600;
            min-height: 42px;
        }
        div[data-testid="stDownloadButton"] button {
            border-radius: 10px;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    view_tab, download_tab, translate_tab, audio_tab = st.tabs(
        [
            "📖 View",
            "⬇ Download PDF",
            "🌐 Extract & Translate",
            "🎧 Audio Book"
        ]
    )

    # =====================================================
    # TAB 1: VIEW
    # =====================================================

    with view_tab:

        st.subheader(
            "Browse Program Brochure"
        )

        # -------------------------------------------------
        # Page navigation
        # -------------------------------------------------

        previous_col, page_col, next_col = st.columns(
            [1, 2, 1]
        )

        with previous_col:

            if st.button(
                "◀ Previous",
                disabled=(
                    st.session_state.flipbook_page == 0
                ),
                use_container_width=True,
                key="flipbook_previous"
            ):

                st.session_state.flipbook_page = max(
                    0,
                    st.session_state.flipbook_page - 1
                )
                st.session_state.flipbook_page_selector = (
                    st.session_state.flipbook_page + 1
                )
                st.rerun()

        with page_col:

            selected_page = st.number_input(
                "Select Page",
                min_value=1,
                max_value=total_pages,
                value=st.session_state.flipbook_page + 1,
                step=1,
                key="flipbook_page_selector"
            )

            if (
                selected_page - 1
                != st.session_state.flipbook_page
            ):

                st.session_state.flipbook_page = (
                    int(selected_page) - 1
                )
                st.session_state.flipbook_page_selector = int(selected_page)
                st.rerun()

        with next_col:

            if st.button(
                "Next ▶",
                disabled=(
                    st.session_state.flipbook_page
                    >= total_pages - 1
                ),
                use_container_width=True,
                key="flipbook_next"
            ):

                st.session_state.flipbook_page = min(
                    total_pages - 1,
                    st.session_state.flipbook_page + 1
                )
                st.session_state.flipbook_page_selector = (
                    st.session_state.flipbook_page + 1
                )
                st.rerun()

        current_page_display = st.session_state.flipbook_page + 1
        st.markdown(
            f"**Page {current_page_display} of {total_pages}**"
        )
        st.progress(current_page_display / total_pages)

        # -------------------------------------------------
        # Zoom controls
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "Zoom Controls"
        )

        zoom_col1, zoom_col2, zoom_col3 = st.columns(
            [1, 2, 1]
        )

        with zoom_col1:

            if st.button(
                "− Zoom Out",
                use_container_width=True,
                key="flipbook_zoom_out"
            ):

                st.session_state.flipbook_zoom = max(
                    0.6,
                    st.session_state.flipbook_zoom - 0.2
                )

                st.rerun()

        with zoom_col2:

            zoom_value = st.slider(
                "Zoom Level",
                min_value=0.6,
                max_value=2.5,
                value=float(
                    st.session_state.flipbook_zoom
                ),
                step=0.1,
                key="flipbook_zoom_slider"
            )

            if zoom_value != st.session_state.flipbook_zoom:

                st.session_state.flipbook_zoom = zoom_value

                st.rerun()

        with zoom_col3:

            if st.button(
                "+ Zoom In",
                use_container_width=True,
                key="flipbook_zoom_in"
            ):

                st.session_state.flipbook_zoom = min(
                    2.5,
                    st.session_state.flipbook_zoom + 0.2
                )

                st.rerun()

        st.divider()

        # -------------------------------------------------
        # Render PDF page
        # -------------------------------------------------

        _render_pdf_pages(
            pdf_bytes=pdf_bytes,
            page_number=st.session_state.flipbook_page,
            zoom=st.session_state.flipbook_zoom
        )

        st.caption(
            "Use Previous / Next to navigate pages. "
            "Use Zoom Controls to change page size."
        )

    # =====================================================
    # TAB 2: DOWNLOAD PDF
    # =====================================================

    with download_tab:

        _render_download_pdf(
            pdf_bytes
        )

    # =====================================================
    # TAB 3: EXTRACT AND TRANSLATE
    # =====================================================

    with translate_tab:

        st.subheader(
            "Extract & Translate PDF Page"
        )

        page_for_translation = st.selectbox(
            "Select Page",
            options=list(range(1, total_pages + 1)),
            index=st.session_state.flipbook_page,
            key="translation_page_selector"
        )

        language_for_translation = st.selectbox(
            "Select Target Language",
            options=list(LANGUAGES.keys()),
            index=0,
            key="translation_language_selector"
        )

        st.divider()

        _render_translation(
            pdf_bytes=pdf_bytes,
            page_number=page_for_translation - 1,
            language=LANGUAGES[language_for_translation]
        )

    # =====================================================
    # TAB 4: AUDIO BOOK
    # =====================================================

    with audio_tab:

        st.subheader(
            "AI Audio Book"
        )

        st.write(
            "Listen to an AI-generated explanation "
            "of each brochure page."
        )

        page_for_audio = st.selectbox(
            "Select Page",
            options=list(range(1, total_pages + 1)),
            index=st.session_state.flipbook_page,
            key="audio_page_selector"
        )

        language_for_audio = st.selectbox(
            "Select Explanation Language",
            options=list(LANGUAGES.keys()),
            index=0,
            key="audio_language_selector"
        )

        st.divider()

        _render_audio_book(
            pdf_bytes=pdf_bytes,
            page_number=page_for_audio - 1,
            language=LANGUAGES[language_for_audio]
        )
