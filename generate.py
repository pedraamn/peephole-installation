#!/usr/bin/env python3
"""
Static site generator (no JS) for a single-service, multi-city site.

Output:
- ./dist/index.html (homepage)
- ./dist/<city>-<state>/index.html (city pages)  e.g. /los-angeles-ca/

SEO rules enforced:
- Only one H1 per page
- <title> == H1
- Title <= ~70 chars (hard-truncated if needed)
- City+State in URL
- Fixed, controlled H2 set
- Cost section placed near bottom
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import html


# -----------------------
# CONFIG (edit these)
# -----------------------
SERVICE_NAME = "Peephole Installation"
BRAND_NAME = "Peephole Installation Company"
PRIMARY_CTA_TEXT = "Request a Free Quote"
PRIMARY_CTA_HREF = "mailto:hello@example.com?subject=Free%20Quote%20Request"

# A single, controlled H2 set (so headings only come from *here*)
H2_HEADINGS = [
    "What’s included in professional installation",
    "Typical materials and door types",
    "DIY vs professional installation",
    "How long the work usually takes",
    "When to replace an existing door viewer",
    "Frequently asked questions",
    "Cost estimate",
]

# NOTE: put major cities here (you can expand to 100+ easily)
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

# “Only number you need to generate”
# You can set a global range, or make a per-state override later.
DEFAULT_COST_LOW = 110
DEFAULT_COST_HIGH = 220

OUTPUT_DIR = Path("public")


# -----------------------
# HELPERS
# -----------------------
def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"&", " and ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s

def city_state_slug(city: str, state: str) -> str:
    return f"{slugify(city)}-{slugify(state)}"

def esc(s: str) -> str:
    return html.escape(s, quote=True)

def clamp_title(title: str, max_chars: int = 70) -> str:
    # Hard truncate to be safe, but avoid chopping in the middle of a multi-byte char.
    if len(title) <= max_chars:
        return title
    return title[: max_chars - 1].rstrip() + "…"

def make_h1_title(service: str, city: str, state: str) -> str:
    # Try to pack keywords early: "Peephole Installation in Los Angeles, CA"
    base = f"{service} in {city}, {state}"
    return clamp_title(base, 70)

def unsplash_image_url(query: str) -> str:
    # Royalty-free photo source (served by Unsplash). No API key needed.
    # This returns a random photo matching the query.
    q = slugify(query).replace("-", ",")
    return f"https://source.unsplash.com/1600x900/?{esc(q)}"


# -----------------------
# TEMPLATES
# -----------------------
def base_html(*, title: str, canonical_path: str, body: str, description: str) -> str:
    # Minimal, clean CSS; no JS.
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{esc(canonical_path)}" />
  <style>
    :root {{
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
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
      color: var(--text);
      background: #f8fafc;
      line-height: 1.55;
    }}
    header {{
      background: linear-gradient(135deg, var(--bg), var(--bg2));
      color: white;
      padding: 44px 18px 34px;
    }}
    .wrap {{
      max-width: var(--max);
      margin: 0 auto;
    }}
    .hero {{
      display: grid;
      gap: 14px;
      justify-items: center;
      text-align: center;
    }}
    .hero h1 {{
      margin: 0;
      font-size: 26px;
      letter-spacing: -0.01em;
    }}
    .sub {{
      margin: 0;
      color: rgba(255,255,255,0.86);
      max-width: 68ch;
      font-size: 14px;
    }}
    .btn {{
      display: inline-block;
      padding: 10px 14px;
      background: var(--cta);
      color: white;
      border-radius: 10px;
      text-decoration: none;
      font-weight: 700;
      font-size: 13px;
    }}
    .btn:hover {{ background: var(--cta-hover); }}
    main {{
      padding: 24px 18px 42px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 18px;
      box-shadow: 0 8px 20px rgba(2, 6, 23, 0.05);
    }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .img {{
      overflow: hidden;
      border-radius: 12px;
      border: 1px solid var(--line);
    }}
    .img img {{
      display: block;
      width: 100%;
      height: auto;
    }}
    h2 {{
      font-size: 16px;
      margin: 18px 0 8px;
      letter-spacing: -0.01em;
    }}
    p {{ margin: 0 0 10px; color: var(--text); }}
    ul {{ margin: 10px 0 14px 18px; color: var(--text); }}
    li {{ margin: 6px 0; }}
    hr {{
      border: none;
      border-top: 1px solid var(--line);
      margin: 18px 0;
    }}
    .muted {{ color: var(--muted); font-size: 13px; }}
    footer {{
      background: linear-gradient(135deg, var(--bg), var(--bg2));
      color: rgba(255,255,255,0.9);
      padding: 34px 18px;
    }}
    .footer-card {{
      max-width: var(--max);
      margin: 0 auto;
      text-align: center;
    }}
    .footer-card h2 {{
      color: white;
      margin: 0 0 10px;
      font-size: 18px;
    }}
    .footer-card p {{ color: rgba(255,255,255,0.85); }}
    .footer-card a {{ margin-top: 10px; }}
    .small {{
      margin-top: 18px;
      font-size: 12px;
      color: rgba(255,255,255,0.7);
    }}
    .links a {{
      color: rgba(255,255,255,0.9);
      text-decoration: underline;
      margin: 0 10px;
      font-size: 13px;
    }}
    .pill {{
      display: inline-block;
      padding: 4px 10px;
      background: #eef2ff;
      border: 1px solid #e0e7ff;
      color: #1e3a8a;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }}
    .table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 14px;
    }}
    .table th, .table td {{
      text-align: left;
      padding: 10px 10px;
      border-top: 1px solid var(--line);
      vertical-align: top;
    }}
    .table th {{
      color: #0f172a;
      background: #f1f5f9;
      border-top: 1px solid var(--line);
    }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""

def city_page(*, city: str, state: str, cost_low: int, cost_high: int) -> str:
    # Enforce SEO rule: H1 == Title
    h1 = make_h1_title(SERVICE_NAME, city, state)
    title = h1  # EXACT match per your rule

    # Keep city mentions controlled: use it in H1 + a couple of natural spots only.
    # Use “the area” / “locally” elsewhere.
    description = clamp_title(
        f"Typical {SERVICE_NAME.lower()} pricing, what affects cost, DIY vs pro, and what’s included — for {city}, {state}.",
        155,
    )

    image_src = unsplash_image_url(f"front door peephole installation")

    canonical = f"/{city_state_slug(city, state)}/"

    body = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      Straightforward pricing guidance, what affects the total, and what you typically get with a professional install.
    </p>
    <a class="btn" href="{esc(PRIMARY_CTA_HREF)}">{esc(PRIMARY_CTA_TEXT)}</a>
  </div>
</header>

<main class="wrap">
  <div class="grid">
    <section class="card">
      <div class="pill">Local cost guide</div>

      <div class="img" style="margin-top:12px;">
        <img src="{image_src}" alt="Door viewer installed in a front door" loading="lazy" />
      </div>

      <h2>{esc(H2_HEADINGS[0])}</h2>
      <p>
        Contractors typically handle measurement, drilling, clean installation, and alignment so the viewer sits flush and works smoothly.
        If your door material is harder (metal) or requires special bits, that can increase labor time.
      </p>

      <h2>{esc(H2_HEADINGS[1])}</h2>
      <p>
        Common installs include standard wood doors, apartment entry doors, and security doors.
        Costs vary based on door thickness, viewer quality, and whether the existing hole needs to be resized or repaired.
      </p>

      <h2>{esc(H2_HEADINGS[2])}</h2>
      <p>
        DIY can be workable if you already have the right drill bits and the door is easy to drill.
        Pros reduce the risk of splintering, misalignment, or cosmetic damage—especially on metal or reinforced doors.
      </p>

      <h2>{esc(H2_HEADINGS[3])}</h2>
      <p>
        Most straightforward installs are typically completed in a single visit.
        Additional time may be needed when replacing a damaged viewer, patching an oversized hole, or working on specialty doors.
      </p>

      <h2>{esc(H2_HEADINGS[4])}</h2>
      <p>
        Replacement is common when the lens is cloudy, the viewer is loose, the mechanism sticks, or you want a wider viewing angle.
        If the current hole is worn or enlarged, a pro can recommend a compatible replacement and secure fit.
      </p>

      <h2>{esc(H2_HEADINGS[5])}</h2>
      <ul>
        <li><strong>Do I need landlord approval?</strong> In many rentals, yes—check your lease or ask before drilling.</li>
        <li><strong>Will it damage the door?</strong> With correct tools and technique, the hole is clean and the trim sits flush.</li>
        <li><strong>Can you install on metal doors?</strong> Often yes, but it may require specialty bits and careful drilling.</li>
        <li><strong>What height should it be?</strong> Typically around eye level for the primary user; pros can help choose placement.</li>
      </ul>

      <hr />

      <h2>{esc(H2_HEADINGS[6])}</h2>
      <p class="muted">
        Estimated installed cost in {esc(city)}, {esc(state)} (most projects): 
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
            <td>{esc(SERVICE_NAME)}</td>
            <td>${cost_low}–${cost_high}</td>
            <td>Door material, thickness, resizing/repair, viewer quality</td>
          </tr>
        </tbody>
      </table>

      <p class="muted" style="margin-top:10px;">
        These are “typical” ranges—actual quotes can vary by door type, hardware choice, and job complexity.
      </p>

      <p style="margin-top:14px;">
        <a href="/articles/">More cost guides</a>
      </p>
    </section>
  </div>
</main>

<footer>
  <div class="footer-card">
    <h2>Ready to move forward?</h2>
    <p>Request a free quote and we’ll confirm the right door viewer and installation approach.</p>
    <a class="btn" href="{esc(PRIMARY_CTA_HREF)}">{esc(PRIMARY_CTA_TEXT)}</a>
    <div class="small">
      © {esc(BRAND_NAME)}. All rights reserved.
      <div class="links" style="margin-top:10px;">
        <a href="/">Home</a>
        <a href="/articles/">Cost Guides</a>
      </div>
    </div>
  </div>
</footer>
"""
    return base_html(title=title, canonical_path=canonical, body=body, description=description)

def homepage(*, cities: list[tuple[str, str]]) -> str:
    # One H1 on homepage too
    h1 = clamp_title(f"{SERVICE_NAME} Cost by City (US)", 70)
    title = h1

    description = clamp_title(
        f"Browse {SERVICE_NAME.lower()} cost estimates across major US cities. Learn what affects price and when to hire a pro.",
        155,
    )

    # Simple image for home
    image_src = unsplash_image_url("front door home security")

    # Build list of links
    links = []
    for city, state in cities:
        path = f"/{city_state_slug(city, state)}/"
        links.append(f'<li><a href="{esc(path)}">{esc(city)}, {esc(state)}</a></li>')

    body = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      Quick, scannable estimates and the factors that usually change the price. Pick your city to get started.
    </p>
    <a class="btn" href="{esc(PRIMARY_CTA_HREF)}">{esc(PRIMARY_CTA_TEXT)}</a>
  </div>
</header>

<main class="wrap">
  <section class="card">
    <div class="pill">Nationwide overview</div>

    <div class="img" style="margin-top:12px;">
      <img src="{image_src}" alt="Front door and hardware" loading="lazy" />
    </div>

    <h2>How pricing usually works</h2>
    <p>
      Installation cost typically depends on door material (wood vs metal), door thickness, whether a hole already exists,
      and the type of door viewer you choose.
    </p>

    <h2>Choose a city</h2>
    <p class="muted">City pages use clean URLs that include city + state for clarity.</p>
    <ul>
      {''.join(links)}
    </ul>

    <p style="margin-top:14px;">
      <a href="/articles/">More cost guides</a>
    </p>
  </section>
</main>

<footer>
  <div class="footer-card">
    <h2>Ready to move forward?</h2>
    <p>Request a free quote and we’ll confirm the right door viewer and installation approach.</p>
    <a class="btn" href="{esc(PRIMARY_CTA_HREF)}">{esc(PRIMARY_CTA_TEXT)}</a>
    <div class="small">© {esc(BRAND_NAME)}. All rights reserved.</div>
  </div>
</footer>
"""
    return base_html(title=title, canonical_path="/", body=body, description=description)


# -----------------------
# GENERATION
# -----------------------
def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Homepage
    write_file(OUTPUT_DIR / "index.html", homepage(cities=CITIES))

    # City pages
    for city, state in CITIES:
        slug = city_state_slug(city, state)
        out = OUTPUT_DIR / slug / "index.html"
        html_page = city_page(
            city=city,
            state=state,
            cost_low=DEFAULT_COST_LOW,
            cost_high=DEFAULT_COST_HIGH,
        )
        write_file(out, html_page)

    print(f"✅ Generated {1 + len(CITIES)} pages into: {OUTPUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
