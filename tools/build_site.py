"""Builds the quarry-site pages from the app's strings.xml, so the web policy says exactly what the app says.

Usage: python build_site.py <quarry repo> <site folder>
"""
import sys, re, shutil, pathlib, html
import xml.etree.ElementTree as ET

app = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
res = app / "app/src/main/res"
LANGS = [("en", "values", "English"), ("fr", "values-fr", "Français"), ("ko", "values-ko", "한국어")]
SECTIONS = ["who", "collect", "use", "see", "keep", "where", "rights", "children", "changes"]


def android_text(raw: str) -> str:
    """Undoes the Android escapes: \\' \\" \\u00a0 \\n."""
    raw = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), raw)
    return raw.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n")


def strings(folder: str) -> dict:
    root = ET.parse(res / folder / "strings.xml").getroot()
    return {e.get("name"): android_text("".join(e.itertext())) for e in root.findall("string")}


texts = {code: strings(folder) for code, folder, _ in LANGS}

LOGO = ('<svg viewBox="64 64 392 392" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" '
        'd="M140,64H340L416,140V320L388,348L456,416L416,456L348,388L320,416H140L64,340V140L140,64ZM176,152L152,176V304L176,328H276L236,288L288,236L328,276V176L304,152H176Z"/></svg>')

STYLE = """
@font-face { font-family: "Space Grotesk"; src: url("{root}assets/space_grotesk.ttf"); font-weight: 300 700; font-display: swap; }
:root { --paper:#0E141B; --card:#17202A; --field:#243140; --line:#2E3B4A; --ink:#F4F2E9; --muted:#9AA5B1; --faint:#6B7684;
        --lavender:#C6B4FF; --on-lavender:#1B1530; --lime:#D4F06B; --caution:#F5C25A; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--paper); color: var(--ink); font: 16px/1.6 "Segoe UI", Roboto, -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", Arial, sans-serif; }
main { max-width: 760px; margin: 0 auto; padding: 32px 20px 56px; }
a { color: var(--lavender); }
.display, h1, h2, .wordmark, .chip, .label, .button, nav button { font-family: "Space Grotesk", sans-serif; }
header { display: flex; align-items: center; gap: 12px; margin-bottom: 40px; }
header a.home { display: flex; align-items: center; gap: 12px; color: var(--ink); text-decoration: none; }
header svg { width: 34px; height: 34px; color: var(--ink); }
.wordmark { font-weight: 600; font-size: 26px; letter-spacing: -0.4px; }
.chip { margin-left: auto; font-weight: 600; font-size: 12px; letter-spacing: 1.6px; text-transform: uppercase; color: var(--on-lavender); background: var(--lavender); padding: 6px 14px; border-radius: 99px; white-space: nowrap; }
h1 { font-weight: 600; font-size: clamp(34px, 7vw, 56px); line-height: 1.04; letter-spacing: -1px; }
h1 em { font-style: normal; color: var(--lavender); }
.lead { color: var(--muted); font-size: 18px; margin-top: 16px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 20px 22px; margin-top: 14px; }
.label { font-weight: 600; font-size: 12px; letter-spacing: 1.6px; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
h2 { font-weight: 600; font-size: 19px; margin-bottom: 6px; }
.card p { color: var(--muted); }
.card p + p { margin-top: 8px; }
.button { display: inline-block; margin-top: 22px; margin-right: 10px; padding: 13px 22px; border-radius: 14px; font-weight: 600; text-decoration: none; background: var(--lavender); color: var(--on-lavender); }
.button.secondary { background: var(--field); color: var(--ink); }
nav.langs { display: flex; gap: 8px; margin: 24px 0 8px; flex-wrap: wrap; }
nav.langs button { border: 1px solid var(--line); background: var(--field); color: var(--ink); border-radius: 99px; padding: 7px 16px; font-size: 14px; font-weight: 600; cursor: pointer; }
nav.langs button[aria-pressed="true"] { background: var(--lavender); color: var(--on-lavender); border-color: var(--lavender); }
section[lang] { display: none; }
section[lang].shown { display: block; }
section[lang="ko"] { word-break: keep-all; }
.card p, .lead { overflow-wrap: anywhere; }
.noscript section[lang="en"] { display: block; }
footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line); color: var(--faint); font-size: 14px; display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
"""

SCRIPT = """
<script>
  // Shows one language: the one asked in the address (?lang=fr), else the browser's, else English.
  document.documentElement.classList.remove("noscript");
  const langs = [...document.querySelectorAll("section[lang]")].map(s => s.lang);
  const asked = new URLSearchParams(location.search).get("lang");
  const browser = (navigator.language || "en").slice(0, 2);
  function show(lang) {
    document.querySelectorAll("section[lang]").forEach(s => s.classList.toggle("shown", s.lang === lang));
    document.querySelectorAll("nav.langs button").forEach(b => b.setAttribute("aria-pressed", b.dataset.lang === lang));
    document.documentElement.lang = lang;
  }
  document.querySelectorAll("nav.langs button").forEach(b => b.addEventListener("click", () => show(b.dataset.lang)));
  show(langs.includes(asked) ? asked : langs.includes(browser) ? browser : "en");
</script>
"""


def page(title: str, root: str, body: str, chip: str) -> str:
    return f"""<!doctype html>
<html lang="en" class="noscript">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" href="{root}assets/logo.svg" type="image/svg+xml">
<style>{STYLE.replace("{root}", root)}</style>
</head>
<body>
<main>
<header><a class="home" href="{root}">{LOGO}<span class="wordmark">quarry</span></a><span class="chip">{chip}</span></header>
{body}
<footer><span>Quarry · a student project</span><a href="mailto:quarrysupport@gmail.com">quarrysupport@gmail.com</a></footer>
</main>
{SCRIPT}
</body>
</html>
"""


def lang_nav() -> str:
    return '<nav class="langs">' + "".join(f'<button type="button" data-lang="{c}">{n}</button>' for c, _, n in LANGS) + "</nav>"


# ---------------------------------------------------------------- privacy/index.html
sections = []
for code, _, _ in LANGS:
    t = texts[code]
    cards = []
    for key in SECTIONS:
        paras = []
        i = 1
        while f"pp_{key}_{i}" in t:
            paras.append(f"<p>{html.escape(t[f'pp_{key}_{i}'])}</p>")
            i += 1
        cards.append(f'<div class="card"><h2>{html.escape(t[f"pp_{key}"])}</h2>{"".join(paras)}</div>')
    sections.append(f'<section lang="{code}"><h1>{html.escape(t["pp_title"])}</h1>'
                    f'<p class="lead">{html.escape(t["pp_subtitle"])}</p>{"".join(cards)}</section>')
privacy = page("Quarry · Privacy policy", "../", lang_nav() + "".join(sections), "Privacy policy")

# ---------------------------------------------------------------- index.html
INDEX = {
    "en": ("Hide-and-seek, <em>for real.</em>",
           "Quarry turns your neighbourhood into the arena. Friends split into hunters and hunted, step outside and play a real chase: pings give away a direction, Bluetooth confirms the catch, and your phone beats like a heart when a hunter gets close.",
           [("Two modes", "Cop / Robber: catch every robber before the time runs out. Zombie / Survivor: whoever is caught joins the horde, and the survivors race to an extraction zone."),
            ("Closed beta", "Quarry is being tested on Android 10 and later, with Bluetooth and GPS. Ask the team for an invitation: quarrysupport@gmail.com.")],
           "Beta presentation (PDF)", "Privacy policy"),
    "fr": ("Le cache-cache, <em>en vrai.</em>",
           "Quarry transforme ton quartier en arène. Les amis se répartissent entre chasseurs et chassés, sortent, et jouent une vraie traque : les pings trahissent une direction, le Bluetooth confirme la capture, et ton téléphone bat comme un cœur quand un chasseur approche.",
           [("Deux modes", "Gendarmes / Voleurs : attrapez tous les voleurs avant la fin du temps. Zombie / Survivant : qui se fait attraper rejoint la horde, et les survivants foncent vers une zone d'extraction."),
            ("Bêta fermée", "Quarry est en test sur Android 10 et plus, avec Bluetooth et GPS. Demande une invitation à l'équipe : quarrysupport@gmail.com.")],
           "Présentation de la bêta (PDF, en anglais)", "Politique de confidentialité"),
    "ko": ("현실에서 즐기는 <em>진짜 숨바꼭질.</em>",
           "Quarry는 우리 동네를 경기장으로 바꿔요. 친구들이 추격자와 도망자로 나뉘어 밖으로 나가 진짜 추격전을 벌여요. 핑은 방향을 알려 주고, 블루투스가 태그를 확인하며, 추격자가 가까워지면 휴대폰이 심장처럼 뛰어요.",
           [("두 가지 모드", "경찰 / 도둑: 시간이 끝나기 전에 도둑을 모두 잡으세요. 좀비 / 생존자: 잡힌 사람은 무리에 합류하고, 생존자는 탈출 구역으로 달려가요."),
            ("비공개 베타", "Quarry는 블루투스와 GPS가 있는 Android 10 이상에서 테스트 중이에요. 초대를 받으려면 팀에 연락하세요: quarrysupport@gmail.com")],
           "베타 소개 (PDF, 영어)", "개인정보 처리방침"),
}
sections = []
for code, (title, lead, cards, pdf, policy_label) in INDEX.items():
    body = "".join(f'<div class="card"><h2>{html.escape(h)}</h2><p>{html.escape(p)}</p></div>' for h, p in cards)
    sections.append(f'<section lang="{code}"><h1>{title}</h1><p class="lead">{html.escape(lead)}</p>{body}'
                    f'<a class="button" href="quarry-closed-beta.pdf">{html.escape(pdf)}</a>'
                    f'<a class="button secondary" href="privacy/?lang={code}">{html.escape(policy_label)}</a></section>')
index = page("Quarry · Hide-and-seek, for real", "", lang_nav() + "".join(sections), "Closed beta")

# ---------------------------------------------------------------- write
(out / "privacy").mkdir(parents=True, exist_ok=True)
(out / "assets").mkdir(exist_ok=True)
(out / "index.html").write_text(index, encoding="utf-8")
(out / "privacy/index.html").write_text(privacy, encoding="utf-8")
(out / "assets/logo.svg").write_text(LOGO.replace("currentColor", "#F4F2E9").replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" '), encoding="utf-8")
shutil.copyfile(res / "font/space_grotesk.ttf", out / "assets/space_grotesk.ttf")
shutil.copyfile(app / "docs/licenses/SpaceGrotesk-OFL.txt", out / "assets/SpaceGrotesk-OFL.txt")
shutil.copyfile(app / "docs/beta/quarry-closed-beta.pdf", out / "quarry-closed-beta.pdf")
# GitHub Pages: serve the files as they are (no Jekyll processing).
(out / ".nojekyll").write_text("", encoding="utf-8")
print("built", out)
