
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

import html
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

            st.error(
                f"Translation failed: {error}"
            )

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
    Play AI-generated explanation using browser
    speechSynthesis.

    Note:
        Audio is played by the browser.
        This does not generate a downloadable MP3.
    """

    if not text or not text.strip():

        st.warning(
            "No explanation is available for audio playback."
        )

        return

    voice_language = LANGUAGE_CODES.get(
        language,
        "en-IN"
    )

    safe_text = html.escape(
        text,
        quote=True
    )

    safe_language = html.escape(
        voice_language,
        quote=True
    )

    component_html = f"""
    <div style="
        padding: 18px;
        border: 1px solid #d9d9d9;
        border-radius: 12px;
        background: #f8fafc;
        font-family: Arial, sans-serif;
    ">

        <h4 style="
            margin-top: 0;
            color: #1e293b;
        ">
            PragyanAI Audio Book Player
        </h4>

        <div style="
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        ">

            <button id="play" style="
                padding: 10px 18px;
                border: none;
                border-radius: 7px;
                color: white;
                background: #2563eb;
                cursor: pointer;
            ">▶ Play</button>

            <button id="pause" style="
                padding: 10px 18px;
                border: none;
                border-radius: 7px;
                color: white;
                background: #64748b;
                cursor: pointer;
            ">⏸ Pause</button>

            <button id="resume" style="
                padding: 10px 18px;
                border: none;
                border-radius: 7px;
                color: white;
                background: #16a34a;
                cursor: pointer;
            ">▶ Resume</button>

            <button id="stop" style="
                padding: 10px 18px;
                border: none;
                border-radius: 7px;
                color: white;
                background: #dc2626;
                cursor: pointer;
            ">■ Stop</button>

        </div>

        <p id="status" style="
            margin-bottom: 0;
            margin-top: 14px;
            font-size: 13px;
            color: #475569;
        ">
            Ready to play.
        </p>

    </div>

    <script>

        const textToSpeak = "{safe_text}";
        const selectedLanguage = "{safe_language}";

        const statusElement =
            document.getElementById("status");

        let speechUtterance = null;

        function stopSpeech() {

            if ("speechSynthesis" in window) {
                window.speechSynthesis.cancel();
            }

        }

        function playSpeech() {

            if (!("speechSynthesis" in window)) {

                statusElement.innerText =
                    "Your browser does not support speech synthesis.";

                return;

            }

            stopSpeech();

            speechUtterance =
                new SpeechSynthesisUtterance(textToSpeak);

            speechUtterance.lang = selectedLanguage;

            speechUtterance.rate = 0.9;

            speechUtterance.pitch = 1;

            speechUtterance.onstart = function() {

                statusElement.innerText =
                    "Playing audio...";

            };

            speechUtterance.onend = function() {

                statusElement.innerText =
                    "Audio completed.";

            };

            speechUtterance.onerror = function(event) {

                statusElement.innerText =
                    "Audio error: " + event.error;

            };

            window.speechSynthesis.speak(
                speechUtterance
            );

        }

        document.getElementById("play")
            .addEventListener("click", playSpeech);

        document.getElementById("pause")
            .addEventListener("click", function() {

                window.speechSynthesis.pause();

                statusElement.innerText =
                    "Audio paused.";

            });

        document.getElementById("resume")
            .addEventListener("click", function() {

                window.speechSynthesis.resume();

                statusElement.innerText =
                    "Audio resumed.";

            });

        document.getElementById("stop")
            .addEventListener("click", function() {

                stopSpeech();

                statusElement.innerText =
                    "Audio stopped.";

            });

    </script>
    """

    st.components.v1.html(
        component_html,
        height=180,
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

            st.error(
                f"Explanation generation failed: {error}"
            )

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

    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 10px 0 18px 0;
        ">

            <h2 style="
                margin-bottom: 5px;
            ">
                PragyanAI Program Flipbook
            </h2>

            <p style="
                color: gray;
                margin-top: 0;
            ">
                Explore the AI Engineering Program brochure.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # Main menu
    # -----------------------------------------------------

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

                st.session_state.flipbook_page -= 1

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
                    selected_page - 1
                )

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

                st.session_state.flipbook_page += 1

                st.rerun()

        st.caption(
            f"Page {st.session_state.flipbook_page + 1} "
            f"of {total_pages}"
        )

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
