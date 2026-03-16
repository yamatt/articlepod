import json
from datetime import datetime, timezone
from pathlib import Path

import click
from baml_client import b  # type: ignore[import-not-found]

from .exceptions import AudioTypeException
from .logger import log
from .tts import TTS


@click.command()
@click.argument("article_url", type=str, required=True)
@click.option(
    "output_file_name",
    "-o",
    "--output-file-name",
    default="output",
    help="File name for output audio and metadata JSON",
)
def main(article_url: str, output_file_name: str):
    log.info("SCRIPT GENERATION", article_url=article_url)

    article = b.ExtractArticle(url=article_url)

    log.info("AUDIO GENERATION", word_count=len(article.script.split()))

    audio_bytes, mime_type = TTS._generate_audio_with_gemini_sdk(article.script)

    log.debug("AUDIO GENERATED", bytes=len(audio_bytes), mime_type=mime_type)

    if mime_type and "audio/l16" in mime_type.lower():
        # Gemini preview TTS often returns raw PCM. Wrap to WAV for compatibility.
        audio_bytes = TTS._pcm_l16_to_wav_bytes(audio_bytes, mime_type)
        mime_type = "audio/wav"
        log.info("AUDIO FORMAT NORMALIZED", normalized_to="audio/wav")
    elif mime_type not in TTS.AUDIO_MIME_TYPE_EXTENSIONS:
        raise AudioTypeException(f"Unrecognised audio mime type: {mime_type}")

    output_audio_file_path = Path(output_file_name)
    extension = TTS.AUDIO_MIME_TYPE_EXTENSIONS[mime_type]
    if output_audio_file_path.suffix.lower() != f".{extension}":
        output_audio_file_path = output_audio_file_path.with_suffix(f".{extension}")
    output_audio_file_path.write_bytes(audio_bytes)

    output_metadata_file_path = _metadata_path_for_output(output_audio_file_path)

    metadata = {
        "article_url": article_url,
        "audio_file": str(output_audio_file_path),
        "mime_type": mime_type,
        "bytes": len(audio_bytes),
        "title": getattr(article, "title", None),
        "published_date": (
            article.published_date.isoformat()
            if getattr(article, "published_date", None)
            else None
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    output_metadata_file_path.write_text(json.dumps(metadata), encoding="utf-8")

    log.info(
        "OUTPUT SAVED",
        output_audio_file_path=str(output_audio_file_path),
        output_metadata_file_path=str(output_metadata_file_path),
    )


def _metadata_path_for_output(output_audio_path: Path) -> Path:
    return output_audio_path.with_suffix(".json")
