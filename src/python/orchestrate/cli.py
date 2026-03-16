import json
from datetime import datetime, timezone

import click

from .exceptions import APIKeyException, AudioTypeException
from .logger import log
from .tts import TTS

from baml_client import b  # type: ignore[import-not-found]


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

    audio_bytes, mime_type = _generate_audio_with_gemini_sdk(article.script)

    log.debug("AUDIO GENERATED", bytes=len(audio_bytes), mime_type=mime_type)

    if mime_type and "audio/l16" in mime_type.lower():
        # Gemini preview TTS often returns raw PCM. Wrap to WAV for compatibility.
        audio_bytes = _pcm_l16_to_wav_bytes(audio_bytes, mime_type)
        log.info("AUDIO FORMAT NORMALIZED", normalized_to="audio/wav")
    else:
        raise AudioTypeException(f"Unrecognised audio mime type: {mime_type}")

    # Write audio file and metadata JSON using the same base file name.
    output_audio_file_path = f"./{output_file_name}.{TTS.AUDIO_MIME_TYPE_EXTENSIONS.get(mime_type, 'dat')}"

    with open(output_audio_file_path, "wb") as output_audio_file:
        output_audio_file.write_bytes(audio_bytes)
        
    output_metadata_file_path = f"./{output_file_name}.json"

    metadata = {
        "article_url": article_url,
        "title": article.title,
        "published_date": (
            article.published_date.isoformat() if article.published_date else None
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(output_metadata_file_path, "w") as output_metadata_file:
        output_metadata_file.write_text(
            json.dumps(metadata)
        )

    log.info("OUTPUT SAVED", output_audio_file_path=output_audio_file_path, output_metadata_file_path=output_metadata_file_path)


