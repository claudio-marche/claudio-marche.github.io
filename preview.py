"""Anteprima locale del sito senza Ruby/Jekyll.

Uso:  python preview.py   poi apri http://127.0.0.1:4000
Le pagine vengono rigenerate a ogni ricarica del browser.
"""
import datetime
import http.server
import os
import shutil
import traceback
import yaml
from liquid import Environment

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_preview")
SKIP = {"preview.py", "_preview", ".venv", "_site", ".git", ".gitignore"}
YEAR = str(datetime.date.today().year)

env = Environment()


def where(seq, key, value):
    return [x for x in seq if str(x.get(key)) == str(value)]


def group_by(seq, key):
    groups = {}
    for x in seq:
        groups.setdefault(str(x[key]), []).append(x)
    return [{"name": n, "items": i, "size": len(i)} for n, i in groups.items()]


def sort(seq, key=None):
    return sorted(seq, key=lambda x: x[key]) if key else sorted(seq)


env.add_filter("relative_url", lambda s: s)
env.add_filter("where", where)
env.add_filter("group_by", group_by)
env.add_filter("sort", sort)


def build():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)

    site = yaml.safe_load(open(os.path.join(ROOT, "_config.yml"), encoding="utf-8"))
    site["data"] = {}
    data_dir = os.path.join(ROOT, "_data")
    for f in os.listdir(data_dir):
        if f.endswith((".yml", ".yaml")):
            with open(os.path.join(data_dir, f), encoding="utf-8") as fh:
                site["data"][os.path.splitext(f)[0]] = yaml.safe_load(fh)

    with open(os.path.join(ROOT, "_layouts", "default.html"), encoding="utf-8") as fh:
        layout = fh.read().replace("'now' | date: \"%Y\"", "'" + YEAR + "'")

    for name in os.listdir(ROOT):
        if name in SKIP or name.startswith((".", "_")):
            continue
        src = os.path.join(ROOT, name)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(OUT, name), dirs_exist_ok=True)
            continue
        with open(src, encoding="utf-8", errors="ignore") as fh:
            raw = fh.read()
        if not (name.endswith(".html") and raw.startswith("---")):
            shutil.copy(src, OUT)
            continue
        _, front, body = raw.split("---", 2)
        page = yaml.safe_load(front) or {}
        page["url"] = page.get("permalink", "/" if name == "index.html" else "/" + name)
        content = env.from_string(body).render(site=site, page=page)
        html = env.from_string(layout).render(site=site, page=page, content=content)
        dest = os.path.join(OUT, page["url"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(html)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=OUT, **kwargs)

    def do_GET(self):
        if self.path.endswith("/") or self.path.endswith(".html"):
            try:
                build()
            except Exception:
                traceback.print_exc()
        super().do_GET()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    build()
    print(f"Anteprima su http://127.0.0.1:{port}  (Ctrl+C per fermare)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
