"""Title Case for headings, menu items, labels and buttons, on every page.

House style: each word in a heading or pointer starts with a capital, minor
words stay lower case ("Range and Prices", "Cost per New Customer"). Hundreds
of headings live in templates and generated reports, so rather than trust each
one to be typed correctly - and every new one after it - the HTML is passed
through here once on its way out.

Only words that start lower case are touched. Nothing is ever lowered, so
acronyms and codes (PKR, COD, D2C, CSV, MR-03) survive as written. Anything
inside an element marked ``class="nc"`` is left exactly as typed: brand names
and team names are the team's, not ours to restyle.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser

# "up" and "off" are left out: in a heading they are nearly always part of a
# verb ("Set Up Your Team", "Sign Off"), which takes a capital.
MINOR = frozenset("""a an the and but or nor for so yet as at by in of on per
to via vs vs. from with into over than""".split())

# Elements whose text is a heading or a pointer.
HEADINGS = frozenset({"h1", "h2", "h3", "h4", "th", "label", "summary", "nav",
                      "legend", "button"})
# Classes that mark a heading-like element that is not a heading tag.
HEADING_CLASSES = frozenset({"grp", "lab", "crumbs", "sec", "cap-h", "t-name"})
# Values and explanations that can sit inside a heading-like element (a tile's
# current value, a note): data, not heading, so left as written.
DATA_CLASSES = frozenset({"nc", "note", "hint", "help", "t-val", "t-help", "val",
                          "hid", "pill", "badge", "d", "cap", "desc"})
SKIP_TAGS = frozenset({"code", "script", "style", "textarea", "option", "select"})
VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                  "link", "meta", "source", "track", "wbr"})

_WORD = re.compile(r"[A-Za-z][A-Za-z'’]*")
# After these a new phrase starts, so its first word is capitalised.
_BREAK = re.compile(r"[:·—–|(\[/!?]\s*$|\s-\s*$|^\s*$")


def tc(text: str, starts: bool = True, ends: bool = True) -> str:
    """Title Case one string. Words that start lower case get a capital,
    except minor words in the middle of a phrase. `starts`/`ends` say whether
    this string begins or finishes the heading, for a heading split by tags."""
    if not text:
        return text
    words = list(_WORD.finditer(text))
    if not words:
        return text
    out, pos = [], 0
    for i, m in enumerate(words):
        word = m.group(0)
        start = m.start()
        out.append(text[pos:start])
        before = text[:start]
        # Part of a hyphenated or dotted compound ("e-commerce", "x.y")?
        joined = start > 0 and text[start - 1] in "-." and \
            start > 1 and text[start - 2].isalnum()
        first = (i == 0 and starts) or (i > 0 and bool(_BREAK.search(before)))
        after = text[m.end():]
        # The end of the heading, or of a phrase within it ("comes from, and").
        last = (i == len(words) - 1 and ends and not after.strip(" .")[:1].isalnum()) \
            or bool(re.match(r"\s*[,;:)]", after))
        if word[0].islower() and not (start > 0 and text[start - 1].isdigit()):
            minor = word.lower() in MINOR
            if joined:
                word = word[0].upper() + word[1:] if not minor else word
            elif first or last or not minor:
                word = word[0].upper() + word[1:]
        out.append(word)
        pos = m.end()
    out.append(text[pos:])
    return "".join(out)


class _Caser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out: list[str] = []
        self.stack: list[tuple[str, bool, bool]] = []   # tag, heading, skip
        self.fresh = True        # next text is the start of the heading
        self.glued = False       # last thing was an apostrophe entity: "month&#39;s"

    def _state(self) -> tuple[bool, bool]:
        heading = any(h for _, h, _ in self.stack)
        skip = any(s for _, _, s in self.stack)
        return heading, skip

    def handle_starttag(self, tag, attrs):
        self.out.append(self.get_starttag_text())
        if tag == "input":
            # A label around a radio or checkbox is an answer, not a heading.
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == "label":
                    self.stack[i] = ("label", False, self.stack[i][2])
                    break
        if tag in VOID:
            return
        classes = set((dict(attrs).get("class") or "").split())
        heading = tag in HEADINGS or bool(classes & HEADING_CLASSES)
        # "note" and "hint" are explanation, not heading, even inside one.
        skip = tag in SKIP_TAGS or bool(classes & DATA_CLASSES)
        if heading and not self._state()[0]:
            self.fresh = True
        self.stack.append((tag, heading, skip))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)
            self.out.pop()

    def handle_endtag(self, tag):
        self.out.append(f"</{tag}>")
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        heading, skip = self._state()
        if heading and not skip and data.strip():
            # The rest of a word broken by an apostrophe entity stays as it is.
            head = ""
            if self.glued:
                m = re.match(r"[A-Za-z]*", data)
                head, data = data[:m.end()], data[m.end():]
            # A heading broken by inline tags (<b>, <small>) is still one
            # phrase: only its very first word is forced to a capital.
            cased = tc(data) if self.fresh and not head else _continue(data)
            self.out.append(head + cased)
            self.fresh = False
        else:
            self.out.append(data)
        self.glued = False

    def handle_entityref(self, name):
        self.out.append(f"&{name};")
        self.glued = name in ("apos", "rsquo", "lsquo")

    def handle_charref(self, name):
        self.out.append(f"&#{name};")
        self.glued = name.lower() in ("39", "x27", "8217", "x2019")

    def handle_comment(self, data):
        self.out.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.out.append(f"<!{decl}>")

    def handle_pi(self, data):
        self.out.append(f"<?{data}>")

    def unknown_decl(self, data):
        self.out.append(f"<![{data}]>")


def _continue(text: str) -> str:
    """Title Case a fragment that continues a phrase begun earlier."""
    return tc(text, starts=False, ends=False)


def html(document: str) -> str:
    """The same document with its headings, labels and buttons in Title Case."""
    parser = _Caser()
    parser.feed(document)
    parser.close()
    return "".join(parser.out)
