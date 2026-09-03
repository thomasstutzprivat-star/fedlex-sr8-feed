import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import re
import feedparser

# Offizieller Feed der Amtlichen Sammlung (AS)
AS_FEED_URL = "https://www.fedlex.admin.ch/feed/as/de"
feed = feedparser.parse(AS_FEED_URL)

# RSS 2.0 Wurzelstruktur aufbauen
rss = ET.Element(
    "rss", version="2.0", attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"}
)
channel = ET.SubElement(rss, "channel")

ET.SubElement(channel, "title").text = (
    "Fedlex: SR 8 Gesundheit - Arbeit - Soziale Sicherheit"
)
ET.SubElement(channel, "link").text = (
    "https://www.fedlex.admin.ch/de/cc/internal-law/8"
)
ET.SubElement(channel, "description").text = (
    "Gefilterte Amtliche Sammlung für den Bereich SR 8"
)
ET.SubElement(channel, "lastBuildDate").text = datetime.now(
    timezone.utc
).strftime("%a, %d %b %Y %H:%M:%S GMT")

# Erkennt SR-Zahlen beginnend mit 8 (z. B. SR 8, SR 81, SR 812.21, SR 832.10)
sr8_pattern = re.compile(r"\bSR\s*8\d{0,2}(\.\d+)*\b", re.IGNORECASE)

matched_items = 0
for entry in feed.entries:
    text_corpus = f"{entry.title} {entry.get('summary', '')}"

    if sr8_pattern.search(text_corpus):
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = entry.title
        ET.SubElement(item, "link").text = entry.link
        ET.SubElement(item, "description").text = entry.get(
            "summary", entry.title
        )
        ET.SubElement(item, "guid").text = entry.get("id", entry.link)
        if "published" in entry:
            ET.SubElement(item, "pubDate").text = entry.published
        matched_items += 1

tree = ET.ElementTree(rss)
tree.write("sr8_feed.xml", encoding="utf-8", xml_declaration=True)
print(
    f"Erfolg: {matched_items} relevante Erlasse nach sr8_feed.xml geschrieben."
)
