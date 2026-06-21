from datetime import datetime
import re

from .baml_client import b

slug_regex = re.compile(r"[^a-z0-9\-]")

def generate_slug(title: str, now: datetime) -> str:
    """Generate a slug from the given title."""
    slug = slug_regex.sub("-", title.lower())
    return f"{now.strftime('%Y-%m-%dT%H-%M-%S')}-{slug}"

def generate_script(article_data: dict) -> str:
    result = b.GeneratePodcastScript(
        title=article_data["title"],
        content=article_data["text"]
    )

    return result
