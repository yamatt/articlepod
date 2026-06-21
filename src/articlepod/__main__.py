from datetime import datetime
import json
import os
from urllib.parse import urljoin

import click

from .episode import generate_slug, generate_script as episode_generate_script
from .rss import generate_rss_feed

now = datetime.now()

@click.group()
def cli():
    pass

@cli.group()
def episode():
    pass

@episode.command()
@click.argument("article_json", type=click.Path(exists=True))
@click.argument("bucket_uri", type=str)
def generate_meta(article_json: str, bucket_uri: str):
    """Generate episode metadata from an article JSON file."""
    # Load the article JSON
    with open(article_json, 'r') as f:
        article_data = json.load(f)

    slug = generate_slug(article_data.get("title"), now)

    # Generate episode metadata
    episode_meta = {
        "title": article_data.get("title"),
        "added": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "slug": slug,
        "audio_url": urljoin(bucket_uri, f"{slug}.mp3"),
    }

    click.echo(json.dumps(episode_meta, ensure_ascii=False))

@episode.command()
@click.argument("article_json", type=click.Path(exists=True))
def generate_script(article_json: str):
    """Generate episode script from an article JSON file."""
    with open(article_json, 'r') as f:
        article_data = json.load(f)

    click.echo(episode_generate_script(article_data))

@cli.group()
def rss():
    pass

@rss.command()
@click.argument("episode_dir", type=click.Path(exists=True))
def generate_rss(episode_dir: str):
    """Generate RSS feed from episode directory."""
    episodes = [
        json.load(open(os.path.join(episode_dir, f)))
        for f in os.listdir(episode_dir)
        if os.path.isfile(os.path.join(episode_dir, f)) and f.endswith(".json")
    ]

    click.echo(generate_rss_feed(episodes, "Articlepod", "A podcast about interesting articles.", "https://github.com/yamatt/articlepod", "https://yamatt.github.io/articlepod/rss.xml"))


if __name__ == "__main__":
    cli()
