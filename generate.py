#!/usr/bin/env python3
"""
Generate a lightweight static "Peephole Installation Company" site with 100 city pages.
Output structure (Cloudflare Pages friendly):
  public/
    index.html
    los-angeles/index.html
    chicago/index.html
    ...
Run:
  python3 generate.py
Deploy:
  Set Cloudflare Pages build output to: public
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple

# -----------------------------
# CONFIG
# -----------------------------

SERVICE_NAME = "Peephole Installation"
BRAND_NAME = "Peephole Installation Company"
PRIMARY_CTA_TEXT = "Get Your Free Estimate"
SECONDARY_CTA_TEXT = "Request a Free Quote"
PHONE = ""  # optional, e.g. "(555) 555-5555"
EMAIL = ""  # optional
BASE_COST_RANGE = (110, 220)  # <- the only numbers we "generate" per page (after multiplier)
NATIONAL_NOTE = "Pricing varies by door type, materials, and complexity. Get a quote for an exact price."

# Royalty-free photo (hotlinked). Swap to "/assets/hero.jpg" if you want local-only.
HERO_IMAGE_URL = (
    "https://images.unsplash.com/photo-1523413651479-597eb2da0ad6"
    "?auto=format&fit=crop&w=1600&q=80"
)

# Optional: city-specific cost multipliers (edit freely).
# If a city isn't in here, it uses 1.00.
COST_MULTIPLIER: Dict[str, float] = {
    "new-york": 1.35,
    "san-francisco": 1.35,
    "san-jose": 1.30,
    "los-angeles": 1.20,
    "san-diego": 1.15,
    "seattle": 1.20,
    "boston": 1.25,
    "washington": 1.20,
    "miami": 1.10,
    "chicago": 1.10,
    "austin": 1.10,
    "denver": 1.10,
    "portland": 1.10,
    "houston": 1.00,
    "dallas": 1.00,
    "phoenix": 0.95,
    "las-vegas": 0.95,
    "atlanta": 1.00,
    "philadelphia": 1.05,
}

# 100 major US cities (city, state, slug)
# (You can replace/expand this list whenever.)
CITIES: List[Tuple[str, str]] = [
    ("New York", "NY"),
    ("Los Angeles", "CA"),
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
    ("Boston", "MA"),
    ("El Paso", "TX"),
    ("Nashville", "TN"),
    ("Detroit", "MI"),
    ("Oklahoma City", "OK"),
    ("Portland", "OR"),
    ("Las Vegas", "NV"),
    ("Memphis", "TN"),
    ("Louisville", "KY"),
    ("Baltimore", "MD"),
    ("Milwaukee", "WI"),
    ("Albuquerque", "NM"),
    ("Tucson", "AZ"),
    ("Fresno", "CA"),
    ("Sacramento", "CA"),
    ("Mesa", "AZ"),
    ("Kansas City", "MO"),
    ("Atlanta", "GA"),
    ("Long Beach", "CA"),
    ("Colorado Springs", "CO"),
    ("Raleigh", "NC"),
    ("Miami", "FL"),
    ("Virginia Beach", "VA"),
    ("Omaha", "NE"),
    ("Oakland", "CA"),
    ("Minneapolis", "MN"),
    ("Tulsa", "OK"),
    ("Tampa", "FL"),
    ("Arlington", "TX"),
    ("Wichita", "KS"),
    ("Bakersfield", "CA"),
    ("Aurora", "CO"),
    ("New Orleans", "LA"),
    ("Cleveland", "OH"),
    ("Anaheim", "CA"),
    ("Honolulu", "HI"),
    ("Santa Ana", "CA"),
    ("Riverside", "CA"),
    ("Corpus Christi", "TX"),
    ("Lexington", "KY"),
    ("Henderson", "NV"),
    ("Stockton", "CA"),
    ("Saint Paul", "MN"),
    ("Cincinnati", "OH"),
    ("St. Louis", "MO"),
    ("Pittsburgh", "PA"),
    ("Greensboro", "NC"),
    ("Anchorage", "AK"),
    ("Plano", "TX"),
    ("Lincoln", "NE"),
    ("Orlando", "FL"),
    ("Irvine", "CA"),
    ("Newark", "NJ"),
    ("Toledo", "OH"),
    ("Durham", "NC"),
    ("Chula Vista", "CA"),
    ("Fort Wayne", "IN"),
    ("Jersey City", "NJ"),
    ("St. Petersburg", "FL"),
    ("Laredo", "TX"),
    ("Madison", "WI"),
    ("Chandler", "AZ"),
    ("Buffalo", "NY"),
    ("Lubbock", "TX"),
    ("Scottsdale", "AZ"),
    ("Reno", "NV"),
    ("Glendale", "AZ"),
    ("Gilbert", "AZ"),
    ("Winston–Salem", "NC"),
    ("North Las Vegas", "NV"),
    ("Norfolk", "VA"),
    ("Chesapeake", "VA"),
    ("Garland", "TX"),
    ("Irving", "TX"),
    ("Hialeah", "FL"),
    ("Fremont", "CA"),
    ("Boise", "ID"),
    ("Richmond", "VA"),
]

OUTPUT_DIR = "public"


# -----------------------------
# HELPERS
# -----------------------------

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s

def money(n: int) -> str:
    return f"${n:,}"

def compute_cost_range(city_slug: str) -> Tuple[int, int]:
    mult = COST_MULTIPLIER.get(city_slug, 1.00)
    low = int(round(BASE_COST_RANGE[0] * mult))
    high = int(round(BASE_COST_RANGE[1] * mult))
    # Keep it sane: ensure low < high and at least a $40 spread.
    if high <= low:
        high = low + 60
    if (high - low) < 40:
        high = low + 60
    return low, high

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def write_file(path: str, content: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def city_page_html(city: str, state: str, city_slug: str) -> str:
    low, high = compute_cost_range(city_slug)
    title = f"{SERVICE_NAME} in {city}, {state} | Cost & Installation"
    meta_desc = (
        f"Typical {SERVICE_NAME.lower()} costs in {city}, {state} range from "
        f"{money(low)} to {money(high)}. Learn what affects pricing and when to hire a pro."
    )
    h1 = f"{SERVICE_NAME} Services in {city}, {state}"
    cost_h2 = f"How Much Does {SERVICE_NAME} Cost in {city}, {state}?"
    cost_sentence = (
        f"In {city}, most {SERVICE_NAME.lower()} jobs run between "
        f"<strong>{money(low)}</strong> and <strong>{money(high)}</strong>. "
        f"{NATIONAL_NOTE}"
    )
    # If you have a domain later, replace canonical base.
    canonical = f"/{city_slug}/"

    # Minimal schema: LocalBusiness + Service (helps rich/AI summary extraction)
    schema = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "{BRAND_NAME}",
  "areaServed": "{city}, {state}",
  "description": "{SERVICE_NAME} services including installation, replacement, and repair.",
  "serviceType": "{SERVICE_NAME}",
  "url": "{canonical}"
}}
</script>""".strip()

    contact_line = ""
    if PHONE or EMAIL:
        parts = []
        if PHONE:
            parts.append(f'<a href="tel:{re.sub(r"[^0-9+]", "", PHONE)}">{PHONE}</a>')
        if EMAIL:
            parts.append(f'<a href="mailto:{EMAIL}">{EMAIL}</a>')
        contact_line = " • " + " • ".join(parts)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{meta_desc}" />
  <link rel="canonical" href="{canonical}" />
  {schema}
  <style>
    :root {{
      --bg: #0b1220;
      --navy: #0f2746;
      --navy2: #0b1d34;
      --ink: #0b1220;
      --text: #0f172a;
      --muted: #475569;
      --line: #e2e8f0;
      --card: #ffffff;
      --accent: #f97316;
      --accent2: #f59e0b;
      --max: 920px;
      --radius: 14px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
      color: var(--text);
      background: #fff;
    }}
    a {{ color: inherit; }}
    .wrap {{ max-width: var(--max); margin: 0 auto; padding: 0 20px; }}
    header.hero {{
      background: radial-gradient(1200px 380px at 50% 0%, #193a67 0%, var(--navy2) 55%, var(--bg) 100%);
      color: #fff;
      padding: 46px 0 36px;
      position: relative;
      overflow: hidden;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
      align-items: center;
    }}
    @media (max-width: 860px) {{
      .hero-grid {{ grid-template-columns: 1fr; }}
      .hero-img {{ display: none; }}
    }}
    h1 {{
      font-size: 26px;
      line-height: 1.2;
      margin: 0 0 10px;
      letter-spacing: 0.2px;
    }}
    .sub {{
      margin: 0 0 16px;
      color: rgba(255,255,255,0.82);
      font-size: 14px;
      line-height: 1.55;
    }}
    .cta {{
      display: inline-block;
      background: linear-gradient(90deg, var(--accent), var(--accent2));
      color: #0b1220;
      text-decoration: none;
      font-weight: 700;
      font-size: 13px;
      padding: 10px 14px;
      border-radius: 10px;
      box-shadow: 0 10px 26px rgba(0,0,0,0.22);
    }}
    .hero-img {{
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: var(--radius);
      overflow: hidden;
      height: 170px;
    }}
    .hero-img img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      filter: saturate(1.05) contrast(1.05);
    }}
    main {{
      padding: 34px 0 24px;
    }}
    .section {{
      padding: 18px 0;
      border-bottom: 1px solid var(--line);
    }}
    h2 {{
      font-size: 16px;
      margin: 0 0 8px;
      color: #0f2a4d;
    }}
    p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.65;
    }}
    .pill {{
      display: inline-block;
      font-size: 12px;
      color: rgba(255,255,255,0.85);
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 999px;
      padding: 6px 10px;
      margin-bottom: 12px;
      background: rgba(255,255,255,0.06);
    }}
    footer.cta-footer {{
      margin-top: 26px;
      background: linear-gradient(180deg, #2a4e7f 0%, #18385f 52%, #0f2746 100%);
      color: #fff;
      padding: 34px 0;
      text-align: center;
    }}
    footer h3 {{
      margin: 0 0 8px;
      font-size: 18px;
    }}
    footer p {{
      color: rgba(255,255,255,0.82);
      margin: 0 auto 14px;
      max-width: 720px;
    }}
    .btn2 {{
      display: inline-block;
      background: #ffffff;
      color: #0b1220;
      text-decoration: none;
      font-weight: 700;
      font-size: 13px;
      padding: 10px 14px;
      border-radius: 10px;
    }}
    .mini {{
      padding: 16px 0 22px;
      text-align: center;
      color: #94a3b8;
      font-size: 12px;
      background: #0b1220;
    }}
    .mini a {{ color: #cbd5e1; text-decoration: none; }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="wrap">
      <div class="pill">{SERVICE_NAME} • {city}, {state}{contact_line}</div>
      <div class="hero-grid">
        <div>
          <h1>{h1}</h1>
          <p class="sub">Fast, clean installs for front doors, apartment doors, and security doors—plus repair and replacement when a viewer is damaged or outdated.</p>
          <a class="cta" href="#quote">{PRIMARY_CTA_TEXT}</a>
        </div>
        <div class="hero-img" aria-hidden="true">
          <img src="{HERO_IMAGE_URL}" alt="Door hardware close-up" loading="lazy" decoding="async" />
        </div>
      </div>
    </div>
  </header>

  <main class="wrap">
    <section class="section">
      <h2>{cost_h2}</h2>
      <p>{cost_sentence}</p>
    </section>

    <section class="section">
      <h2>Door Viewer Installation</h2>
      <p>We install standard and wide-angle door viewers at the right height and alignment so you get a clear view and a secure fit.</p>
    </section>

    <section class="section">
      <h2>How Professional Installation Works</h2>
      <p>Typical jobs include measuring placement, drilling the correct bore size, cleanly seating the viewer hardware, and checking operation from both sides.</p>
    </section>

    <section class="section">
      <h2>Peephole Repair and Replacement</h2>
      <p>If your viewer is loose, scratched, fogged, or misaligned, replacement can restore clarity and reduce draft or wobble.</p>
    </section>

    <section class="section">
      <h2>When You Should Hire a Pro</h2>
      <p>Metal doors, reinforced doors, specialty materials, and incorrect existing holes often need the right bits and hardware to avoid damage.</p>
    </section>

    <section class="section">
      <h2>DIY vs Professional {SERVICE_NAME}</h2>
      <p>DIY can work for straightforward wood doors, but pros typically reduce the risk of chipping, misalignment, and hardware that loosens over time.</p>
    </section>

    <section class="section" id="quote">
      <h2>Flexible Scheduling in {city}</h2>
      <p>Tell us your door type and any existing hole size—then we’ll recommend the right viewer and provide a quick estimate.</p>
    </section>
  </main>

  <footer class="cta-footer">
    <div class="wrap">
      <h3>Get Started in {city}, {state}</h3>
      <p>Ready for {SERVICE_NAME.lower()} in {city}? We serve {city}, {state} and nearby areas with reliable, detail-oriented service.</p>
      <a class="btn2" href="#quote">{SECONDARY_CTA_TEXT}</a>
    </div>
  </footer>

  <div class="mini">
    <div class="wrap">© {BRAND_NAME}. All rights reserved. • <a href="/">Home</a></div>
  </div>
</body>
</html>
"""

def home_page_html(city_rows: List[Tuple[str, str, str]]) -> str:
    items = "\n".join(
        f'<li><a href="/{slug}/">{city}, {state}</a></li>'
        for city, state, slug in city_rows
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{BRAND_NAME} | City Pages</title>
  <meta name="description" content="Find {SERVICE_NAME.lower()} cost estimates and service details across major US cities." />
  <style>
    :root {{
      --bg: #0b1220;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #475569;
      --line: #e2e8f0;
      --max: 920px;
      --radius: 14px;
      --accent: #f97316;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; color: var(--text); background: #fff; }}
    header {{
      background: radial-gradient(1200px 380px at 50% 0%, #193a67 0%, #0b1d34 55%, var(--bg) 100%);
      color: #fff;
      padding: 42px 0 28px;
    }}
    .wrap {{ max-width: var(--max); margin: 0 auto; padding: 0 20px; }}
    h1 {{ margin: 0 0 8px; font-size: 24px; }}
    p {{ margin: 0; color: rgba(255,255,255,0.82); font-size: 13px; line-height: 1.6; }}
    main {{ padding: 24px 0 34px; }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 18px;
    }}
    ul {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    @media (max-width: 820px) {{ ul {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 520px) {{ ul {{ grid-template-columns: 1fr; }} }}
    a {{
      display: block;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid var(--line);
      text-decoration: none;
      color: var(--text);
      font-weight: 600;
      font-size: 13px;
      background: #fff;
    }}
    a:hover {{ border-color: #cbd5e1; }}
    .mini {{ margin-top: 12px; color: var(--muted); font-size: 12px; }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>{BRAND_NAME}</h1>
      <p>Choose your city for a fast, scannable cost estimate and service overview.</p>
    </div>
  </header>

  <main class="wrap">
    <div class="card">
      <ul>
        {items}
      </ul>
      <div class="mini">Generated static pages. No JavaScript.</div>
    </div>
  </main>
</body>
</html>
"""

def main() -> None:
    city_rows: List[Tuple[str, str, str]] = []
    for city, state in CITIES:
        city_slug = slugify(city)
        city_rows.append((city, state, city_slug))

        out_path = os.path.join(OUTPUT_DIR, city_slug, "index.html")
        write_file(out_path, city_page_html(city, state, city_slug))

    write_file(os.path.join(OUTPUT_DIR, "index.html"), home_page_html(city_rows))

    print(f"✅ Generated {len(city_rows)} city pages + homepage into ./{OUTPUT_DIR}/")
    print("   Example paths:")
    for sample in ["los-angeles", "chicago", "new-york", "san-francisco"]:
        p = os.path.join(OUTPUT_DIR, sample, "index.html")
        if os.path.exists(p):
            print(f"   - /{sample}/  ->  {p}")

if __name__ == "__main__":
    main()
