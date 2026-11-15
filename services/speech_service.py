"""
PragyanAI Speech Service
========================

Speech and audio utilities for the PragyanAI Streamlit application.

Features
--------
1. Speech-to-text from uploaded audio bytes or a local audio file.
2. Optional local microphone recording/transcription (works only where a
   microphone is accessible to the Python process; not normally available
   on Streamlit Community Cloud).
3. Audio format conversion to WAV using pydub.
4. Text-to-speech MP3 generation using gTTS.
5. Optional translation through the existing services.page_assistant module.

Recommended requirements.txt additions
---------------------------------------
gTTS>=2.5.4
SpeechRecognition>=3.14.0
pydub>=0.25.1

System dependency
-----------------
pydub may require FFmpeg for MP3, M4A, AAC, and other compressed formats.
Install FFmpeg in the deployment environment. WAV audio can usually be
processed without FFmpeg.

SpeechRecognition's Google recognizer and gTTS require internet access.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Optional, Union

# ---------------------------------------------------------------------
# Optional dependencies
# ---------------------------------------------------------------------

try:
    import speech_recognition as sr

    SPEECH_RECOGNITION_AVAILABLE = True
    SPEECH_RECOGNITION_IMPORT_ERROR = None
except Exception as import_error:
    sr = None
    SPEECH_RECOGNITION_AVAILABLE = False
    SPEECH_RECOGNITION_IMPORT_ERROR = str(import_error)

try:
    from pydub import AudioSegment

    PYDUB_AVAILABLE = True
    PYDUB_IMPORT_ERROR = None
except Exception as import_error:
    AudioSegment = None
    PYDUB_AVAILABLE = False
    PYDUB_IMPORT_ERROR = str(import_error)

try:
    from gtts import gTTS

    GTTS_AVAILABLE = True
    GTTS_IMPORT_ERROR = None
except Exception as import_error:
    gTTS = None
    GTTS_AVAILABLE = False
    GTTS_IMPORT_ERROR = str(import_error)


# ---------------------------------------------------------------------
# Language configuration
# ---------------------------------------------------------------------

# SpeechRecognition's Google recognizer accepts BCP-47-style language tags.
SPEECH_LANGUAGE_CODES = {
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
    "Chinese (Mandarin)": "zh-CN",
}

# gTTS language identifiers. gTTS support can vary by package release.
GTTS_LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Telugu": "te",
    "Tamil": "ta",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Urdu": "ur",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Arabic": "ar",
    "Japanese": "ja",
    "Chinese (Mandarin)": "zh-CN",
}


# ---------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------

def get_speech_service_status() -> dict:
    """
    Return dependency availability and import errors.

    This is useful for showing a diagnostics section in Streamlit.
    """
    return {
        "speech_recognition_available": SPEECH_RECOGNITION_AVAILABLE,
        "speech_recognition_error": SPEECH_RECOGNITION_IMPORT_ERROR,
        "pydub_available": PYDUB_AVAILABLE,
        "pydub_error": PYDUB_IMPORT_ERROR,
        "gtts_available": GTTS_AVAILABLE,
        "gtts_error": GTTS_IMPORT_ERROR,
    }


def _require_speech_recognition() -> None:
    if not SPEECH_RECOGNITION_AVAILABLE:
        raise RuntimeError(
            "SpeechRecognition is not installed. Add "
            "'SpeechRecognition>=3.14.0' to requirements.txt and redeploy. "
            f"Import details: {SPEECH_RECOGNITION_IMPORT_ERROR}"
        )


def _require_pydub() -> None:
    if not PYDUB_AVAILABLE:
        raise RuntimeError(
            "pydub is not installed. Add 'pydub>=0.25.1' to "
            "requirements.txt and redeploy. "
            f"Import details: {PYDUB_IMPORT_ERROR}"
        )


def _require_gtts() -> None:
    if not GTTS_AVAILABLE:
        raise RuntimeError(
            "gTTS is not installed. Add 'gTTS>=2.5.4' to "
            "requirements.txt and redeploy. "
            f"Import details: {GTTS_IMPORT_ERROR}"
        )


# ---------------------------------------------------------------------
# Audio conversion helpers
# ---------------------------------------------------------------------

def convert_audio_to_wav(
    audio_bytes: bytes,
    source_format: Optional[str] = None,
    sample_rate: int = 16000,
    channels: int = 1,
) -> bytes:
    """
    Convert uploaded audio bytes to mono WAV suitable for recognition.

    Args:
        audio_bytes: Uploaded audio content.
        source_format: Optional format hint such as "mp3", "m4a", "ogg",
            "webm", or "wav". If omitted, pydub attempts to detect it.
        sample_rate: Output sample rate. 16000 Hz is a practical default.
        channels: Output channel count. Speech recognition generally works
            well with mono audio.

    Returns:
        WAV file bytes.

    Note:
        Compressed formats generally require FFmpeg to be installed.
    """
    _require_pydub()

    if not audio_bytes:
        raise ValueError("The uploaded audio file is empty.")

    if sample_rate <= 0:
        raise ValueError("sample_rate must be greater than zero.")

    if channels not in (1, 2):
        raise ValueError("channels must be 1 or 2.")

    audio_stream = BytesIO(audio_bytes)
    format_hint = source_format.lower().strip(". ") if source_format else None

    try:
        if format_hint:
            audio = AudioSegment.from_file(
                audio_stream,
                format=format_hint
            )
        else:
            audio = AudioSegment.from_file(audio_stream)

        audio = audio.set_frame_rate(sample_rate).set_channels(channels)

        wav_buffer = BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        return wav_buffer.getvalue()

    except Exception as error:
        raise RuntimeError(
            "Audio conversion failed. Confirm the file is a supported audio "
            "format and that FFmpeg is installed for compressed formats. "
            f"Details: {error}"
        ) from error


def audio_file_to_wav(
    file_path: Union[str, Path],
    sample_rate: int = 16000,
    channels: int = 1,
) -> bytes:
    """
    Read a local audio file and convert it to WAV bytes.
    """
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")

    try:
        audio_bytes = path.read_bytes()
    except Exception as error:
        raise RuntimeError(f"Unable to read audio file: {error}") from error

    return convert_audio_to_wav(
        audio_bytes=audio_bytes,
        source_format=path.suffix.lstrip(".") or None,
        sample_rate=sample_rate,
        channels=channels,
    )


# ---------------------------------------------------------------------
# Speech-to-text
# ---------------------------------------------------------------------

def transcribe_audio_bytes(
    audio_bytes: bytes,
    language: str = "English",
    source_format: Optional[str] = None,
    timeout: int = 20,
    phrase_time_limit: Optional[int] = None,
) -> str:
    """
    Transcribe uploaded audio bytes using SpeechRecognition's Google
    Web Speech recognizer.

    Args:
        audio_bytes: Uploaded audio bytes.
        language: A key in SPEECH_LANGUAGE_CODES, or a BCP-47 language code.
        source_format: Optional input format (mp3, m4a, wav, ogg, webm, etc.).
            If omitted, pydub attempts to detect the format.
        timeout: Maximum time to wait for speech to start.
        phrase_time_limit: Optional maximum phrase duration in seconds.

    Returns:
        Recognized text.

    Raises:
        ValueError: Empty audio or no speech recognized.
        RuntimeError: Missing dependency, conversion, network, or API errors.
    """
    _require_speech_recognition()

    if not audio_bytes:
        raise ValueError("The uploaded audio file is empty.")

    language_code = SPEECH_LANGUAGE_CODES.get(language, language)

    # WAV may be passed directly to SpeechRecognition. Other formats are
    # converted through pydub/FFmpeg first.
    extension = (source_format or "").lower().strip(". ")
    if extension == "wav":
        wav_bytes = audio_bytes
    else:
        wav_bytes = convert_audio_to_wav(
            audio_bytes=audio_bytes,
            source_format=extension or None,
        )

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(BytesIO(wav_bytes)) as audio_source:
            audio_data = recognizer.record(
                audio_source,
                duration=phrase_time_limit
            )

        recognized_text = recognizer.recognize_google(
            audio_data,
            language=language_code
        )

        recognized_text = recognized_text.strip()
        if not recognized_text:
            raise ValueError("No speech was recognized in the audio.")

        return recognized_text

    except sr.UnknownValueError as error:
        raise ValueError(
            "Speech could not be understood. Try a clearer recording "
            "with less background noise."
        ) from error
    except sr.RequestError as error:
        raise RuntimeError(
            "The speech recognition service could not be reached. "
            "Check the internet connection and try again. "
            f"Details: {error}"
        ) from error
    except (ValueError, RuntimeError):
        raise
    except Exception as error:
        raise RuntimeError(
            f"Speech transcription failed: {error}"
        ) from error


def transcribe_audio_file(
    file_path: Union[str, Path],
    language: str = "English",
    timeout: int = 20,
    phrase_time_limit: Optional[int] = None,
) -> str:
    """
    Transcribe a local audio file.

    The file extension is used as the source format hint.
    """
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")

    audio_bytes = path.read_bytes()

    return transcribe_audio_bytes(
        audio_bytes=audio_bytes,
        language=language,
        source_format=path.suffix.lstrip(".") or None,
        timeout=timeout,
        phrase_time_limit=phrase_time_limit,
    )


def transcribe_microphone(
    language: str = "English",
    timeout: int = 5,
    phrase_time_limit: int = 15,
) -> str:
    """
    Record and transcribe audio from a microphone attached to the machine
    running this Python process.

    IMPORTANT:
    This is intended for local Python applications. In Streamlit Cloud,
    sr.Microphone() accesses the server's microphone, not the website
    visitor's computer. For browser microphone input, use a Streamlit
    browser microphone component and pass its returned audio bytes to
    transcribe_audio_bytes().
    """
    _require_speech_recognition()

    language_code = SPEECH_LANGUAGE_CODES.get(language, language)
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.6
            )
            audio_data = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        recognized_text = recognizer.recognize_google(
            audio_data,
            language=language_code
        ).strip()

        if not recognized_text:
            raise ValueError("No speech was recognized.")

        return recognized_text

    except sr.WaitTimeoutError as error:
        raise TimeoutError(
            "No speech was detected before the recording timeout."
        ) from error
    except sr.UnknownValueError as error:
        raise ValueError(
            "Speech could not be understood. Please try again."
        ) from error
    except sr.RequestError as error:
        raise RuntimeError(
            f"Speech recognition service error: {error}"
        ) from error
    except (TimeoutError, ValueError, RuntimeError):
        raise
    except OSError as error:
        raise RuntimeError(
            "Microphone is unavailable. Check microphone permissions "
            f"and the audio input device. Details: {error}"
        ) from error


# ---------------------------------------------------------------------
# Text-to-speech
# ---------------------------------------------------------------------

def text_to_speech_mp3(
    text: str,
    language: str = "English",
    slow: bool = False,
) -> bytes:
    """
    Convert text into MP3 bytes using gTTS.

    Internet access is required. Returns MP3 bytes for st.audio() or
    st.download_button().
    """
    _require_gtts()

    clean_text = str(text or "").strip()
    if not clean_text:
        raise ValueError("There is no text available for speech generation.")

    language_code = GTTS_LANGUAGE_CODES.get(language, language)

    try:
        buffer = BytesIO()
        speech = gTTS(
            text=clean_text,
            lang=language_code,
            slow=slow
        )
        speech.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as error:
        raise RuntimeError(
            "gTTS could not generate audio. Check your internet connection "
            "and confirm that the selected language is supported. "
            f"Details: {error}"
        ) from error


# ---------------------------------------------------------------------
# Translation using the existing PragyanAI page assistant
# ---------------------------------------------------------------------

def translate_recognized_text(
    text: str,
    target_language: str,
) -> str:
    """
    Translate recognized speech using the existing page assistant.

    This function reuses services.page_assistant.translate_page_text(),
    so the Groq configuration remains centralized in that module.
    """
    clean_text = str(text or "").strip()

    if not clean_text:
        raise ValueError("There is no recognized text to translate.")

    try:
        from services.page_assistant import translate_page_text
    except Exception as error:
        raise RuntimeError(
            "The PragyanAI translation service could not be imported. "
            "Check services/page_assistant.py and its dependencies. "
            f"Details: {error}"
        ) from error

    try:
        translated = translate_page_text(
            clean_text,
            target_language
        )
    except Exception as error:
        raise RuntimeError(
            f"Speech text translation failed: {error}"
        ) from error

    if not translated or not str(translated).strip():
        raise RuntimeError("Translation returned an empty result.")

    return str(translated).strip()


# ---------------------------------------------------------------------
# Convenience pipeline
# ---------------------------------------------------------------------

def transcribe_and_translate(
    audio_bytes: bytes,
    source_language: str = "English",
    target_language: Optional[str] = None,
    source_format: Optional[str] = None,
) -> dict:
    """
    Transcribe uploaded audio and optionally translate the recognized text.

    Returns:
        {
            "recognized_text": "...",
            "translated_text": "... or None",
            "source_language": "...",
            "target_language": "... or None"
        }
    """
    recognized_text = transcribe_audio_bytes(
        audio_bytes=audio_bytes,
        language=source_language,
        source_format=source_format,
    )

    translated_text = None
    if target_language:
        translated_text = translate_recognized_text(
            recognized_text,
            target_language
        )

    return {
        "recognized_text": recognized_text,
        "translated_text": translated_text,
        "source_language": source_language,
        "target_language": target_language,
    }
