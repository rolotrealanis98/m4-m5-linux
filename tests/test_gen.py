# SPDX-License-Identifier: MIT
import gen


def test_generate_is_deterministic_and_check_passes(mini_repo):
    a = gen.generate(mini_repo)
    b = gen.generate(mini_repo)
    assert a == b
    assert gen.main(["--root", str(mini_repo)]) == 0
    assert gen.main(["--root", str(mini_repo), "--check"]) == 0
    (mini_repo / "site" / "extra.html").write_text("x")
    assert gen.main(["--root", str(mini_repo), "--check"]) == 1


def test_readme_tables(mini_repo):
    files = gen.generate(mini_repo)
    readme = files["README.md"]
    assert "| All CPU cores (`cpu.smp`) | works (daily) R |" in readme
    assert "[example/linux#1](https://github.com/example/linux/pull/1)" in readme
    assert "| open |" in readme


def test_site_pages(mini_repo):
    files = gen.generate(mini_repo)
    for p in ["site/index.html", "site/machines/j999t.html", "site/machines/j999t/results/2026-11-01-boot.html",
              "site/builds/j999t/daily.html", "site/topics/boot-chain.html", "site/topics/index.html",
              "site/upstream.html", "site/style.css"]:
        assert p in files, p
    topic = files["site/topics/boot-chain.html"]
    assert 'href="../machines/j999t/results/2026-11-01-boot.html#cpu"' in topic
    machine = files["site/machines/j999t.html"]
    assert 'href="../machines/j999t/results/2026-11-01-boot.html#cpu"' in machine
    assert "Claim: works" in machine


def test_markdown_subset():
    out = gen.md_to_html("# T `x`\n\n| a | b |\n|---|---|\n| 1 | **2** |\n\n- i\n- j\n\n```\n<raw>\n```\n",
                         lambda t: t)
    assert '<h1 id="t-x">' in out and "<td><strong>2</strong></td>" in out
    assert "<li>i</li>" in out and "&lt;raw&gt;" in out


def test_stale_flag_uses_status_date(mini_repo):
    p = mini_repo / "upstream" / "status.json"
    p.write_text(p.read_text().replace("2026-11-05T00:00:00Z", "2027-01-05T00:00:00Z"))
    assert "works (daily) R*" in gen.generate(mini_repo)["README.md"]


def site_link_errors(files):
    """Every relative href in the generated site points at a generated file and an existing id."""
    import html as _html
    import posixpath
    import re
    errs = []
    for name, text in files.items():
        if not name.endswith(".html"):
            continue
        for href in re.findall(r'href="([^"]+)"', text):
            href = _html.unescape(href)
            if re.match(r"^[a-z]+:", href):
                continue
            path, _, anchor = href.partition("#")
            dest = name if not path else posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
            if dest not in files:
                errs.append(f"{name}: {href} (no such file)")
            elif anchor and f'id="{anchor}"' not in files[dest]:
                errs.append(f"{name}: {href} (no such id)")
    return errs


def test_site_links_resolve(mini_repo):
    assert site_link_errors(gen.generate(mini_repo)) == []


def test_repository_site_links_resolve():
    from conftest import ROOT
    assert site_link_errors(gen.generate(ROOT)) == []
