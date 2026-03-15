import base64
import importlib
import io
import json
import os
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path

import click

from .logger import log

# Allow running from src/python while loading generated client at repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from baml_client import b  # type: ignore[import-not-found]


@click.command()
@click.argument("article_url", type=str, required=True)
@click.option(
    "output_file_name",
    "-o",
    "--output-file-name",
    default="output",
    help="Base file name for output artifacts (audio + metadata JSON).",
)
def main(article_url: str, output_file_name: str):
    log.info("START UP", article_url=article_url)

    # get title, published date and content from article

    log.info("SCRIPT GENERATION")
    try:
        article = b.ExtractArticle(url=article_url)
    except Exception as exc:
        raise click.ClickException(f"Failed to extract article script: {exc}") from exc

    log.debug("SCRIPT GENERATED", word_count=len(article.script.split()))
    log.info("AUDIO GENERATION")

    # Generate audio bytes with Gemini SDK (BAML does not currently parse TTS inlineData).
    try:
        audio_bytes, mime_type = _generate_audio_with_gemini_sdk(article.script)
    except Exception as exc:
        raise click.ClickException(f"Failed to generate podcast audio: {exc}") from exc

    log.debug("AUDIO GENERATED", bytes=len(audio_bytes), mime_type=mime_type)
    final_mime_type = mime_type

    if mime_type and "audio/l16" in mime_type.lower():
        # Gemini preview TTS often returns raw PCM. Wrap to WAV for compatibility.
        audio_bytes = _pcm_l16_to_wav_bytes(audio_bytes, mime_type)
        final_mime_type = "audio/wav"
        log.info("AUDIO FORMAT NORMALIZED", normalized_to="audio/wav")

    # Write audio file and metadata JSON using the same base file name.
    output_audio_file = _path_for_mime_type(Path(output_file_name), final_mime_type)
    output_audio_file.parent.mkdir(parents=True, exist_ok=True)
    output_audio_file.write_bytes(audio_bytes)

    output_metadata_file = _metadata_path_for_output(output_audio_file)
    metadata = {
        "article_url": article_url,
        "title": article.title,
        "published_date": (
            article.published_date.isoformat() if article.published_date else None
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    output_metadata_file.write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    log.info("AUDIO SAVED", output_file_name=str(output_audio_file))
    log.info("METADATA SAVED", output_file_name=str(output_metadata_file))


def _generate_audio_with_gemini_sdk(script: str) -> tuple[bytes, str]:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise click.ClickException("GOOGLE_API_KEY is not set")

    genai_module = importlib.import_module("google.genai")
    types_module = importlib.import_module("google.genai.types")

    client = genai_module.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=f"A concise, clear podcast narrator:\n\n{script}",
        config=types_module.GenerateContentConfig(response_modalities=["AUDIO"]),
    )

    audio_bytes, mime_type = _extract_audio_bytes(response)
    if not audio_bytes:
        raise click.ClickException("Gemini TTS response did not include audio bytes")
    return audio_bytes, mime_type


def _extract_audio_bytes(response: object) -> tuple[bytes, str]:
    # SDK objects vary across versions, so handle object and dict-style payloads.
    candidates = getattr(response, "candidates", None)
    if candidates is None and isinstance(response, dict):
        candidates = response.get("candidates")

    for candidate in candidates or []:
        content = getattr(candidate, "content", None)
        if content is None and isinstance(candidate, dict):
            content = candidate.get("content")

        parts = getattr(content, "parts", None)
        if parts is None and isinstance(content, dict):
            parts = content.get("parts")

        for part in parts or []:
            inline_data = getattr(part, "inline_data", None)
            if inline_data is None and isinstance(part, dict):
                inline_data = part.get("inlineData") or part.get("inline_data")

            if inline_data is None:
                continue

            data = getattr(inline_data, "data", None)
            if data is None and isinstance(inline_data, dict):
                data = inline_data.get("data")

            mime_type = getattr(inline_data, "mime_type", None)
            if mime_type is None:
                mime_type = getattr(inline_data, "mimeType", None)
            if mime_type is None and isinstance(inline_data, dict):
                mime_type = inline_data.get("mimeType") or inline_data.get("mime_type")

            if isinstance(data, bytes):
                return data, str(mime_type or "")
            if isinstance(data, str):
                return base64.b64decode(data), str(mime_type or "")

    return b"", ""


def _pcm_l16_to_wav_bytes(audio_bytes: bytes, mime_type: str) -> bytes:
    sample_rate = 24000
    parts = [part.strip() for part in mime_type.split(";")]
    for part in parts:
        if part.startswith("rate="):
            try:
                sample_rate = int(part.split("=", 1)[1])
            except ValueError:
                pass

    with io.BytesIO() as wav_io:
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # L16 = 16-bit PCM
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_bytes)
        return wav_io.getvalue()


def _path_for_mime_type(output_file_name: Path, mime_type: str) -> Path:
    expected_extension = _extension_for_mime_type(mime_type)
    if not expected_extension:
        return output_file_name

    current_extension = output_file_name.suffix.lower()
    if current_extension == expected_extension:
        return output_file_name

    return output_file_name.with_suffix(expected_extension)


def _metadata_path_for_output(output_audio_file: Path) -> Path:
    return output_audio_file.with_suffix(".json")


def _extension_for_mime_type(mime_type: str) -> str:
    lower = mime_type.lower()
    if "audio/wav" in lower or "audio/x-wav" in lower:
        return ".wav"
    if "audio/mpeg" in lower or "audio/mp3" in lower:
        return ".mp3"
    if "audio/flac" in lower:
        return ".flac"
    if "audio/ogg" in lower:
        return ".ogg"
    return ""
