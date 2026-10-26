"""On-demand PDF rendering for team-member résumés.

The résumés live in PostgreSQL as plain text (``team_members.resume_en`` /
``resume_fa``) and the public site reads them over the same JSON API as the
About page. Rather than storing a second copy of every résumé as a PDF blob
(which would have to be re-uploaded whenever a text is edited), the file is
rendered on demand from exactly the text the website shows, so the download can
never drift out of sync with the on-page version.

Persian needs two extra steps before it can be drawn. ReportLab lays every
glyph out strictly left-to-right and has no notion of right-to-left scripts, so
each line is first converted to its *presentation forms* (the joined/ligatured
letter shapes) by ``arabic_reshaper`` and then run through the Unicode
bidirectional algorithm by ``python-bidi`` to obtain the visual order. The
result is drawn as ordinary left-to-right text.

Because that visual string is meaningless to a naive line-breaker (its words run
right-to-left), line breaking is done on the *logical* text and each finished
line is converted separately — that keeps word order and letter joining correct
on every line of a wrapped paragraph.
"""

from __future__ import annotations

import io
import logging
import re
from html.parser import HTMLParser
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

logger = logging.getLogger("cloudland.resume_pdf")

# Bundled with the backend image (SIL Open Font License 1.1, see OFL.txt).
FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
REGULAR_FONT = "Vazirmatn"
BOLD_FONT = "Vazirmatn-Bold"

# Page geometry.
MARGIN_X = 18 * mm

# Brand palette, mirroring the About page.
NAVY = colors.HexColor("#101c60")
GOLD = colors.HexColor("#f5a300")
BODY_TEXT = colors.HexColor("#333c52")
MUTED = colors.HexColor("#6b7490")

# A line ending in a period is prose; a short standalone line is a heading.
_HEADING_MAX_LEN = 70
_BULLET_RE = re.compile(r"^\s*[-*•·–—]+\s+(.+)$")

# Résumé layout templates, keyed by the value stored in
# `team_members.resume_template`. These follow the standard résumé sections
# (summary / experience / education / skills) that the admin editor guides the
# author towards; they only change spacing and emphasis, never the content.
#
#   body_size / body_leading — the running text
#   heading_size             — section headings
#   heading_gap              — space before a heading
#   bullet_gap               — space after a list
#   rule                     — a hairline under the header block
TEMPLATES: dict[str, dict[str, float | bool]] = {
    # GitHub-style: roomy, clear section separation. The default.
    "classic": {
        "body_size": 10.5,
        "body_leading": 18,
        "heading_size": 12,
        "heading_gap": 12,
        "bullet_gap": 4,
        "rule": True,
    },
    # Airier, for a one-page summary aimed at recruiters.
    "modern": {
        "body_size": 11,
        "body_leading": 19,
        "heading_size": 13,
        "heading_gap": 16,
        "bullet_gap": 6,
        "rule": True,
    },
    # Denser: fits a long CV onto fewer pages.
    "compact": {
        "body_size": 9.5,
        "body_leading": 15,
        "heading_size": 10.5,
        "heading_gap": 8,
        "bullet_gap": 2,
        "rule": False,
    },
}


# Résumés are written in the rich text editor, so they arrive as HTML. These
# tags carry meaning for the layout and everything else is just inline styling.
_HTML_MARKUP_RE = re.compile(
    r"<\s*/?\s*(p|div|ul|ol|li|h[1-6]|br|hr|blockquote|pre|strong|b|em|i|u|"
    r"span|table|tr|td|th|a|img|code|section|article)\b",
    re.IGNORECASE,
)
_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_PARAGRAPH_TAGS = {"p", "div", "section", "article", "blockquote", "pre"}
_SKIPPED_TAGS = {"style", "script", "head", "title", "meta", "link", "noscript"}




class _ResumeHTMLParser(HTMLParser):
    """Turn rich-text HTML into the ``(kind, lines)`` blocks the PDF wants.

    Headings become headings, list items become bullets (numbered for ``<ol>``),
    and every other block becomes a paragraph. Inline formatting (bold, links,
    spans) contributes its text and is otherwise dropped: a PDF cannot show an
    editor's inline styles, and a résumé does not need them.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, list[str]]] = []
        self._kind: str | None = None
        self._buffer: list[str] = []
        self._skip_depth = 0
        self._list_stack: list[str] = []
        self._item_index = 0

    # -- helpers ------------------------------------------------------------
    def _flush(self) -> None:
        text = "".join(self._buffer).strip()
        self._buffer.clear()
        if not text or self._kind is None:
            self._kind = None
            return
        # A block may contain <br>-separated lines; keep them as lines of the
        # same block so wrapping stays inside one paragraph.
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            self.blocks.append((self._kind, lines))
        self._kind = None

    def _current_prefix(self) -> str:
        """Bullet marker for the item being collected, if inside a list."""
        if not self._list_stack:
            return ""
        if self._list_stack[-1] == "ol":
            self._item_index += 1
            return f"{self._item_index}. "
        return "• "

    # -- HTMLParser ---------------------------------------------------------
    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in _SKIPPED_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return

        if tag in ("ul", "ol"):
            self._flush()
            self._list_stack.append(tag)
            self._item_index = 0
            return

        if tag == "li":
            self._flush()
            self._kind = "bullet"
            self._buffer.append(self._current_prefix())
            return

        if tag in _HEADING_TAGS:
            self._flush()
            self._kind = "heading"
            return

        if tag in _PARAGRAPH_TAGS:
            self._flush()
            self._kind = "para"
            return

        if tag == "br":
            self._buffer.append("\n")
            return

        if tag == "hr":
            self._flush()
            self.blocks.append(("rule", []))
            return

        if tag in ("td", "th"):
            # Tables have no PDF equivalent; keep the cell text on its own line.
            self._flush()
            self._kind = "para"

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _SKIPPED_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return

        if tag in ("ul", "ol"):
            self._flush()
            if self._list_stack:
                self._list_stack.pop()
                self._item_index = 0
            return

        if tag in _HEADING_TAGS or tag in _PARAGRAPH_TAGS or tag == "li":
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._skip_depth or self._kind is None:
            return
        if data.strip():
            self._buffer.append(data)

    def close(self) -> None:
        super().close()
        self._flush()


def looks_like_html(text: str) -> bool:
    """True when the stored résumé is editor HTML rather than plain text."""
    return bool(_HTML_MARKUP_RE.search(text or ""))


def html_to_blocks(html: str) -> list[tuple[str, list[str]]]:
    """Parse résumé HTML into ``(kind, lines)`` blocks.

    Falls back to the plain-text parser for rows written before the editors
    existed, so old résumés keep rendering exactly as they did.
    """
    if not looks_like_html(html):
        return _blocks(html)
    parser = _ResumeHTMLParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception:  # noqa: BLE001 - never fail a download over odd markup
        logger.warning("Could not parse resume HTML; falling back to text", exc_info=True)
        return _blocks(re.sub(r"<[^>]+>", " ", html))
    return parser.blocks or _blocks(re.sub(r"<[^>]+>", " ", html))


class ResumePdfError(RuntimeError):
    """Raised when a PDF cannot be produced (missing font, unusable résumé)."""


_fonts_ready = False


def _register_fonts() -> None:
    """Register the bundled Vazirmatn faces with ReportLab (once per process)."""
    global _fonts_ready
    if _fonts_ready:
        return

    faces = {
        REGULAR_FONT: FONT_DIR / "Vazirmatn-Regular.ttf",
        BOLD_FONT: FONT_DIR / "Vazirmatn-Bold.ttf",
    }
    for name, path in faces.items():
        if not path.is_file():
            raise ResumePdfError(f"PDF font is missing from the image: {path.name}")
        pdfmetrics.registerFont(TTFont(name, str(path)))

    pdfmetrics.registerFontFamily(
        REGULAR_FONT,
        normal=REGULAR_FONT,
        bold=BOLD_FONT,
        italic=REGULAR_FONT,
        boldItalic=BOLD_FONT,
    )
    _fonts_ready = True


# --------------------------------------------------------------- text utils --

def _escape(text: str) -> str:
    """Escape the three characters ReportLab's mini-markup treats as markup."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _display(text: str) -> str:
    """Presentation forms + bidi reordering (visual, left-to-right draw order)."""
    return get_display(arabic_reshaper.reshape(text))


def _wrap(text: str, font: str, size: float, width: float, rtl: bool) -> list[str]:
    """Greedy word wrap, applied to logical text and shaped per finished line.

    Wrapping *after* bidi would be wrong: in the visual string the words run
    right-to-left, so breaking it on spaces would reverse the word order of
    every line. Instead the break decision is made while reading the text in
    its natural direction, and only the completed line is converted for drawing.
    """
    words = [word for word in text.split() if word]
    if not words:
        return []

    # A finished line is handed to the bidi pass whole, never word by word:
    # reversing each word separately would also reverse the order of embedded
    # Latin runs (a name like "Soroush Rahimi" would come out reversed).
    def shape(line: str) -> str:
        return _display(line) if rtl else line

    def fits(text: str) -> bool:
        # Measure the logical string: bidi reordering moves whole runs around
        # but does not change how much width they need.
        return pdfmetrics.stringWidth(text, font, size) <= width

    # A single word can be wider than the whole line (a long URL, or a résumé
    # pasted without spaces). ReportLab cannot break a word on its own, so the
    # overflow would run off the page: split it at character boundaries instead.
    def split_long_word(word: str) -> list[str]:
        pieces: list[str] = []
        current = ""
        for char in word:
            if current and not fits(current + char):
                pieces.append(current)
                current = char
            else:
                current += char
        if current:
            pieces.append(current)
        return pieces

    lines: list[str] = []
    current = ""
    for word in words:
        if not fits(word):
            # Flush what is pending, then emit the broken-up word on its own.
            if current:
                lines.append(shape(current))
                current = ""
            lines.extend(shape(piece) for piece in split_long_word(word))
            continue
        candidate = f"{current} {word}".strip()
        if current and not fits(candidate):
            lines.append(shape(current))
            current = word
        else:
            current = candidate
    if current:
        lines.append(shape(current))
    return lines


def _looks_like_heading(block: list[str]) -> bool:
    text = " ".join(block).strip()
    if not text or len(text) > _HEADING_MAX_LEN:
        return False
    if text.endswith((".", "،", ",", "؛", ";")):
        return False
    return True


def _blocks(text: str) -> list[tuple[str, list[str]]]:
    """Split a plain-text résumé into ``(kind, lines)`` blocks.

    ``kind`` is ``heading``, ``bullet`` or ``para``. Résumés are stored as free
    text by the admins, so the parser stays deliberately forgiving: a blank-line
    separated block of bullet lines becomes a list, a short standalone line
    becomes a heading, everything else is prose.
    """
    blocks: list[tuple[str, list[str]]] = []
    for chunk in re.split(r"\n\s*\n", text.strip()):
        lines = [line.rstrip() for line in chunk.splitlines() if line.strip()]
        if not lines:
            continue
        matches = [_BULLET_RE.match(line) for line in lines]
        if all(matches):
            # Keep a canonical marker in the text so plain-text and HTML résumés
            # reach the renderer in exactly the same shape.
            blocks.append(("bullet", [f"• {match.group(1)}" for match in matches]))
        elif len(lines) == 1 and _looks_like_heading(lines):
            blocks.append(("heading", lines))
        else:
            blocks.append(("para", lines))
    return blocks


# ------------------------------------------------------------------ styles --

def _styles(rtl: bool, metrics: dict) -> dict[str, ParagraphStyle]:
    align = TA_RIGHT if rtl else TA_LEFT
    body = ParagraphStyle(
        "body",
        fontName=REGULAR_FONT,
        fontSize=metrics["body_size"],
        leading=metrics["body_leading"],
        alignment=align,
        textColor=BODY_TEXT,
        spaceAfter=0,
    )
    return {
        "name": ParagraphStyle(
            "name",
            parent=body,
            fontName=BOLD_FONT,
            fontSize=19,
            leading=25,
            textColor=NAVY,
        ),
        "role": ParagraphStyle(
            "role", parent=body, fontSize=11.5, leading=16, textColor=GOLD
        ),
        "contact": ParagraphStyle(
            "contact", parent=body, fontSize=9, leading=14, textColor=MUTED
        ),
        "heading": ParagraphStyle(
            "heading",
            parent=body,
            fontName=BOLD_FONT,
            fontSize=metrics["heading_size"],
            leading=metrics["heading_size"] + 5,
            textColor=NAVY,
            spaceBefore=metrics["heading_gap"],
            spaceAfter=4,
        ),
        "body": body,
        "bullet": ParagraphStyle(
            "bullet",
            parent=body,
            # Persian bullets hang off the right edge, English ones the left.
            leftIndent=0 if rtl else 12,
            rightIndent=12 if rtl else 0,
        ),
    }


    for word in words:
        if rtl:
            # Prepend: the visual line reads right-to-left, so the next logical
            # word goes to the front rather than the back.
            shaped = _display(word)

# ------------------------------------------------------------------ builder --

def _contact_line(member: dict, rtl: bool) -> str:
    """The profile links on one line; the bidi pass keeps each URL intact."""
    raw: list[str] = []
    for key in ("website_url", "linkedin_url", "github_url"):
        url = (member.get(key) or "").strip()
        if url:
            raw.append(url)
    if not raw:
        return ""
    if rtl:
        raw.reverse()
    joined = "  •  ".join(raw)
    return _display(joined) if rtl else joined


def _footer(canvas, doc, rtl: bool) -> None:
    """Page number, drawn on every page."""
    canvas.saveState()
    canvas.setFont(REGULAR_FONT, 8)
    canvas.setFillColor(MUTED)
    label = f"— {doc.page} —"
    if rtl:
        canvas.drawRightString(A4[0] - MARGIN_X, 12 * mm, label)
    else:
        canvas.drawString(MARGIN_X, 12 * mm, label)
    canvas.restoreState()


def build_resume_pdf(member: dict, lang: str) -> bytes:
    """Render ``member``'s résumé as PDF bytes.

    ``lang`` is ``fa`` for Persian (right-to-left, shaped) or ``en`` for English
    (left-to-right, as stored). The layout follows ``member['resume_template']``
    — the GitHub-style ``classic`` single column, a roomier ``modern`` variant,
    or a dense ``compact`` one — and falls back to ``classic``.

    Raises :class:`ResumePdfError` when the résumé for that language is empty or
    the bundled font is unavailable.
    """
    if lang not in ("fa", "en"):
        raise ResumePdfError(f"Unsupported language: {lang!r}")

    _register_fonts()

    text = (member.get(f"resume_{lang}") or "").strip()
    if not text:
        raise ResumePdfError(
            f"Team member {member.get('id')} has no {lang.upper()} résumé"
        )

    rtl = lang == "fa"
    template = str(member.get("resume_template") or "classic").strip().lower()
    if template not in TEMPLATES:
        template = "classic"
    metrics = TEMPLATES[template]

    # The Latin spelling heads the English résumé and the Persian one heads the
    # Persian résumé, and the same applies to the job title. Both fall back to
    # the original for rows that predate the columns.
    if lang == "en":
        person_name = (member.get("full_name_en") or member.get("full_name") or "").strip()
        job_title = (member.get("role_en") or member.get("role") or "").strip()
    else:
        person_name = (member.get("full_name") or "").strip()
        job_title = (member.get("role") or "").strip()

    styles = _styles(rtl, metrics)
    content_width = A4[0] - 2 * MARGIN_X

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_X,
        bottomMargin=20 * mm,
        title=f"{person_name} — {'رزومه' if rtl else 'Resume'}",
        author=person_name or "CloudLand",
    )

    story: list = []

    def add(value: str, style: ParagraphStyle, size: float, font: str, width: float) -> None:
        lines = _wrap(value, font, size, width, rtl)
        # Escape each line, *then* join: escaping the joined string would turn
        # the separators themselves into literal "<br/>" text.
        story.append(Paragraph("<br/>".join(_escape(line) for line in lines), style))

    # --- header -------------------------------------------------------------
    if person_name:
        add(person_name, styles["name"], 19, BOLD_FONT, content_width)

    if job_title:
        add(job_title, styles["role"], 11.5, REGULAR_FONT, content_width)

    contact = _contact_line(member, rtl)
    if contact:
        add(contact, styles["contact"], 9, REGULAR_FONT, content_width)

    story.append(Spacer(1, 6))
    if metrics["rule"]:
        story.append(HRFlowable(
            width="100%",
            thickness=0.8,
            color=colors.HexColor("#dfe4f2"),
            spaceAfter=2,
        ))

    body_size = metrics["body_size"]

    # --- body ---------------------------------------------------------------
    for kind, lines in html_to_blocks(text):
        if kind == "rule":
            story.append(Spacer(1, 6))
            story.append(HRFlowable(
                width="100%",
                thickness=0.6,
                color=colors.HexColor("#dfe4f2"),
                spaceAfter=2,
            ))
            continue

        if kind == "heading":
            add(
                " ".join(lines),
                styles["heading"],
                metrics["heading_size"],
                BOLD_FONT,
                content_width,
            )
            continue

        if kind == "bullet":
            for line in lines:
                # The marker is already part of the text (added by the block
                # parser, or written by the author in a plain-text résumé), and
                # the bidi pass places it on the correct edge for the language.
                wrapped = _wrap(line, REGULAR_FONT, body_size, content_width - 12, rtl)
                story.append(
                    Paragraph(
                        "<br/>".join(_escape(item) for item in wrapped),
                        styles["bullet"],
                    )
                )
            story.append(Spacer(1, metrics["bullet_gap"]))
            continue

        for line in lines:
            add(line, styles["body"], body_size, REGULAR_FONT, content_width)

    doc.build(
        story,
        onFirstPage=lambda canvas, d: _footer(canvas, d, rtl),
        onLaterPages=lambda canvas, d: _footer(canvas, d, rtl),
    )
    return buffer.getvalue()


def resume_filename(member: dict, lang: str) -> str:
    """ASCII-safe download name, e.g. ``soroush-rahimi-resume-en.pdf``.

    Uses the Latin spelling for the English file, so the name is slug-friendly
    without transliterating Persian; the Persian file falls back to the
    identifier when the Persian name has no ASCII characters at all.
    """
    if lang == "en":
        name = member.get("full_name_en") or member.get("full_name") or ""
    else:
        name = member.get("full_name") or ""
    slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    if not slug:
        slug = f"member-{member.get('id', 'x')}"
    return f"{slug}-resume-{lang}.pdf"


__all__ = ["ResumePdfError", "build_resume_pdf", "resume_filename"]
