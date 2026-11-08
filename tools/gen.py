#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""gen.py - render the README status tables and the static site (site/) from the YAML data.

  python3 tools/gen.py           # rewrite the generated README sections and site/
  python3 tools/gen.py --check   # exit 1 if anything generated is out of date (CI)

The output is deterministic: it depends only on the files in the repository (no clock), so --check is exact.
Standard library + PyYAML.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common  # noqa: E402

# Update after the transfer to omacom (the old URL keeps redirecting).
REPO_URL = "https://github.com/rolotrealanis98/m4plus-linux"
SITE_TITLE = "M4Plus-Linux"
MARK = "<!-- {} GENERATED: {} -->"
STATE_LABEL = {
    "works-daily": "works (daily)", "works-test": "works (test)", "attended": "attended", "prepared": "prepared",
    "blocked": "blocked", "not-realistic": "not realistic", "untested": "untested", "reported": "reported",
}


# ---------------------------------------------------------------- data

class Data:
    def __init__(self, root):
        self.root = pathlib.Path(root)
        self.features = common.load_yaml(self.root / "schema" / "features.yaml")
        self.fids = list(self.features["features"])
        self.machines = []
        for f, m in common.load_machines(self.root):
            m = dict(m)
            m["_dir"] = f.parent
            m["_slug"] = f.parent.name
            self.machines.append(m)
        self.machines.sort(key=lambda m: m["board"])
        self.prs = (common.load_prs(self.root).get("prs") or [])
        self.status = (common.load_status(self.root).get("prs") or {})
        # gen.py never reads the clock: staleness is judged against the last upstream refresh (status.json),
        # which the daily bot updates, so the output depends only on the files in the repository.
        self.ref_date = common.parse_date(common.load_status(self.root).get("fetched_at"))

    def families(self):
        return sorted({m.get("family", "?") for m in self.machines})

    def boards(self, family):
        return [m for m in self.machines if m.get("family") == family]

    def feature_rows(self, machines):
        present = set()
        for m in machines:
            present |= set((m.get("features") or {}).keys())
        return [f for f in self.fids if f in present]

    def pr_state(self, ref):
        st = self.status.get(ref) or {}
        s = st.get("state", "unknown")
        if s == "open" and st.get("draft"):
            s = "draft"
        return s


def cell_summary(cells, ref_date=None, owners=None):
    """-> (state, flags) for the matrix: best state across setups, 'R' when reproduced, '*' when stale."""
    if not cells:
        return "untested", ""
    best = common.newest_cell(cells)
    state = best.get("state", "untested")
    flags = ""
    if common.reproduced(cells, owners):
        flags += "R"
    if ref_date is not None and any(common.is_stale(c, ref_date) for c in cells if c.get("state") == state):
        flags += "*"
    return state, flags


# ---------------------------------------------------------------- README

def readme_matrix(d, ref_date):
    out = []
    for fam in d.families():
        ms = d.boards(fam)
        out.append(f"#### {fam} family\n")
        head = "| Feature | " + " | ".join(
            f"[{m['board']}](machines/{m['_slug']}/machine.yaml){' (draft)' if m.get('draft') else ''}" for m in ms) + " |"
        out.append(head)
        out.append("|---|" + "---|" * len(ms))
        for fid in d.feature_rows(ms):
            title = d.features["features"][fid]["title"]
            row = [f"{title} (`{fid}`)"]
            for m in ms:
                cells = (m.get("features") or {}).get(fid) or []
                state, flags = cell_summary(cells, ref_date, common.setup_owners(m))
                row.append(STATE_LABEL[state] + (f" {flags}" if flags else ""))
            out.append("| " + " | ".join(row) + " |")
        out.append("")
    out.append("States and evidence rules: see [States and evidence](#states-and-evidence). "
               "`R` = reproduced on two setups, `*` = stale.")
    return "\n".join(out)


def readme_machines(d):
    out = ["| Board | Model | Identifier | SoC | Owners | Entry | Setups | Current build |", "|---|---|---|---|---|---|---|---|"]
    for m in d.machines:
        owners = ", ".join(f"[@{o}](https://github.com/{o})" for o in common.owners_of(m))
        setups = ", ".join(s["id"] for s in m.get("setups", []))
        builds = ", ".join(f"[{pathlib.Path(s['current_build']).stem}]({s['current_build']})"
                           for s in m.get("setups", []) if s.get("current_build")) or "none"
        entry = "draft (from public posts, not yet confirmed)" if m.get("draft") else "confirmed"
        out.append(f"| [{m['board']}](machines/{m['_slug']}/machine.yaml) | {m['model']} | {m['identifier']} | {m['soc']} | "
                   f"{owners} | {entry} | {setups} | {builds} |")
    return "\n".join(out)


def readme_upstream(d):
    out = ["| PR | Title | Machines | Features | State |", "|---|---|---|---|---|"]
    for pr in sorted(d.prs, key=lambda p: (p["repo"], p["number"])):
        ref = common.pr_key(pr["repo"], pr["number"])
        url = f"https://github.com/{pr['repo']}/pull/{pr['number']}"
        feats = ", ".join(f"`{f}`" for f in pr.get("features", []))
        out.append(f"| [{ref}]({url}) | {pr['title']} | {', '.join(pr['machines'])} | {feats} | {d.pr_state(ref)} |")
    st = common.load_status(d.root)
    when = st.get("fetched_at")
    out.append("")
    out.append(f"State from `upstream/status.json`" + (f", fetched {when}." if when else " (not fetched yet)."))
    return "\n".join(out)


def splice(text, name, body):
    b, e = MARK.format("BEGIN", name), MARK.format("END", name)
    rx = re.compile(re.escape(b) + r".*?" + re.escape(e), re.S)
    if not rx.search(text):
        raise SystemExit(f"README.md has no {b} ... {e} markers")
    return rx.sub(lambda _: f"{b}\n{body}\n{e}", text)


def render_readme(d, ref_date):
    text = (d.root / "README.md").read_text(encoding="utf-8")
    text = splice(text, "matrix", readme_matrix(d, ref_date))
    text = splice(text, "machines", readme_machines(d))
    text = splice(text, "upstream", readme_upstream(d))
    return text


# ---------------------------------------------------------------- Markdown -> HTML (small subset)

def _emph(s):
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])", r"<em>\1</em>", s)


def _inline(s, link):
    codes = []

    def keep_code(m):
        codes.append(html.escape(m.group(1)))
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", keep_code, s)
    links = []

    def keep_link(m):
        text, target = m.group(1), m.group(2)
        links.append((_emph(html.escape(text, quote=False)), link(target)))
        return f"\x01{len(links) - 1}\x01"

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", keep_link, s)
    s = re.sub(r"<(https://[^>\s]+)>", lambda m: (links.append((html.escape(m.group(1), quote=False), m.group(1))) or
                                                   f"\x01{len(links) - 1}\x01"), s)
    s = _emph(html.escape(s, quote=False))
    s = re.sub(r"\x01(\d+)\x01", lambda m: f'<a href="{html.escape(links[int(m.group(1))][1])}">'
                                           f'{links[int(m.group(1))][0]}</a>', s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", s)
    return s


def md_to_html(text, link):
    lines = text.splitlines()
    out, i, seen = [], 0, {}
    para = []

    def flush_para():
        if para:
            out.append("<p>" + _inline(" ".join(x.strip() for x in para), link) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        st = line.strip()
        if st.startswith("```") or st.startswith("~~~"):
            flush_para()
            fence, info = st[:3], st[3:].strip()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith(fence):
                buf.append(lines[i])
                i += 1
            i += 1
            cls = f' class="language-{html.escape(info.split()[0])}"' if info else ""
            out.append(f"<pre><code{cls}>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            flush_para()
            lvl = len(m.group(1))
            s = common.slugify(m.group(2))
            n = seen.get(s, 0)
            seen[s] = n + 1
            hid = s if n == 0 else f"{s}-{n}"
            out.append(f'<h{lvl} id="{hid}">{_inline(m.group(2), link)} <a class="anchor" href="#{hid}">#</a></h{lvl}>')
            i += 1
            continue
        if st.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            flush_para()

            def cells(row):
                row = row.strip()
                row = row[1:] if row.startswith("|") else row
                row = row[:-1] if row.endswith("|") else row
                return [c.strip() for c in re.split(r"(?<!\\)\|", row)]

            head = cells(line)
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append(cells(lines[i]))
                i += 1
            t = ['<div class="table"><table><thead><tr>' + "".join(f"<th>{_inline(c, link)}</th>" for c in head) +
                 "</tr></thead><tbody>"]
            for r in body:
                t.append("<tr>" + "".join(f"<td>{_inline(c, link)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            flush_para()
            ordered = bool(re.match(r"^\s*\d+\.", line))
            items = []
            while i < len(lines) and lines[i].strip():
                lm = re.match(r"^\s*([-*]|\d+\.)\s+(.*)$", lines[i])
                if lm and (len(lines[i]) - len(lines[i].lstrip())) < 2:
                    items.append(lm.group(2))
                elif lm:   # nested item: keep it as its own line in the parent
                    items[-1] += "\n" + lm.group(2)
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(
                "<li>" + "<br>".join(_inline(x, link) for x in it.split("\n")) + "</li>" for it in items) + f"</{tag}>")
            continue
        if st.startswith(">"):
            flush_para()
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote>" + md_to_html("\n".join(buf), link) + "</blockquote>")
            continue
        if not st:
            flush_para()
            i += 1
            continue
        para.append(line)
        i += 1
    flush_para()
    return "\n".join(out)


# ---------------------------------------------------------------- site

CSS = """:root{--bg:#fbfbfa;--fg:#1d1f21;--muted:#5d6166;--line:#d9dbde;--card:#ffffff;--link:#1f5fbf;
--ok:#1e7a3c;--okbg:#e3f3e8;--test:#2d6a8f;--testbg:#e2eef6;--att:#8a5a00;--attbg:#fbefd9;--prep:#5b4a8a;
--prepbg:#ece8f6;--blk:#a12b2b;--blkbg:#f8e1e1;--nr:#555;--nrbg:#ececec;--un:#8a8f95;--unbg:transparent;
--rep:#6b5d1f;--repbg:#f4f0d8;--code:#f0f1f2}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15171a;--fg:#e6e7e8;--muted:#a3a8ae;
--line:#30343a;--card:#1c1f23;--link:#7fb0ff;--ok:#7dd69a;--okbg:#173322;--test:#8cc6ea;--testbg:#14293a;
--att:#f0c171;--attbg:#3a2c12;--prep:#c2b4f0;--prepbg:#2a2440;--blk:#f19a9a;--blkbg:#3d1b1b;--nr:#bbb;
--nrbg:#2a2a2a;--un:#7c8187;--rep:#e3d58a;--repbg:#34301a;--code:#22262b}}
:root[data-theme="dark"]{--bg:#15171a;--fg:#e6e7e8;--muted:#a3a8ae;--line:#30343a;--card:#1c1f23;--link:#7fb0ff;
--ok:#7dd69a;--okbg:#173322;--test:#8cc6ea;--testbg:#14293a;--att:#f0c171;--attbg:#3a2c12;--prep:#c2b4f0;
--prepbg:#2a2440;--blk:#f19a9a;--blkbg:#3d1b1b;--nr:#bbb;--nrbg:#2a2a2a;--un:#7c8187;--rep:#e3d58a;--repbg:#34301a;
--code:#22262b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,
"Segoe UI",sans-serif}main{max-width:1180px;margin:0 auto;padding:16px}a{color:var(--link)}
header.site{border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:16px;flex-wrap:wrap;align-items:center}
header.site a{text-decoration:none;font-weight:600}header.site nav a{font-weight:400;margin-right:12px}
h1{font-size:1.6rem}h2{font-size:1.25rem;margin-top:2rem}h3{font-size:1.05rem}.anchor{opacity:.25;text-decoration:none}
.muted{color:var(--muted)}code{background:var(--code);padding:1px 4px;border-radius:4px;font-size:.9em}
pre{background:var(--code);padding:10px;border-radius:6px;overflow-x:auto}pre code{padding:0;background:none}
.table{overflow-x:auto;margin:12px 0}table{border-collapse:collapse;min-width:100%}th,td{border:1px solid var(--line);
padding:4px 8px;vertical-align:top;text-align:left}th{background:var(--card);position:sticky;top:0}
.st{display:inline-block;padding:0 6px;border-radius:4px;font-size:.85em;white-space:nowrap;font-weight:600}
.st-works-daily{color:var(--ok);background:var(--okbg)}.st-works-test{color:var(--test);background:var(--testbg)}
.st-attended{color:var(--att);background:var(--attbg)}.st-prepared{color:var(--prep);background:var(--prepbg)}
.st-blocked{color:var(--blk);background:var(--blkbg)}.st-not-realistic{color:var(--nr);background:var(--nrbg)}
.st-untested{color:var(--un);background:var(--unbg);font-weight:400}.st-reported{color:var(--rep);background:var(--repbg)}
.flag{font-size:.8em;color:var(--muted);margin-left:4px}blockquote{border-left:3px solid var(--line);margin:0;padding:0 12px}
footer{border-top:1px solid var(--line);margin-top:32px;padding:12px 16px;color:var(--muted);font-size:.9em}
"""


def page(title, body, depth):
    up = "../" * depth
    nav = (f'<header class="site"><a href="{up}index.html">{SITE_TITLE}</a><nav>'
           f'<a href="{up}index.html">Matrix</a><a href="{up}upstream.html">Upstream PRs</a>'
           f'<a href="{up}topics/index.html">Topics</a><a href="{REPO_URL}">Repository</a></nav></header>')
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{html.escape(title)}</title><link rel=\"stylesheet\" href=\"{up}style.css\"></head>"
            f"<body>{nav}<main>\n{body}\n</main><footer>Generated by <code>tools/gen.py</code> from the data in "
            f'<a href="{REPO_URL}">the repository</a>. Text and data CC-BY-SA-4.0; tools MIT. Independent of Apple, '
            f"Asahi Linux, omacom/Omarchy and Aurora Silicon.</footer></body></html>\n")


def st_badge(state, flags=""):
    f = f'<span class="flag">{html.escape(flags)}</span>' if flags else ""
    return f'<span class="st st-{state}">{html.escape(STATE_LABEL[state])}</span>{f}'


class Site:
    def __init__(self, d):
        self.d = d
        self.files = {}
        self.rendered_md = {}   # repo-relative md path -> site-relative html path

    def add(self, rel, content):
        self.files[f"site/{rel}"] = content

    def link_for(self, src_rel, depth):
        """Return a link resolver for Markdown found at repo path src_rel, rendered at the given depth."""
        src_dir = pathlib.PurePosixPath(src_rel).parent
        up = "../" * depth

        def resolve(target):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                return target
            path, _, anchor = target.partition("#")
            norm = _normpath(src_dir / path)
            frag = f"#{anchor}" if anchor else ""
            if norm in self.rendered_md:
                return up + self.rendered_md[norm] + frag
            if norm.startswith("builds/") and norm.endswith(".yaml"):
                return up + norm[:-5] + ".html" + frag
            return f"{REPO_URL}/blob/main/{norm}{frag}"
        return resolve

    def build(self):
        d = self.d
        # plan the rendered Markdown first, so links can point at it
        for m in d.machines:
            for rf in sorted((m["_dir"] / "results").glob("*.md")):
                rel = rf.relative_to(d.root).as_posix()
                self.rendered_md[rel] = f"machines/{m['_slug']}/results/{rf.stem}.html"
        topics = sorted((d.root / "topics").glob("*/README.md")) if (d.root / "topics").exists() else []
        for t in topics:
            self.rendered_md[t.relative_to(d.root).as_posix()] = f"topics/{t.parent.name}.html"
        self.add("style.css", CSS)
        self.add(".nojekyll", "")
        self.index()
        for m in d.machines:
            self.machine(m)
            for rf in sorted((m["_dir"] / "results").glob("*.md")):
                self.result(m, rf)
        for bf in sorted((d.root / "builds").glob("*/*.yaml")):
            self.build_page(bf)
        self.topics(topics)
        self.upstream()
        return self.files

    def index(self):
        d = self.d
        body = [f"<h1>{SITE_TITLE}</h1>",
                "<p>Status of Linux on Macs with M4 and M5 chips, by machine and feature. Every <em>works</em> cell links "
                "a dated result from that machine; draft machines show their owners' public claims as "
                "<em>reported</em> until the owners confirm them. Code lives upstream; this site tracks it.</p>",
                '<p class="muted">Legend: ' + " ".join(st_badge(s) for s in common.STATES) +
                ' &nbsp; R = reproduced on two setups, * = stale (no supporting result in the 30 days before the last upstream refresh).</p>']
        for fam in d.families():
            ms = d.boards(fam)
            body.append(f'<h2 id="{fam.lower()}">{fam} family</h2><div class="table"><table><thead><tr><th>Feature</th>')
            for m in ms:
                body.append(f'<th><a href="machines/{m["_slug"]}.html">{html.escape(m["board"])}</a><br>'
                            f'<span class="muted">{html.escape(m["model"])}{" (draft)" if m.get("draft") else ""}</span></th>')
            body.append("</tr></thead><tbody>")
            for fid in d.feature_rows(ms):
                f = d.features["features"][fid]
                body.append(f'<tr><td>{html.escape(f["title"])}<br><code>{fid}</code></td>')
                for m in ms:
                    cells = (m.get("features") or {}).get(fid) or []
                    state, flags = cell_summary(cells, d.ref_date, common.setup_owners(m))
                    tip = html.escape(" / ".join(c.get("note", "") or c.get("claim", "") for c in cells)[:300])
                    frag = f"#{_fid(fid)}" if cells else ""
                    body.append(f'<td title="{tip}"><a href="machines/{m["_slug"]}.html{frag}">'
                                f"{st_badge(state, flags)}</a></td>")
                body.append("</tr>")
            body.append("</tbody></table></div>")
        self.add("index.html", page(SITE_TITLE, "\n".join(body), 0))

    def machine(self, m):
        d = self.d
        slug = m["_slug"]
        owners = ", ".join(f'<a href="https://github.com/{o}">@{html.escape(o)}</a>' for o in common.owners_of(m))
        b = [f"<h1>{html.escape(m['board'])}: {html.escape(m['model'])}</h1>",
             f"<p>{html.escape(m['identifier'])} · {html.escape(m['soc'])} · {html.escape(m.get('family', ''))} family · "
             f"owners {owners}</p>"]
        if m.get("draft"):
            b.append('<p><strong>Draft.</strong> Written from the owners\' public posts and not yet confirmed by them. '
                     "Every cell is a reported claim with a link to its source.</p>")
        if m.get("notes"):
            b.append(f"<p>{_inline(m['notes'], self.link_for(f'machines/{slug}/machine.yaml', 1))}</p>")
        if m.get("status_repos"):
            b.append("<p>Status repositories: " + ", ".join(f'<a href="{html.escape(u)}">{html.escape(u)}</a>'
                                                          for u in m["status_repos"]) + "</p>")
        b.append("<h2>Setups</h2><ul>")
        for s in m.get("setups", []):
            fw = s.get("firmware") or {}
            stack = s.get("stack") or {}
            parts = [f"<strong>{html.escape(s['id'])}</strong> (@{html.escape(s['owner'])})"]
            if fw:
                parts.append(f"firmware os {html.escape(fw.get('os', '?'))}, system {html.escape(fw.get('system', '?'))}")
            for k in ("kernel", "loader", "userspace"):
                if stack.get(k):
                    parts.append(f"{k}: {html.escape(stack[k])}")
            if s.get("current_build"):
                cb = s["current_build"]
                parts.append(f'current build <a href="../{cb[:-5]}.html">{html.escape(pathlib.Path(cb).stem)}</a>')
            if s.get("source"):
                parts.append(f'<a href="{html.escape(s["source"])}">source</a>')
            b.append("<li>" + "; ".join(parts) + "</li>")
        b.append("</ul><h2>Features</h2>")
        link = self.link_for(f"machines/{slug}/machine.yaml", 1)
        b.append('<div class="table"><table><thead><tr><th>Feature</th><th>Setup</th><th>State</th><th>Kind</th>'
                 "<th>Evidence</th><th>Upstream</th><th>Verified</th><th>Note</th></tr></thead><tbody>")
        feats = m.get("features") or {}
        for fid in [f for f in d.fids if f in feats]:
            cells = feats[fid]
            for n, c in enumerate(cells):
                ev = []
                for e in c.get("evidence") or []:
                    label = e.split("/")[-1] if not e.startswith("https://") else _short_url(e)
                    ev.append(f'<a href="{html.escape(link(e))}">{html.escape(label)}</a>')
                ups = []
                for u in c.get("upstream") or []:
                    repo, num = u.split("#")
                    ups.append(f'<a href="https://github.com/{repo}/pull/{num}">{html.escape(u)}</a> '
                               f'<span class="muted">{html.escape(d.pr_state(u))}</span>')
                note = c.get("note") or ""
                if c.get("claim"):
                    note = f"Claim: {c['claim']}" + (f". {note}" if note else "")
                first = f'<td rowspan="{len(cells)}" id="{_fid(fid)}">{html.escape(d.features["features"][fid]["title"])}' \
                        f'<br><code>{fid}</code></td>' if n == 0 else ""
                b.append(f"<tr>{first}<td>{html.escape(c.get('setup', ''))}</td><td>{st_badge(c['state'])}</td>"
                         f"<td>{html.escape(c.get('kind', ''))}</td><td>{'<br>'.join(ev)}</td><td>{'<br>'.join(ups)}</td>"
                         f"<td>{html.escape(c.get('verified', '') or '')}</td><td>{_inline(note, link)}</td></tr>")
        b.append("</tbody></table></div>")
        b.append(f'<p class="muted">Source: <a href="{REPO_URL}/blob/main/machines/{slug}/machine.yaml">'
                 f"machines/{slug}/machine.yaml</a></p>")
        self.add(f"machines/{slug}.html", page(f"{m['board']} - {SITE_TITLE}", "\n".join(b), 1))

    def result(self, m, rf):
        rel = rf.relative_to(self.d.root).as_posix()
        fm, body = common.front_matter(rf.read_text(encoding="utf-8"))
        link = self.link_for(rel, 3)
        rows = []
        for k, v in (fm or {}).items():
            val = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
            if k == "build" and isinstance(v, str) and v.startswith("builds/"):
                val_html = f'<a href="{html.escape(link("../../../" + v))}">{html.escape(v)}</a>'
            elif k == "source" and isinstance(v, str):
                val_html = f'<a href="{html.escape(v)}">{html.escape(_short_url(v))}</a>'
            else:
                val_html = html.escape(val)
            rows.append(f"<tr><th>{html.escape(k)}</th><td>{val_html}</td></tr>")
        content = (f'<p><a href="../../{m["_slug"]}.html">{html.escape(m["board"])}</a> · result '
                   f"<code>{html.escape(rf.name)}</code></p>"
                   f'<div class="table"><table><tbody>{"".join(rows)}</tbody></table></div>\n' + md_to_html(body, link))
        self.add(f"machines/{m['_slug']}/results/{rf.stem}.html", page(f"{rf.stem} - {SITE_TITLE}", content, 3))

    def build_page(self, bf):
        rel = bf.relative_to(self.d.root).as_posix()
        b = common.load_yaml(bf)
        text = bf.read_text(encoding="utf-8")
        results = "".join(f'<li><a href="../../{self.rendered_md.get(r, r)}">{html.escape(r)}</a></li>'
                          for r in b.get("results", []))
        content = (f"<h1>Build {html.escape(b.get('name', bf.stem))}</h1><p>{html.escape(b.get('board', ''))} · "
                   f"status {html.escape(b.get('status', ''))} · {html.escape(b.get('date', ''))}</p>"
                   f"<h2>Results</h2><ul>{results}</ul><h2>Recipe</h2><pre><code>{html.escape(text)}</code></pre>"
                   f'<p class="muted"><a href="{REPO_URL}/blob/main/{rel}">{rel}</a></p>')
        self.add(rel[:-5] + ".html", page(f"{b.get('name', bf.stem)} - {SITE_TITLE}", content, 2))

    def topics(self, topics):
        items = []
        for t in topics:
            rel = t.relative_to(self.d.root).as_posix()
            text = t.read_text(encoding="utf-8")
            m = re.search(r"^#\s+(.*)$", text, re.M)
            title = m.group(1).strip() if m else t.parent.name
            items.append(f'<li><a href="{t.parent.name}.html">{_inline(title, lambda x: x)}</a></li>')
            self.add(f"topics/{t.parent.name}.html",
                     page(f"{common.slugify(title)} - {SITE_TITLE}", md_to_html(text, self.link_for(rel, 1)), 1))
        self.add("topics/index.html", page(f"Topics - {SITE_TITLE}",
                                           "<h1>Topics</h1><p>What is known per SoC, written once, with links to the "
                                           "machine results and the upstream PRs.</p><ul>" + "".join(items) + "</ul>", 1))

    def upstream(self):
        d = self.d
        st = common.load_status(d.root)
        rows = []
        for pr in sorted(d.prs, key=lambda p: (p["repo"], p["number"])):
            ref = common.pr_key(pr["repo"], pr["number"])
            s = d.status.get(ref) or {}
            rows.append(f'<tr><td><a href="https://github.com/{pr["repo"]}/pull/{pr["number"]}">{html.escape(ref)}</a></td>'
                        f"<td>{html.escape(pr['title'])}</td><td>{html.escape(', '.join(pr['machines']))}</td>"
                        f"<td>{html.escape(', '.join(pr.get('features', [])))}</td><td>{html.escape(d.pr_state(ref))}</td>"
                        f"<td>{html.escape(s.get('review', '') or '')}</td><td>{html.escape((s.get('updated_at') or '')[:10])}</td></tr>")
        when = st.get("fetched_at")
        body = ("<h1>Upstream pull requests</h1><p>Index: <code>upstream/prs.yaml</code>. State: "
                f"<code>upstream/status.json</code>{', fetched ' + html.escape(when) if when else ''}.</p>"
                '<div class="table"><table><thead><tr><th>PR</th><th>Title</th><th>Machines</th><th>Features</th>'
                "<th>State</th><th>Review</th><th>Updated</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")
        self.add("upstream.html", page(f"Upstream PRs - {SITE_TITLE}", body, 0))


def _fid(fid):
    return "f-" + fid.replace(".", "-")


def _short_url(u):
    u = re.sub(r"^https://(www\.)?", "", u)
    return u if len(u) <= 60 else u[:57] + "..."


def _normpath(p):
    parts = []
    for x in pathlib.PurePosixPath(p).parts:
        if x == "..":
            if parts:
                parts.pop()
        elif x != ".":
            parts.append(x)
    return "/".join(parts)


# ---------------------------------------------------------------- main

def generate(root):
    d = Data(root)
    files = {"README.md": render_readme(d, d.ref_date)}
    files.update(Site(d).build())
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(common.ROOT))
    ap.add_argument("--check", action="store_true", help="exit 1 if the generated files are out of date")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root)
    files = generate(root)
    existing = {p.relative_to(root).as_posix() for p in (root / "site").rglob("*") if p.is_file()} \
        if (root / "site").exists() else set()
    stale = sorted(existing - set(files))
    changed = sorted(k for k, v in files.items()
                     if not (root / k).exists() or (root / k).read_text(encoding="utf-8") != v)
    if a.check:
        for k in changed:
            print(f"out of date: {k}")
        for k in stale:
            print(f"not generated (remove it): {k}")
        if changed or stale:
            print("gen.py --check: run python3 tools/gen.py and commit the result")
            return 1
        print(f"gen.py --check: {len(files)} file(s) up to date")
        return 0
    for k in changed:
        p = root / k
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(files[k], encoding="utf-8")
    for k in stale:
        (root / k).unlink()
    print(f"gen.py: {len(changed)} file(s) written, {len(stale)} removed, {len(files)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
