import xml.etree.ElementTree as ET  # nosec
from datetime import datetime, timezone
from email.utils import format_datetime
from functools import cached_property
from html import escape

def generate_rss_feed(episodes: list) -> str:
    """Generate an RSS feed from a list of episode metadata."""
    channel = ET.SubElement(self.rss, "channel")

    ET.SubElement(channel, "title").text = self.title
    ET.SubElement(channel, "description").text = self.description
    ET.SubElement(channel, "link").text = self.host_url

    # Add atom:link with rel="self"
    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", self.feed_url)
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for episode in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = episode["title"]
        ET.SubElement(item, "description").text = episode["description"]
        ET.SubElement(item, "link").text = episode["audio_url"]
        ET.SubElement(item, "guid").text = episode["slug"]


    return rss_feed