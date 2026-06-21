import xml.etree.ElementTree as ET  # nosec

def generate_rss_feed(episodes: list, title: str, description: str, host_url: str, feed_url: str) -> str:
    """Generate an RSS feed from a list of episode metadata."""
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = title
    ET.SubElement(channel, "description").text = description
    ET.SubElement(channel, "link").text = host_url

    # Add atom:link with rel="self"
    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", feed_url)
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for episode in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = episode["title"]
        ET.SubElement(item, "description").text = episode["description"]
        ET.SubElement(item, "link").text = episode["audio_url"]
        ET.SubElement(item, "guid").text = episode["slug"]


    return rss