
import streamlit as st
from utils.config import get_setting


def get_google_form_url():
    """
    Read Google Form URL from Streamlit Secrets
    or environment configuration.
    """

    embed_url = get_setting("GOOGLE_FORM_EMBED_URL")

    if not embed_url:
        embed_url = get_setting("GOOGLE_FORM_URL")

    return embed_url.strip() if embed_url else ""


def convert_to_embed_url(form_url):
    """
    Convert standard Google Forms responder URL
    into an embedded Google Forms URL.
    """

    form_url = form_url.strip()

    if not form_url:
        return ""

    if "docs.google.com/forms" not in form_url:
        return ""

    if "embedded=true" in form_url:
        return form_url

    separator = "&" if "?" in form_url else "?"

    return f"{form_url}{separator}embedded=true"


def render_google_eoi_form():

    st.markdown(
        """
        <div style="
            background:linear-gradient(120deg,#24075c,#5512a0);
            padding:25px;
            border-radius:15px;
            color:white;
            margin-bottom:20px;
        ">
            <h2 style="color:white;">
                Expression of Interest
            </h2>
            <p>
                Join PragyanAI's 6-Month AI Engineering Program.
                Submit your details to receive program information
                and admission guidance.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    form_url = get_google_form_url()

    if not form_url:

        st.warning(
            "Google Form URL is not configured."
        )

        st.info(
            "Please configure GOOGLE_FORM_URL "
            "in Streamlit Secrets."
        )

        st.code(
            """
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform"
            """,
            language="toml"
        )

        return

    embed_url = convert_to_embed_url(form_url)

    if not embed_url:

        st.error(
            "Invalid Google Forms URL. "
            "Please provide a valid responder URL."
        )

        return

    st.markdown(
        "### Student Registration Form"
    )

    st.caption(
        "Please complete all required fields "
        "and submit your Expression of Interest."
    )

    # Display Google Form inside Streamlit
    st.components.v1.iframe(
        src=embed_url,
        height=1150,
        scrolling=True
    )

    st.markdown("---")

    st.markdown(
        "Having trouble with the embedded form?"
    )

    # Direct Google Form link
    direct_url = embed_url.replace(
        "embedded=true", ""
    ).rstrip("?&")

    st.link_button(
        "Open Google Form Directly",
        direct_url,
        use_container_width=True
    )

    st.caption(
        "Your response is submitted directly to "
        "the PragyanAI Google Form."
    )
