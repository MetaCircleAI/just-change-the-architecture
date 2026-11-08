"""Build index.html (GitHub Pages) from article.zh.md.  Usage: python build.py"""
import html, re
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent
SITE = "https://metacircleai.github.io/just-change-the-architecture/"
src = (ROOT / "article.zh.md").read_text(encoding="utf-8")

# ---- header: title, authors, affiliations
lines = src.split("\n")
title = lines[0].lstrip("# ").strip()
rest = "\n".join(lines[1:]).lstrip("\n")
authors, rest = rest.split("\n\n", 1)
affils, rest = rest.lstrip("\n").split("\n\n", 1)
def sup(s):
    s = html.escape(s)
    s = re.sub(r"([¹²³⁴])(?:\s*([¹²³⁴]))?", lambda m: "<sup>" + m.group(1) + ("," + m.group(2) if m.group(2) else "") + "</sup>", s)
    return s
sup_map = str.maketrans("¹²³⁴", "1234")
authors_html = sup(authors).translate(sup_map)
affil_items = [a.strip() for a in affils.split("　") if a.strip()]
affils_html = "".join(f'<span>{sup(a).translate(sup_map)}</span>' for a in affil_items)

# ---- figures: image line followed by a "**图 N** caption" paragraph
def figure(m):
    alt, path, label, cap = m.group(1), m.group(2), m.group(3), m.group(4)
    wide = " wide" if label.strip() == "图 1" else ""
    return (f'\n<figure class="fig{wide}"><img src="{path}" alt="{html.escape(alt)}" loading="lazy">'
            f'<figcaption><b>{html.escape(label)}</b>　{html.escape(cap.strip())}</figcaption></figure>\n')
rest = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)\n\n\*\*(图 \d+)\*\*\s*([^\n]+)", figure, rest)

body = markdown.markdown(rest, extensions=["tables"], output_format="html5")
body = re.sub(r"<p><strong>(表 \d+)</strong>", r'<p class="table-caption"><strong>\1</strong>', body)
body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
lede = re.search(r"<p>(.*?)</p>", body, re.S).group(1)
desc = html.escape(re.sub(r"<[^>]+>", "", lede))[:150]

page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}figures/hero_two_rows_3200.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<main class="post">
<header class="post-header">
<h1>{html.escape(title)}</h1>
<p class="authors">{authors_html}</p>
<p class="affils">{affils_html}</p>
</header>
{body}
</main>
</body>
</html>
"""
(ROOT / "index.html").write_text(page, encoding="utf-8")
print("wrote index.html", len(page), "bytes")
