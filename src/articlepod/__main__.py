from datetime import datetime
import asyncio
import json
import os
from urllib.parse import urljoin

import click

from .page import get_page_html
from .article import generate_slug, generate_script as episode_generate_script
from .rss import generate_rss_feed


def generate_now():
    """Return the current datetime."""
    return datetime.now()


@click.group()
def page():
    pass


@click.group()
def cli():
    pass


cli.add_command(page)


@click.group()
def video():
    pass


cli.add_command(video)


@cli.group()
def article():
    pass


@page.command()
@click.argument("url", type=str)
def get_html(url: str):
    """Get HTML for a page from a URL."""
    html = asyncio.run(get_page_html(url))
    click.echo(html)


@article.command(name="generate-meta")
@click.argument("article_json", type=click.Path(exists=True))
@click.argument("bucket_uri", type=str)
def generate_article_meta(article_json: str, bucket_uri: str):
    """Generate episode metadata from an article JSON file."""
    # Load the article JSON
    with open(article_json, "r") as f:
        article_data = json.load(f)

    now = generate_now()

    slug = generate_slug(article_data.get("title"), now)

    description = f"""
    <b>Title:</b> {article_data.get("title")}<br>
    <b>URL:</b> <a href="{article_data.get("source")}">{article_data.get("source")}</a><br>
    <b>Description:</b> {article_data.get("description", "")}<br>
    """

    # Generate episode metadata
    episode_meta = {
        "title": article_data.get("title"),
        "source_url": article_data.get("source"),
        "added": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "slug": slug,
        "audio_url": urljoin(bucket_uri, f"{slug}.mp3"),
        "description": description,
    }

    click.echo(json.dumps(episode_meta, ensure_ascii=False))


@article.command()
@click.argument("article_json", type=click.Path(exists=True))
def generate_script(article_json: str):
    """Generate episode script from an article JSON file."""
    with open(article_json, "r") as f:
        article_data = json.load(f)

    click.echo(episode_generate_script(article_data))


@video.command(name="generate-meta")
@click.argument("video_json", type=click.Path(exists=True))
@click.argument("bucket_uri", type=str)
def generate_video_meta(video_json: str, bucket_uri: str):
    """Generate episode metadata from a video JSON file."""
    # Load the video JSON
    with open(video_json, "r") as f:
        video_data = json.load(f)

    now = generate_now()

    slug = generate_slug(video_data.get("title"), now)

    description = f"""
    <b>Title:</b> {video_data.get("fulltitle")}<br>
    <b>URL:</b> <a href="{video_data.get("source")}">{video_data.get("source")}</a><br>
    <b>Description:</b> {video_data.get("description", "")}<br>
    """

    # Generate episode metadata
    episode_meta = {
        "title": video_data.get("fulltitle"),
        "source_url": video_data.get("source"),
        "added": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "slug": slug,
        "audio_url": urljoin(bucket_uri, f"{slug}.mp3"),
        "thumbnail": video_data.get("thumbnail"),
        "description": description,
    }

    click.echo(json.dumps(episode_meta, ensure_ascii=False))


@cli.group()
def rss():
    pass


@rss.command()
@click.argument("episode_dir", type=click.Path(exists=True))
@click.option(
    "--host_url",
    default="https://yamatt.github.io/articlepod",
    type=str,
    help="The URL of the host site.",
)
@click.option(
    "--episodes",
    default=10,
    type=int,
    help="Number of episodes to include in the RSS feed.",
)
def generate_rss(episode_dir: str, host_url: str, episodes: int = 10):
    """Generate RSS feed from episode directory."""
    episodes = sorted(
        [
            json.load(open(os.path.join(episode_dir, f)))
            for f in os.listdir(episode_dir)
            if os.path.isfile(os.path.join(episode_dir, f)) and f.endswith(".json")
        ],
        key=lambda x: x["added"],
        reverse=True,
    )[
        :episodes
    ]  # Get the specified number of most recent episodes

    description = f"A podcast about interesting articles."

    click.echo(
        generate_rss_feed(
            episodes, "Articlepod", description, host_url, f"{host_url}/rss.xml"
        )
    )


if __name__ == "__main__":
    cli()
