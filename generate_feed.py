from datetime import datetime, timezone
import re
import xml.etree.ElementTree as ET
import feedparser

# Offizieller Feed der Amtlichen Sammlung (AS)
AS_FEED_URL = "https://www.fedlex.admin.ch/feed/as/de"
feed = feedparser.parse(AS_FEED_URL)

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

# Breiterer Filter:
# 1. Erkennt "SR 8", "SR 8xx", "(SR 8xx.xx)"
# 2. Erkennt typische Gesetzeskürzel aus SR 8 (Arbeit, Gesundheit, Heilmittel, Sozialversicherungen)
sr8_pattern = re.compile(
    r"(\bSR\s*8\d{0,2}(\.\d+)*\b|\b(KVG|BVG|AVIG|UVG|IVG|AHVG|ELG|ArG|HMG|MepV|EpG|StHG)\b)",
    re.IGNORECASE,
)

matched_items = 0
for entry in feed.entries:
    # Sucht in Titel, Kurzbeschreibung und Link-URL
    text_corpus = f"{entry.title} {entry.get('summary', '')} {entry.link}"

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

# Fallback: Falls aktuell gar kein SR-8-Erlass im AS-Feed ist, einen Info-Eintrag setzen,
# damit Outlook den Feed sofort akzeptiert und nicht über eine leere Datei stolpert.
if matched_items == 0:
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = (
        "SR-8 Monitor aktiv - Aktuell keine offenen Änderungen in der AS"
    )
    ET.SubElement(item, "link").text = (
        "https://www.fedlex.admin.ch/de/cc/internal-law/8"
    )
    ET.SubElement(item, "description").text = (
        "Der Filter läuft fehlerfrei. Sobald die Bundeskanzlei neue Erlasse zu SR 8 publiziert, erscheinen sie hier."
    )
    ET.SubElement(item, "guid").text = (
        "sr8-initial-status-" + datetime.now(timezone.utc).strftime("%Y%m%d")
    )
    ET.SubElement(item, "pubDate").text = datetime.now(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

tree = ET.ElementTree(rss)
tree.write("sr8_feed.xml", encoding="utf-8", xml_declaration=True)
print(f"Abgeschlossen: {matched_items} Treffer erfasst (oder Status gesetzt).")
