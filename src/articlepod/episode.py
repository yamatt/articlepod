from datetime import datetime

from .baml_client import b

def generate_slug(title: str, now: datetime) -> str:
    """Generate a slug from the given title."""
    slug = title.lower().replace(" ", "-")
    return f"{now.strftime('%Y-%m-%dT%H-%M-%S')}-{slug}"

def generate_script(article_data: dict) -> str:
    result = b.GeneratePodcastScript(
        title=article_data["title"],
        content=article_data["text"]
    )

    return result
