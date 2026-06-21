from datetime import datetime
import xml.etree.ElementTree as ET  # nosec

ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
ET.register_namespace("itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")


def generate_rss_feed(
    episodes: list, title: str, description: str, host_url: str, feed_url: str
) -> str:
    """Generate a valid, iTunes-compliant RSS feed from episode metadata."""
    # Create root with both Atom and iTunes namespaces
    rss = ET.Element(
        "rss",
        {
            "version": "2.0",
            "xmlns:atom": "http://www.w3.org/2005/Atom",
            "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        },
    )

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    # Core Channel Metadata
    ET.SubElement(channel, "title").text = title
    ET.SubElement(channel, "description").text = description
    ET.SubElement(channel, "link").text = host_url
    ET.SubElement(channel, "language").text = "en-us"

    # Self-referencing Atom link
    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", feed_url)
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    # Process Episodes
    for episode in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = episode["title"]
        ET.SubElement(item, "description").text = episode.get(
            "description", description
        )
        ET.SubElement(item, "link").text = episode["audio_url"]

        # GUID should ideally have isPermaLink="false" if it's just a raw URL string
        guid = ET.SubElement(item, "guid", {"isPermaLink": "false"})
        guid.text = episode["audio_url"]

        # CRITICAL: The enclosure tag tells podcast apps where the audio file is
        ET.SubElement(
            item,
            "enclosure",
            {
                "url": episode["audio_url"],
                "type": episode.get(
                    "mime_type", "audio/mpeg"
                ),
            },
        )

        # Handle Publication Date (Expects RFC 2822 format string)
            # %z handles timezone, %a %d %b %Y %H:%M:%S is standard RFC 2822
        ET.SubElement(item, "pubDate").text = datetime.fromisoformat(episode["added"]).strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )

    return ET.tostring(
        rss, encoding="utf-8", xml_declaration=True
    ).decode("utf-8")
