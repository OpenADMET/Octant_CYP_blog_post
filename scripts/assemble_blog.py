#!/usr/bin/env python3
"""Assemble cyp-blog-post.qmd from Google Doc HTML export + figure includes.

Usage: python scripts/assemble_blog.py

Reads:
    data/raw/blog_post_text.html     (HTML export from Google Docs)
Writes:
    cyp-blog-post.qmd
"""

import csv
import hashlib
import re
from datetime import date
from pathlib import Path
from urllib.parse import unquote

from lxml import html

# ---------------------------------------------------------------------------
# Locate repo root via .here marker
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
assert (REPO_ROOT / ".here").exists(), f"Cannot find .here marker in {REPO_ROOT}"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

YAML_HEADER = """\
---
title: "Building the OpenADMET Data Engine"
date: "March 2, 2026"
format:
  html:
    output-file: index.html
---"""

AUTHOR_LINE = (
    ":::{.doc-authors}\n"
    "Robert Warneford-Thomson [{{< ai orcid color=#a6ce39 >}}](https://orcid.org/0000-0002-4521-0568), "
    "Steven Edgar, "
    "Hugo MacDermott-Opeskin [{{< ai orcid color=#a6ce39 >}}](https://orcid.org/0000-0002-7393-7457), "
    "Naomi Handly [{{< ai orcid color=#a6ce39 >}}](https://orcid.org/0009-0007-1480-6741), "
    "Pat Walters [{{< ai orcid color=#a6ce39 >}}](https://orcid.org/0000-0003-2860-7958), "
    "Sri Kosuri [{{< ai orcid color=#a6ce39 >}}](https://orcid.org/0000-0002-4661-0600)"
    "\n:::"
)

SETUP_INCLUDES = [
    "{{< include post/_setup_r.qmd >}}",
    "",
    "{{< include post/_setup_python.qmd >}}",
]

# Short figure titles for the ToC sidebar (overrides auto-extracted titles).
TOC_SHORT_TITLES = {
    "1": "CYP screening overview",
    "2": "CYP3A4 vs CYP2J2 reactivity",
    "3": "CYP3A4 inhibition vs reactivity",
    "4": "CYP assay development",
    "5": "Built-in quality checks",
    "6": "Expanding chemical coverage",
    "7": "Clearance & TDI assays",
}

# Map figure numbers to their include syntax.
FIGURE_INCLUDES = {
    "1": "{{< include post/figures/figure_1.qmd >}}",
    "2": "{{< include post/figures/figure_2.qmd >}}",
    "3": "{{< include post/figures/figure_3.qmd >}}",
    "4": "{{< include post/figures/figure_4.qmd >}}",
    "5": "![](post/Figure_5.png)",
    "6": "{{< include post/figures/figure_6.qmd >}}",
    "7": "{{< include post/figures/figure_7.qmd >}}",
}

# ---------------------------------------------------------------------------
# Load citation metadata
# ---------------------------------------------------------------------------

cite_tooltips: dict[str, str] = {}
cite_urls: dict[str, str] = {}

citations_path = REPO_ROOT / "data" / "citations.tsv"
if citations_path.exists():
    with open(citations_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            num = row["number"]
            cite_tooltips[num] = row.get("tooltip", "")
            cite_urls[num] = row.get("url", "")
    print(f"Loaded {len(cite_tooltips)} citations")
else:
    print("No citations.tsv found — tooltips will be skipped")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def unwrap_google_url(url: str) -> str:
    """Unwrap Google redirect URLs to the actual destination."""
    if url.startswith("https://www.google.com/url?"):
        m = re.search(r"[?&]q=([^&]+)", url)
        if m:
            return unquote(m.group(1))
    return url


def format_citation_link(text: str, href: str) -> str:
    """Format a citation link with hover tooltip from citations.tsv."""
    num = text.strip().strip("[]")
    display = text.strip()
    tooltip = cite_tooltips.get(num, "")
    if tooltip:
        tooltip_escaped = tooltip.replace('"', "&quot;")
        return f'<a href="{href}" class="cite-tip" data-tooltip="{tooltip_escaped}">{display}</a>'
    return f"[{display}]({href})"


def _wrap_bold_italic(inner: str, is_bold: bool, is_italic: bool) -> str:
    """Wrap text in bold/italic markers, moving leading/trailing whitespace outside."""
    if not (is_bold or is_italic):
        return inner

    # Google Docs often includes leading/trailing whitespace inside styled
    # spans; move it outside the markers so bold/italic renders correctly.
    leading = ""
    trailing = ""

    m = re.match(r"^([\s\u00a0]+)", inner)
    if m:
        leading = m.group(1)
        inner = inner[m.end():]

    m = re.search(r"([\s\u00a0]+)$", inner)
    if m:
        trailing = m.group(1)
        inner = inner[:m.start()]

    if not inner:
        # The span was whitespace-only; don't emit empty markers
        return leading + trailing

    if is_bold and is_italic:
        inner = f"***{inner}***"
    elif is_bold:
        inner = f"**{inner}**"
    elif is_italic:
        inner = f"*{inner}*"

    return leading + inner + trailing


def span_to_md(element) -> str:
    """Convert a <span> element (possibly containing <a> tags) to markdown."""
    parts: list[str] = []
    for child in element:
        # Text before any child element
        pass
    # lxml models text differently: element.text + each child's tail
    if element.text:
        parts.append(element.text)
    for child in element:
        tag = child.tag
        if tag == "a":
            href = unwrap_google_url(child.get("href", ""))
            text = child.text_content()
            if href.startswith("#cmnt"):
                pass  # skip comment anchors
            elif re.match(r"^\[?\d+\]?$", text.strip()):
                parts.append(format_citation_link(text, href))
            else:
                parts.append(f"[{text}]({href})")
        else:
            parts.append(child.text_content())
        # Tail text after the child element
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def node_to_md(node) -> str:
    """Convert an HTML paragraph/element to markdown text.

    Walks child nodes, converting <a> to [text](url),
    <span font-weight:700> to **text**, and <span font-style:italic> to *text*.
    """
    parts: list[str] = []

    # Leading text content of the node itself
    if node.text:
        parts.append(node.text)

    for child in node:
        tag = child.tag
        style = child.get("style", "")

        if tag == "a":
            href = unwrap_google_url(child.get("href", ""))
            text = child.text_content()
            if href.startswith("#cmnt"):
                pass  # skip comment anchors
            elif re.match(r"^\[?\d+\]?$", text.strip()):
                parts.append(format_citation_link(text, href))
            else:
                parts.append(f"[{text}]({href})")

        elif tag == "span":
            inner = span_to_md(child)
            is_bold = bool(re.search(r"font-weight:\s*700", style))
            is_italic = bool(re.search(r"font-style:\s*italic", style))
            parts.append(_wrap_bold_italic(inner, is_bold, is_italic))

        else:
            parts.append(child.text_content())

        # Tail text after each child element
        if child.tail:
            parts.append(child.tail)

    return "".join(parts).strip()


def li_to_md(li_node) -> str:
    """Convert a <li> element to a markdown bullet line."""
    parts: list[str] = []

    if li_node.text:
        parts.append(li_node.text)

    for child in li_node:
        tag = child.tag
        style = child.get("style", "")

        if tag == "span":
            inner = span_to_md(child)
            is_bold = bool(re.search(r"font-weight:\s*700", style))
            is_italic = bool(re.search(r"font-style:\s*italic", style))
            parts.append(_wrap_bold_italic(inner, is_bold, is_italic))

        elif tag == "a":
            href = unwrap_google_url(child.get("href", ""))
            text = child.text_content()
            if not href.startswith("#cmnt"):
                if re.match(r"^\[?\d+\]?$", text.strip()):
                    parts.append(format_citation_link(text, href))
                else:
                    parts.append(f"[{text}]({href})")

        else:
            parts.append(child.text_content())

        if child.tail:
            parts.append(child.tail)

    return "- " + "".join(parts).strip()


# Abbreviations that should NOT trigger sentence splitting
_ABBREVIATIONS = re.compile(
    r"(?:[Ee]\.g|[Ii]\.e|[Ee]t al|[Vv]s|[Dd]r|[Mm]r|[Mm]rs|[Mm]s"
    r"|[Nn]o|[Aa]pprox|[Ff]ig|[Rr]ef)\.$"
)


def one_sentence_per_line(text: str) -> str:
    """Split text so each sentence starts on a new line (for readable diffs).

    Avoids splitting inside HTML tags or after common abbreviations.
    """
    # Separate HTML tags from prose so we only split prose segments
    parts = re.split(r"(<[^>]+>)", text)

    result: list[str] = []
    for part in parts:
        if part.startswith("<"):
            result.append(part)
        else:
            result.append(_split_sentences(part))

    return "".join(result)


def _split_sentences(text: str) -> str:
    """Split prose at sentence boundaries, preserving abbreviations."""
    # Match sentence-ending punctuation followed by whitespace
    chunks = re.split(r"([.!?])\s+", text)
    if len(chunks) <= 1:
        return text

    out_parts: list[str] = []
    i = 0
    while i < len(chunks):
        if i + 1 < len(chunks) and chunks[i + 1] in ".!?":
            # chunks[i] is text before punctuation, chunks[i+1] is the punctuation
            segment = chunks[i] + chunks[i + 1]
            # Check if this ends with an abbreviation
            if _ABBREVIATIONS.search(segment):
                # Don't split — rejoin with the next chunk
                if i + 2 < len(chunks):
                    chunks[i + 2] = segment + " " + chunks[i + 2]
                else:
                    out_parts.append(segment)
                i += 2
                continue
            out_parts.append(segment)
            i += 2
        else:
            out_parts.append(chunks[i])
            i += 1

    return "\n".join(out_parts)


# ---------------------------------------------------------------------------
# Parse HTML body into markdown lines
# ---------------------------------------------------------------------------

html_path = REPO_ROOT / "data" / "raw" / "blog_post_text.html"
doc = html.parse(str(html_path))
body = doc.find(".//body")

children = list(body)

out: list[str] = []
skip_header = True
title_seen = False

i = 0
while i < len(children):
    node = children[i]
    tag = node.tag
    text = (node.text_content() or "").strip()

    # Skip Google Docs comment divs at the end
    if tag == "div":
        i += 1
        continue

    # Skip the preamble: first <p> is author note, first <h2> is the title
    if skip_header:
        if tag == "p" and not title_seen:
            i += 1
            continue
        if tag == "h2" and not title_seen:
            title_seen = True
            i += 1
            continue
        if title_seen:
            skip_header = False

    # Skip empty paragraphs
    if tag == "p" and re.match(r"^[\s\u00a0]*$", text):
        i += 1
        continue

    # --- Figure reference lines ---
    if tag == "p" and re.match(r"^(Draft )?Figure \d+:?\s*$", text, re.IGNORECASE):
        fig_num = re.search(r"\d+", text).group()

        # Look ahead past blank <p> elements to find the caption
        j = i + 1
        while (
            j < len(children)
            and children[j].tag == "p"
            and re.match(r"^[\s\u00a0]*$", children[j].text_content() or "")
        ):
            j += 1

        # Extract short title from caption
        fig_title = ""
        if j < len(children):
            cap_text = (children[j].text_content() or "").strip()
            title_match = re.search(
                rf"Figure\s+{fig_num}:\s*(.+?)\.", cap_text
            )
            if title_match:
                fig_title = title_match.group(1).strip()

        short = TOC_SHORT_TITLES.get(fig_num)
        if short:
            toc_label = f"Figure {fig_num}: {short}"
        elif fig_title:
            toc_label = f"Figure {fig_num}: {fig_title}"
        else:
            toc_label = f"Figure {fig_num}"

        include = FIGURE_INCLUDES.get(fig_num)
        if include:
            out.extend([
                "",
                f"#### {toc_label} {{.figure-toc}}",
                "",
                include,
                "",
            ])

        i += 1
        continue

    # --- Figure caption lines (bold prefix, wrapped in fenced div) ---
    if tag == "p" and re.match(r"^\s*Figure \d+:", text):
        md = node_to_md(node)
        # Bold the "Figure N:" prefix if not already bold
        md = re.sub(r"^\*\*(Figure \d+:)\*\*", r"**\1**", md)
        if not md.startswith("**Figure"):
            md = re.sub(r"^(Figure \d+:)", r"**\1**", md)
        md = one_sentence_per_line(md)
        out.extend([":::{.figure-caption}", md, ":::", ""])
        i += 1
        continue

    # --- Headings ---
    m = re.match(r"^h([1-6])$", tag)
    if m:
        level = int(m.group(1))
        prefix = "#" * level
        out.extend(["", f"{prefix} {text}", ""])
        i += 1
        continue

    # --- Lists ---
    if tag == "ul":
        items = node.findall(".//li")
        out.append("")
        for li in items:
            out.append(li_to_md(li))
        out.append("")
        i += 1
        continue

    # --- Regular paragraphs ---
    if tag == "p":
        md = node_to_md(node)

        # Italicize "Note:" lines
        if md.startswith("Note:"):
            md = f"*{md}*"

        md = one_sentence_per_line(md)
        out.extend([md, ""])
        i += 1
        continue

    i += 1


# ---------------------------------------------------------------------------
# Clean up
# ---------------------------------------------------------------------------

# Remove Google Docs comment markers [a], [b], etc. that survived
out = [re.sub(r"\[[a-z]\]", "", line) for line in out]

# Fix bold spans split across punctuation BEFORE collapsing redundant markers.
# "**X**,** Y**" → "**X**, **Y**"  (keep closing **, add space, keep opening **)
out = [re.sub(r"\*\*([,;])\s*\*\*", r"**\1 **", line) for line in out]

# Clean up redundant bold markers (e.g., ****text****)
out = [re.sub(r"\*{4,}", "**", line) for line in out]

# Fix spaces before closing bold/italic markers (e.g., "text **" → "text**")
out = [re.sub(r"\s+(\*{1,3})(?=\s|$)", r"\1", line) for line in out]

# Remove empty bold/italic markers (e.g., "** **" → single space)
out = [re.sub(r"\*{2,3}\s+\*{2,3}", " ", line) for line in out]

# Clean up stray spaces/nbsp before punctuation
out = [re.sub(r"[\s\u00a0]+([,;])", r"\1", line) for line in out]

# Subscript common scientific terms
def apply_subscripts(text: str) -> str:
    text = re.sub(r"\b(p?IC)(50)\b", r"\1<sub>\2</sub>", text)
    text = re.sub(r"\b(EC)(50)\b", r"\1<sub>\2</sub>", text)
    text = re.sub(r"\b([Ll]og)(10|2)\b", r"\1<sub>\2</sub>", text)
    return text


out = [apply_subscripts(line) for line in out]

# Collapse runs of 2+ blank lines to 1
final: list[str] = []
blank_count = 0
for line in out:
    if line == "":
        blank_count += 1
        if blank_count <= 1:
            final.append(line)
    else:
        blank_count = 0
        final.append(line)

# Trim leading/trailing blank lines
while final and final[0] == "":
    final.pop(0)
while final and final[-1] == "":
    final.pop()

# ---------------------------------------------------------------------------
# Content hash (for "last updated" tracking)
# ---------------------------------------------------------------------------

data_dir = REPO_ROOT / "data"
data_files = sorted(data_dir.glob("*.tsv"))
data_hashes = []
for f in data_files:
    md5 = hashlib.md5(f.read_bytes()).hexdigest()
    data_hashes.append(f"{f.name} {md5}")

hash_input = "\n".join(final + ["", "# data file hashes"] + data_hashes) + "\n"
content_hash = hashlib.md5(hash_input.encode()).hexdigest()[:7]

# ---------------------------------------------------------------------------
# Determine "last updated" date
# ---------------------------------------------------------------------------

hash_path = REPO_ROOT / ".content-hash"
prev_hash = None
prev_date = None
if hash_path.exists():
    lines = hash_path.read_text().splitlines()
    if len(lines) >= 1:
        prev_hash = lines[0]
    if len(lines) >= 2:
        prev_date = lines[1]

today_date = date.today().strftime("%B %d, %Y")
if prev_hash == content_hash and prev_date:
    last_updated = prev_date
else:
    last_updated = today_date

# ---------------------------------------------------------------------------
# Assemble final QMD
# ---------------------------------------------------------------------------

version_tag = [
    "::::{.doc-version}",
    f":::{{{'.doc-version-left'}}}\nLast updated: {last_updated}\n:::",
    ":::{.doc-version-right}\nBuilt with ❤️ and [Quarto](https://quarto.org)\n:::",
    "::::",
]

qmd = (
    [YAML_HEADER, ""]
    + SETUP_INCLUDES
    + ["", AUTHOR_LINE, ""]
    + ["{{< include post/figures/banner_drc_animation.qmd >}}", ""]
    + final
    + ["", ""]
    + version_tag
    + [""]
)

out_path = REPO_ROOT / "cyp-blog-post.qmd"
out_path.write_text("\n".join(qmd) + "\n")

# Write content hash + last-updated date to sidecar file
hash_path.write_text(f"{content_hash}\n{last_updated}\n")

print(f"Wrote: {out_path}")
print(f"Content hash: {content_hash}")
print(f"Last updated: {last_updated}")
