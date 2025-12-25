#!/usr/bin/env python3
"""
Static site generator (no JS) for a single-service, multi-city site.

Cloudflare Pages:
- Build command: (empty)
- Output directory: public

URL structure:
- /<city>-<state>/  e.g. /los-angeles-ca/

SEO rules enforced:
- Exactly one H1 per page
- <title> == H1
- Title <= 70 characters
- Controlled H2 set (city pages only use headings from H2_HEADINGS)
- Avoid over-repeating city name in body copy
- Cost section near the bottom
- Natural CTA at the bottom (exact text required)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import html
import re


# -----------------------
# CONFIG
# -----------------------
@dataclass(frozen=True)
class SiteConfig:
    # Service phrasing tuned to include strong close variants (peephole + door viewer).
    service_name: str = "Peephole & Door Viewer Installation"
    brand_name: str = "Peephole Installation Company"
    cta_text: str = "Get Free Estimate"
    cta_href: str = "mailto:hello@example.com?subject=Free%20Quote%20Request"
    output_dir: Path = Path("public")
    cost_low: int = 110
    cost_high: int = 220


CONFIG = SiteConfig()

# Controlled H2 set (city pages ONLY pull headings from this list)
H2_HEADINGS = [
    "Peephole vs Door Viewer",
    "Can You Add a Peephole to a Door?",
    "Where Should a Peephole Go?",
    "Door Types and Common Install Issues",
    "DIY vs Professional Installation",
    "Replacing an Old Door Viewer",
    "How Long Installation Takes",
    "Peephole Installation Cost",
    "Service Area",
]

CITIES: list[tuple[str, str]] = [
    ("Los Angeles", "CA"),
    ("New York", "NY"),
    ("Chicago", "IL"),
    ("Houston", "TX"),
    ("Phoenix", "AZ"),
    ("Philadelphia", "PA"),
    ("San Antonio", "TX"),
    ("San Diego", "CA"),
    ("Dallas", "TX"),
    ("San Jose", "CA"),
    ("Austin", "TX"),
    ("Jacksonville", "FL"),
    ("Fort Worth", "TX"),
    ("Columbus", "OH"),
    ("Charlotte", "NC"),
    ("San Francisco", "CA"),
    ("Indianapolis", "IN"),
    ("Seattle", "WA"),
    ("Denver", "CO"),
    ("Washington", "DC"),
]

# Prefer local images so it always works on Cloudflare Pages.
LOCAL_IMAGE_CITY = "/assets/door-viewer.jpg"
LOCAL_IMAGE_HOME = "/assets/front-door.jpg"


# -----------------------
# HELPERS
# -----------------------
def esc(s: str) -> str:
    return html.escape(s, quote=True)


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"&", " and ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def city_state_slug(city: str, state: str) -> str:
    return f"{slugify(city)}-{slugify(state)}"


def clamp_title(title: str, max_chars: int = 70) -> str:
    if len(title) <= max_chars:
        return title
    return title[: max_chars - 1].rstrip() + "…"


def make_city_h1(service: str, city: str, state: str) -> str:
    return clamp_title(f"{service} in {city}, {state}", 70)


def toolbar_html() -> str:
    return f"""
<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="/">{esc(CONFIG.brand_name)}</a>
    <div class="topbar-actions">
      <a class="toplink" href="/">Home</a>
      <a class="btn btn-top" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    </div>
  </div>
</div>
""".rstrip()


CSS = """
:root {
  --bg: #0b1b33;
  --bg2: #102a4d;
  --text: #0f172a;
  --muted: #475569;
  --card: #ffffff;
  --line: #e2e8f0;
  --cta: #f97316;
  --cta-hover: #ea580c;
  --max: 980px;
  --radius: 14px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
  color: var(--text);
  background: #f8fafc;
  line-height: 1.55;
  padding-top: 58px; /* room for fixed toolbar */
}

/* Fixed top toolbar (all pages) */
.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 58px;
  background: rgba(255,255,255,0.98);
  border-bottom: 1px solid var(--line);
  z-index: 999;
  backdrop-filter: blur(8px);
}

.topbar-inner {
  max-width: var(--max);
  margin: 0 auto;
  height: 100%;
  padding: 0 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.brand {
  font-weight: 800;
  text-decoration: none;
  color: #0b1b33;
  letter-spacing: -0.01em;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.toplink {
  text-decoration: none;
  color: #0f172a;
  font-size: 13px;
}

header {
  background: linear-gradient(135deg, var(--bg), var(--bg2));
  color: white;
  padding: 44px 18px 34px;
}

.wrap { max-width: var(--max); margin: 0 auto; }

.hero {
  display: grid;
  gap: 14px;
  justify-items: center;
  text-align: center;
}

.hero h1 {
  margin: 0;
  font-size: 26px;
  letter-spacing: -0.01em;
}

.sub {
  margin: 0;
  color: rgba(255,255,255,0.86);
  max-width: 68ch;
  font-size: 14px;
}

.btn {
  display: inline-block;
  padding: 10px 14px;
  background: var(--cta);
  color: white;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 800;
  font-size: 13px;
  border: 0;
}

.btn:hover { background: var(--cta-hover); }

.btn-top { padding: 9px 12px; }

main { padding: 24px 18px 42px; }

.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: 0 8px 20px rgba(2, 6, 23, 0.05);
}

.grid { display: grid; gap: 16px; }

.img {
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid var(--line);
}

.img img { display: block; width: 100%; height: auto; }

h2 {
  font-size: 16px;
  margin: 18px 0 8px;
  letter-spacing: -0.01em;
}

p { margin: 0 0 10px; color: var(--text); }
ul { margin: 10px 0 14px 18px; color: var(--text); }
li { margin: 6px 0; }

hr { border: none; border-top: 1px solid var(--line); margin: 18px 0; }

.muted { color: var(--muted); font-size: 13px; }

footer {
  background: linear-gradient(135deg, var(--bg), var(--bg2));
  color: rgba(255,255,255,0.9);
  padding: 34px 18px;
}

.footer-card { max-width: var(--max); margin: 0 auto; text-align: center; }

.footer-card h2 { color: white; margin: 0 0 10px; font-size: 18px; }

.footer-card p { color: rgba(255,255,255,0.85); }

.small { margin-top: 18px; font-size: 12px; color: rgba(255,255,255,0.7); }

.links a {
  color: rgba(255,255,255,0.9);
  text-decoration: underline;
  margin: 0 10px;
  font-size: 13px;
}

.pill {
  display: inline-block;
  padding: 4px 10px;
  background: #eef2ff;
  border: 1px solid #e0e7ff;
  color: #1e3a8a;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 14px;
}

.table th, .table td {
  text-align: left;
  padding: 10px 10px;
  border-top: 1px solid var(--line);
  vertical-align: top;
}

.table th {
  color: #0f172a;
  background: #f1f5f9;
  border-top: 1px solid var(--line);
}

/* Clean city buttons (simple, uncluttered) */
.city-grid {
  list-style: none;
  padding: 0;
  margin: 10px 0 0;
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.city-grid a {
  display: block;
  text-decoration: none;
  color: #0f172a;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 700;
  font-size: 14px;
}

.city-grid a:hover {
  border-color: #cbd5e1;
}
""".strip()


# -----------------------
# HTML SHELL
# -----------------------
def base_html(*, title: str, canonical_path: str, description: str, body_inner: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{esc(canonical_path)}" />
  <style>
{CSS}
  </style>
</head>
<body>
{toolbar_html()}
{body_inner}
</body>
</html>
"""


# -----------------------
# CONTENT (shared)
# -----------------------
def shared_sections_html(*, city: str | None = None, state: str | None = None) -> str:
    # Keep city mentions light to avoid repetition.
    local_line = ""
    if city and state:
        local_line = f' <span class="muted">Serving {esc(city)}, {esc(state)}.</span>'

    return f"""
<h2>{esc(H2_HEADINGS[0])}</h2>
<p>
  People use “peephole” and “door viewer” for the same thing. It is a small lens set through the door.
  It lets you see outside before you open.{local_line}
</p>

<h2>{esc(H2_HEADINGS[1])}</h2>
<p>
  In many cases, yes. A pro can add a viewer to a solid wood door, a steel door, or an apartment entry door.
  The key is matching the viewer to the door thickness and drilling a clean hole.
</p>

<h2>{esc(H2_HEADINGS[2])}</h2>
<p>
  Place it at eye level for the main user. Many installs land around 58–60 inches from the floor.
  If more than one person uses the door, pick a middle height that still feels natural.
</p>

<h2>{esc(H2_HEADINGS[3])}</h2>
<p>
  Wood doors drill fast. Metal doors can take longer and may need different bits.
  Doors with panels, glass, or reinforcements can limit where the hole can go.
</p>

<h2>{esc(H2_HEADINGS[4])}</h2>
<p>
  DIY can work if you have the right tools and a simple door. A pro helps avoid splintering,
  a crooked hole, or a loose fit. This matters most on metal or finished doors.
</p>

<h2>{esc(H2_HEADINGS[5])}</h2>
<p>
  Replace a viewer when the lens looks cloudy, the tube spins, or the angle feels narrow.
  If the old hole is worn or oversized, a pro can recommend a size that fits well.
</p>

<h2>{esc(H2_HEADINGS[6])}</h2>
<p>
  Many installs finish in one visit. Extra time may be needed if the old hardware is stuck,
  the hole needs repair, or the door material is hard to drill.
</p>
""".rstrip()


# -----------------------
# PAGES
# -----------------------
def city_page(*, city: str, state: str) -> str:
    h1 = make_city_h1(CONFIG.service_name, city, state)
    title = h1  # EXACT match per your rule

    description = clamp_title(
        f"{CONFIG.service_name} pricing, placement, and install details for {city}, {state}.",
        155,
    )

    canonical = f"/{city_state_slug(city, state)}/"

    body_inner = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      A clear guide to choosing a door viewer, placing it at the right height, and getting a clean install.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <div class="grid">
    <section class="card">
      <div class="pill">Local install guide</div>

      <div class="img" style="margin-top:12px;">
        <img src="{esc(LOCAL_IMAGE_CITY)}" alt="Door viewer installed in a front door" loading="lazy" />
      </div>

      {shared_sections_html(city=city, state=state)}

      <hr />

      <h2>{esc(H2_HEADINGS[7])}</h2>
      <p class="muted">
        Estimated installed cost in {esc(city)}, {esc(state)} (many projects):
      </p>

      <table class="table" aria-label="Cost estimate table">
        <thead>
          <tr>
            <th>Service</th>
            <th>Typical range</th>
            <th>What moves the price</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{esc(CONFIG.service_name)}</td>
            <td>${CONFIG.cost_low}–${CONFIG.cost_high}</td>
            <td>Door material, thickness, patching/resizing, viewer quality</td>
          </tr>
        </tbody>
      </table>

      <p class="muted" style="margin-top:10px;">
        Final pricing depends on the door, hardware choice, and any repair work around the hole.
      </p>

      <hr />

      <h2>{esc(H2_HEADINGS[8])}</h2>
      <p>
        We schedule work across the metro area. If you are nearby, you can request a quote and we will confirm fit and timing.
      </p>
    </section>
  </div>
</main>

<footer>
  <div class="footer-card">
    <h2>Next steps</h2>
    <p>Ready to move forward? Request a free quote</p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    <div class="small">
      © {esc(CONFIG.brand_name)}. All rights reserved.
      <div class="links" style="margin-top:10px;">
        <a href="/">Home</a>
      </div>
    </div>
  </div>
</footer>
""".rstrip()

    return base_html(title=title, canonical_path=canonical, description=description, body_inner=body_inner)


def homepage(*, cities: list[tuple[str, str]]) -> str:
    # Non-location H1 (per your requirement). Keep it short and human.
    h1 = clamp_title(CONFIG.service_name, 70)
    title = h1

    description = clamp_title(
        "Simple guide to door peephole and door viewer installation, placement, and typical costs.",
        155,
    )

    city_links = "\n".join(
        f'<li><a href="{esc("/" + city_state_slug(city, state) + "/")}">{esc(city)}, {esc(state)}</a></li>'
        for city, state in cities
    )

    body_inner = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      Add a clear view to your front door. Learn what gets installed, where it goes, and what the work tends to cost.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <section class="card">
    <div class="pill">Straight answers</div>

    <div class="img" style="margin-top:12px;">
      <img src="{esc(LOCAL_IMAGE_HOME)}" alt="Front door and hardware" loading="lazy" />
    </div>

    {shared_sections_html()}

    <hr />

    <h2>{esc(H2_HEADINGS[7])}</h2>
    <p class="muted">
      Many installs fall in the ${CONFIG.cost_low}–${CONFIG.cost_high} range. Door material and repair work can change that.
    </p>

    <hr />

    <h2>Choose your city</h2>
    <p class="muted">Select a location for a page with local pricing context and the same full guide.</p>

    <!-- Clean city buttons (grid) -->
    <ul class="city-grid">
      {city_links}
    </ul>
  </section>
</main>

<footer>
  <div class="footer-card">
    <h2>Next steps</h2>
    <p>Ready to move forward? Request a free quote</p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    <div class="small">© {esc(CONFIG.brand_name)}. All rights reserved.</div>
  </div>
</footer>
""".rstrip()

    return base_html(title=title, canonical_path="/", description=description, body_inner=body_inner)


# -----------------------
# GENERATION
# -----------------------
def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    CONFIG.output_dir.mkdir(parents=True, exist_ok=True)

    # Homepage
    write_file(CONFIG.output_dir / "index.html", homepage(cities=CITIES))

    # City pages
    for city, state in CITIES:
        slug = city_state_slug(city, state)
        out = CONFIG.output_dir / slug / "index.html"
        write_file(out, city_page(city=city, state=state))

    print(f"✅ Generated {1 + len(CITIES)} pages into: {CONFIG.output_dir.resolve()}")


if __name__ == "__main__":
    main()
