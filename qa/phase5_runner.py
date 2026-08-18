from __future__ import annotations

from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json
import os
import re
import shutil
import subprocess
import time

ROOT = Path.cwd().resolve()
QA = ROOT / "qa-output"
LH = QA / "lighthouse"
SS = QA / "screenshots"
LH.mkdir(parents=True, exist_ok=True)
SS.mkdir(parents=True, exist_ok=True)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.links = []
        self.assets = []
        self.meta = {}
        self.canonical = None
        self.h1 = 0
        self.lang = None
        self.jsonld = []
        self._json = False
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self.in_title = True
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("img", "script", "link"):
            key = "src" if tag in ("img", "script") else "href"
            if a.get(key):
                self.assets.append(a[key])
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key and a.get("content") is not None:
                self.meta[key.lower()] = a["content"]
        if tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href")
        if tag == "h1":
            self.h1 += 1
        if tag == "script" and a.get("type") == "application/ld+json":
            self._json = True
            self._buf = ""

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self._json:
            self.jsonld.append(self._buf)
            self._json = False
            self._buf = ""

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self._json:
            self._buf += data


def local_target(page: Path, href: str):
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    u = urlparse(href)
    if u.scheme in ("http", "https"):
        if u.netloc not in ("kronatrix.co.uk", "www.kronatrix.co.uk"):
            return None
        path = unquote(u.path)
    elif u.scheme:
        return None
    else:
        path = unquote(u.path)
    if not path:
        return page
    target = ROOT / path.lstrip("/") if path.startswith("/") else page.parent / path
    target = Path(str(target).split("#")[0].split("?")[0])
    if target.is_dir() or path.endswith("/"):
        target = target / "index.html"
    return target


def static_qa():
    html_files = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "qa-output" not in p.parts)
    issues = []
    rows = []
    canonicals = {}
    titles = {}

    for p in html_files:
        q = Parser()
        q.feed(p.read_text(encoding="utf-8", errors="replace"))
        rel = str(p.relative_to(ROOT))
        title = " ".join(q.title.split())
        desc = q.meta.get("description", "").strip()
        rows.append((rel, len(title), len(desc), q.h1, q.canonical or "—"))
        if not title:
            issues.append((rel, "ERROR", "Missing title"))
        elif len(title) > 70:
            issues.append((rel, "WARN", f"Title length {len(title)} > 70"))
        if not desc:
            issues.append((rel, "WARN", "Missing meta description"))
        elif not 25 <= len(desc) <= 160:
            issues.append((rel, "WARN", f"Meta description length {len(desc)} outside 25–160"))
        if not q.canonical:
            issues.append((rel, "WARN", "Missing canonical"))
        else:
            canonicals.setdefault(q.canonical, []).append(rel)
        if title:
            titles.setdefault(title, []).append(rel)
        if q.h1 != 1:
            issues.append((rel, "WARN", f"Expected 1 H1, found {q.h1}"))
        if q.lang not in ("en-GB", "en-gb"):
            issues.append((rel, "WARN", f"html lang is {q.lang!r}, expected en-GB"))
        for js in q.jsonld:
            try:
                json.loads(js)
            except Exception as exc:
                issues.append((rel, "ERROR", f"Invalid JSON-LD: {exc}"))
        for href in q.links + q.assets:
            target = local_target(p, href)
            if target is not None and not target.exists():
                issues.append((rel, "ERROR", f"Missing local target: {href}"))

    for canonical, files in canonicals.items():
        if len(files) > 1:
            issues.append(("GLOBAL", "WARN", f"Duplicate canonical {canonical}: {files}"))
    for title, files in titles.items():
        if len(files) > 1:
            issues.append(("GLOBAL", "WARN", f"Duplicate title {title!r}: {files}"))

    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        for u in re.findall(r"<loc>(.*?)</loc>", sitemap.read_text(encoding="utf-8")):
            target = local_target(ROOT / "index.html", u)
            if target is not None and not target.exists():
                issues.append(("sitemap.xml", "ERROR", f"Sitemap target missing: {u}"))
    else:
        issues.append(("GLOBAL", "ERROR", "sitemap.xml missing"))

    errors = sum(1 for _, sev, _ in issues if sev == "ERROR")
    warnings = sum(1 for _, sev, _ in issues if sev == "WARN")
    md = [
        "# Phase 5 static QA",
        "",
        f"Pages checked: **{len(html_files)}**  ",
        f"Errors: **{errors}**  ",
        f"Warnings: **{warnings}**",
        "",
        "| File | Title len | Description len | H1 | Canonical |",
        "|---|---:|---:|---:|---|",
    ]
    md += [f"| `{a}` | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows]
    md += ["", "## Findings"]
    md += [f"- **{sev}** `{f}` — {m}" for f, sev, m in issues] or ["- No static findings."]
    (QA / "static-report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (QA / "static-report.json").write_text(json.dumps({"pages": len(html_files), "errors": errors, "warnings": warnings, "issues": issues}, indent=2), encoding="utf-8")
    return len(html_files), errors, warnings


def run(cmd, **kwargs):
    print("+", " ".join(str(x) for x in cmd))
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def browser_qa():
    chrome = next((p for p in [shutil.which("google-chrome"), shutil.which("google-chrome-stable"), shutil.which("chromium")] if p), None)
    if not chrome:
        raise RuntimeError("Chrome/Chromium not found")
    run([chrome, "--version"])
    server_log = open(QA / "server.log", "w", encoding="utf-8")
    server = subprocess.Popen([shutil.which("python") or "python", "-m", "http.server", "8000", "--bind", "127.0.0.1"], stdout=server_log, stderr=subprocess.STDOUT)
    try:
        import urllib.request
        for _ in range(30):
            try:
                urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1).read(50)
                break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError("Local preview server did not start")

        shots = [
            ("1440,1200", "home-desktop.png", "/"),
            ("390,844", "home-mobile.png", "/"),
            ("1440,1200", "ai-seo-desktop.png", "/what-is-ai-seo/"),
            ("390,844", "accountants-mobile.png", "/industries/accountants/"),
        ]
        for size, name, path in shots:
            run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", f"--window-size={size}", f"--screenshot={SS / name}", f"http://127.0.0.1:8000{path}"])

        run(["npm", "install", "--global", "lighthouse@12"])
        lighthouse = shutil.which("lighthouse") or "lighthouse"
        flags = "--headless=new --no-sandbox --disable-gpu"
        tests = [
            ("home-desktop", "/", "desktop"),
            ("home-mobile", "/", "mobile"),
            ("ai-seo-mobile", "/what-is-ai-seo/", "mobile"),
            ("accountants-mobile", "/industries/accountants/", "mobile"),
            ("research-mobile", "/research/uk-ai-search-access-index/", "mobile"),
        ]
        for name, path, form in tests:
            cmd = [lighthouse, f"http://127.0.0.1:8000{path}", "--quiet", f"--chrome-flags={flags}", "--only-categories=performance,accessibility,best-practices,seo", f"--form-factor={form}", "--output=json", f"--output-path={LH / (name + '.json')}"]
            if form == "desktop":
                cmd.insert(-2, "--screenEmulation.disabled")
            run(cmd)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except Exception:
            server.kill()
        server_log.close()


def lighthouse_summary():
    rows = []
    for p in sorted(LH.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        c = d["categories"]
        a = d["audits"]
        score = lambda k: round((c[k]["score"] or 0) * 100)
        def metric(k):
            value = a.get(k, {}).get("numericValue")
            return None if value is None else round(value, 1)
        rows.append((p.stem, score("performance"), score("accessibility"), score("best-practices"), score("seo"), metric("first-contentful-paint"), metric("largest-contentful-paint"), metric("cumulative-layout-shift"), metric("total-blocking-time")))
    md = ["# Phase 5 Lighthouse summary", "", "| Run | Perf | A11y | Best | SEO | FCP ms | LCP ms | CLS | TBT ms |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    md += ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    if not rows:
        md.append("| no report | — | — | — | — | — | — | — | — |")
    md += ["", "Targets: Performance 90+, Accessibility 95+, Best Practices 95+, SEO 95+, CLS < 0.10."]
    (QA / "lighthouse-summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows


def main():
    pages, errors, warnings = static_qa()
    browser_error = None
    try:
        browser_qa()
    except Exception as exc:
        browser_error = str(exc)
        (QA / "browser-error.txt").write_text(browser_error + "\n", encoding="utf-8")
    rows = lighthouse_summary()
    body = [
        "## Phase 5 automated QA result",
        "",
        f"Pages checked: **{pages}**  ",
        f"Static errors: **{errors}**  ",
        f"Static warnings: **{warnings}**",
        "",
        (QA / "lighthouse-summary.md").read_text(encoding="utf-8"),
    ]
    if browser_error:
        body += ["", f"Browser/Lighthouse runner error: `{browser_error}`"]
    body += ["", "Screenshots and raw Lighthouse JSON are included in the workflow artifact."]
    (QA / "pr-comment.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    print((QA / "pr-comment.md").read_text())

if __name__ == "__main__":
    main()
