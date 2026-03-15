import shutil
import sys
from pathlib import Path
from urllib.request import urlopen

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
    "output_path",
    "-o",
    "--output-path",
    default="output.mp3",
    help="Path to save the output audio file.",
)
@click.option(
    "persona",
    "-p",
    "--persona",
    default="A concise, clear podcast narrator",
    help="Persona/style prompt used by TTS generation.",
)
def main(article_url: str, output_path: str, persona: str):
    log.info("START UP", article_url=article_url)

    # get title, published date and content from article

    log.info("SCRIPT GENERATION")
    try:
        response = b.ExtractArticle(url=article_url)
    except Exception as exc:
        raise click.ClickException(f"Failed to extract article script: {exc}") from exc

    log.debug("SCRIPT GENERATED", script=response.script)
    log.info("AUDIO GENERATION")

    # send content to TTS endpoint and get audio file URL
    try:
        audio_url = b.GeneratePodcastAudio(script=response.script, persona=persona)
    except Exception as exc:
        raise click.ClickException(f"Failed to generate podcast audio: {exc}") from exc

    log.debug("AUDIO GENERATED", audio_url=audio_url)

    # download audio file and save to output path
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    _download_file(audio_url, output_file)
    log.info("AUDIO SAVED", output_path=output_path)


def _download_file(url: str, destination: Path) -> None:
    try:
        with urlopen(url, timeout=60) as response, destination.open("wb") as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as exc:
        raise click.ClickException(
            f"Failed to download audio from {url}: {exc}"
        ) from exc
