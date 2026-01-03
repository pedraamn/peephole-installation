#!/usr/bin/env python3
"""
Static site generator (no JS) for a single-service, multi-city site.

Cloudflare Pages:
- Build command: (empty)
- Output directory: public

URL structure:
- /<city>-<state>/   e.g. /los-angeles-ca/
- /cost/
- /how-to/

SEO rules enforced:
- Exactly one H1 per page
- <title> == H1
- Title <= 70 characters
- Main + City pages use the exact same H2 set (Ahrefs-driven)
- Cost and How-To use distinct H2 sets (no reused headings across them)
- Pure CSS, barebones, fast
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import html
import re
import shutil


# -----------------------
# CONFIG
# -----------------------
@dataclass(frozen=True)
class SiteConfig:
    service_name: str = "Wasp Nest/Wasp Hive Removal & Wasp Control Services"
    brand_name: str = "Peephole Installation Company"
    cta_text: str = "Get Free Estimate"
    cta_href: str = "mailto:hello@example.com?subject=Free%20Quote%20Request"
    output_dir: Path = Path("public")
    image_filename: str = "picture.png"  # sits next to generate.py
    cost_low: int = 150
    cost_high: int = 450


CONFIG = SiteConfig()

CITIES: list[tuple[str, str]] = [
  ("New York", "NY"),
  ("Los Angeles", "CA"),
  ("Chicago", "IL"),
  ("Dallas", "TX"),
  ("Fort Worth", "TX"),
  ("Philadelphia", "PA"),
  ("Houston", "TX"),
  ("Atlanta", "GA"),
  ("Washington", "DC"),
  ("Hagerstown", "MD"),
  ("Boston", "MA"),
  ("Manchester", "NH"),
  ("San Francisco", "CA"),
  ("Oakland", "CA"),
  ("San Jose", "CA"),
  ("Tampa", "FL"),
  ("St. Petersburg", "FL"),
  ("Sarasota", "FL"),
  ("Phoenix", "AZ"),
  ("Prescott", "AZ"),
  ("Seattle", "WA"),
  ("Tacoma", "WA"),
  ("Detroit", "MI"),
  ("Orlando", "FL"),
  ("Daytona Beach", "FL"),
  ("Melbourne", "FL"),
  ("Minneapolis", "MN"),
  ("St. Paul", "MN"),
  ("Denver", "CO"),
  ("Miami", "FL"),
  ("Fort Lauderdale", "FL"),
  ("Cleveland", "OH"),
  ("Akron", "OH"),
  ("Canton", "OH"),
  ("Sacramento", "CA"),
  ("Stockton", "CA"),
  ("Modesto", "CA"),
  ("Charlotte", "NC"),
  ("Raleigh", "NC"),
  ("Durham", "NC"),
  ("Fayetteville", "NC"),
  ("Portland", "OR"),
  ("St. Louis", "MO"),
  ("Indianapolis", "IN"),
  ("Nashville", "TN"),
  ("Pittsburgh", "PA"),
  ("Salt Lake City", "UT"),
  ("Baltimore", "MD"),
  ("San Diego", "CA"),
  ("San Antonio", "TX"),
  ("Hartford", "CT"),
  ("New Haven", "CT"),
  ("Kansas City", "MO"),
  ("Austin", "TX"),
  ("Columbus", "OH"),
  ("Greenville", "SC"),
  ("Spartanburg", "SC"),
  ("Asheville", "NC"),
  ("Anderson", "SC"),
  ("Cincinnati", "OH"),
  ("Milwaukee", "WI"),
  ("West Palm Beach", "FL"),
  ("Fort Pierce", "FL"),
  ("Las Vegas", "NV"),
  ("Jacksonville", "FL"),
  ("Harrisburg", "PA"),
  ("Lancaster", "PA"),
  ("Lebanon", "PA"),
  ("York", "PA"),
  ("Grand Rapids", "MI"),
  ("Kalamazoo", "MI"),
  ("Battle Creek", "MI"),
  ("Norfolk", "VA"),
  ("Portsmouth", "VA"),
  ("Newport News", "VA"),
  ("Birmingham", "AL"),
  ("Anniston", "AL"),
  ("Tuscaloosa", "AL"),
  ("Greensboro", "NC"),
  ("High Point", "NC"),
  ("Winston-Salem", "NC"),
  ("Oklahoma City", "OK"),
  ("Albuquerque", "NM"),
  ("Santa Fe", "NM"),
  ("Louisville", "KY"),
  ("New Orleans", "LA"),
  ("Memphis", "TN"),
  ("Providence", "RI"),
  ("New Bedford", "MA"),
  ("Fort Myers", "FL"),
  ("Naples", "FL"),
  ("Buffalo", "NY"),
  ("Fresno", "CA"),
  ("Visalia", "CA"),
  ("Richmond", "VA"),
  ("Petersburg", "VA"),
  ("Mobile", "AL"),
  ("Pensacola", "FL"),
  ("Fort Walton Beach", "FL"),
  ("Little Rock", "AR"),
  ("Pine Bluff", "AR"),
  ("Wilkes-Barre", "PA"),
  ("Scranton", "PA"),
  ("Hazleton", "PA"),
  ("Knoxville", "TN"),
  ("Tulsa", "OK"),
  ("Albany", "NY"),
  ("Schenectady", "NY"),
  ("Troy", "NY"),
  ("Lexington", "KY"),
  ("Dayton", "OH"),
  ("Tucson", "AZ"),
  ("Sierra Vista", "AZ"),
  ("Spokane", "WA"),
  ("Des Moines", "IA"),
  ("Ames", "IA"),
  ("Green Bay", "WI"),
  ("Appleton", "WI"),
  ("Honolulu", "HI"),
  ("Roanoke", "VA"),
  ("Lynchburg", "VA"),
  ("Wichita", "KS"),
  ("Hutchinson", "KS"),
  ("Flint", "MI"),
  ("Saginaw", "MI"),
  ("Bay City", "MI"),
  ("Omaha", "NE"),
  ("Springfield", "MO"),
  ("Huntsville", "AL"),
  ("Decatur", "AL"),
  ("Florence", "AL"),
  ("Columbia", "SC"),
  ("Madison", "WI"),
  ("Portland", "ME"),
  ("Auburn", "ME"),
  ("Rochester", "NY"),
  ("Harlingen", "TX"),
  ("Weslaco", "TX"),
  ("Brownsville", "TX"),
  ("McAllen", "TX"),
  ("Toledo", "OH"),
  ("Charleston", "WV"),
  ("Huntington", "WV"),
  ("Waco", "TX"),
  ("Temple", "TX"),
  ("Bryan", "TX"),
  ("Savannah", "GA"),
  ("Charleston", "SC"),
  ("Chattanooga", "TN"),
  ("Colorado Springs", "CO"),
  ("Pueblo", "CO"),
  ("Syracuse", "NY"),
  ("El Paso", "TX"),
  ("Las Cruces", "NM"),
  ("Paducah", "KY"),
  ("Cape Girardeau", "MO"),
  ("Harrisburg", "IL"),
  ("Shreveport", "LA"),
  ("Texarkana", "TX"),
  ("Champaign", "IL"),
  ("Urbana", "IL"),
  ("Springfield", "IL"),
  ("Decatur", "IL"),
  ("Burlington", "VT"),
  ("Plattsburgh", "NY"),
  ("Cedar Rapids", "IA"),
  ("Waterloo", "IA"),
  ("Iowa City", "IA"),
  ("Dubuque", "IA"),
  ("Baton Rouge", "LA"),
  ("Fort Smith", "AR"),
  ("Fayetteville", "AR"),
  ("Springdale", "AR"),
  ("Rogers", "AR"),
  ("Myrtle Beach", "SC"),
  ("Florence", "SC"),
  ("Boise", "ID"),
  ("Jackson", "MS"),
  ("South Bend", "IN"),
  ("Elkhart", "IN"),
  ("Johnson City", "TN"),
  ("Kingsport", "TN"),
  ("Bristol", "VA"),
  ("Greenville", "NC"),
  ("New Bern", "NC"),
  ("Washington", "NC"),
  ("Reno", "NV"),
  ("Davenport", "IA"),
  ("Rock Island", "IL"),
  ("Moline", "IL"),
  ("Tallahassee", "FL"),
  ("Thomasville", "GA"),
  ("Tyler", "TX"),
  ("Longview", "TX"),
  ("Lufkin", "TX"),
  ("Nacogdoches", "TX"),
  ("Lincoln", "NE"),
  ("Hastings", "NE"),
  ("Kearney", "NE"),
  ("Augusta", "GA"),
  ("Aiken", "SC"),
  ("Evansville", "IN"),
  ("Fort Wayne", "IN"),
  ("Sioux Falls", "SD"),
  ("Mitchell", "SD"),
  ("Johnstown", "PA"),
  ("Altoona", "PA"),
  ("State College", "PA"),
  ("Fargo", "ND"),
  ("Valley City", "ND"),
  ("Yakima", "WA"),
  ("Pasco", "WA"),
  ("Richland", "WA"),
  ("Kennewick", "WA"),
  ("Springfield", "MA"),
  ("Holyoke", "MA"),
  ("Traverse City", "MI"),
  ("Cadillac", "MI"),
  ("Lansing", "MI"),
  ("Youngstown", "OH"),
  ("Macon", "GA"),
  ("Eugene", "OR"),
  ("Montgomery", "AL"),
  ("Selma", "AL"),
  ("Peoria", "IL"),
  ("Bloomington", "IL"),
  ("Santa Barbara", "CA"),
  ("Santa Maria", "CA"),
  ("San Luis Obispo", "CA"),
  ("Lafayette", "LA"),
  ("Bakersfield", "CA"),
  ("Wilmington", "NC"),
  ("Columbus", "GA"),
  ("Monterey", "CA"),
  ("Salinas", "CA"),
  ("La Crosse", "WI"),
  ("Eau Claire", "WI"),
  ("Corpus Christi", "TX"),
  ("Salisbury", "MD"),
  ("Amarillo", "TX"),
  ("Wausau", "WI"),
  ("Rhinelander", "WI"),
  ("Columbus", "MS"),
  ("Tupelo", "MS"),
  ("West Point", "MS"),
  ("Starkville", "MS"),
  ("Columbia", "MO"),
  ("Jefferson City", "MO"),
  ("Chico", "CA"),
  ("Redding", "CA"),
  ("Rockford", "IL"),
  ("Duluth", "MN"),
  ("Superior", "WI"),
  ("Medford", "OR"),
  ("Klamath Falls", "OR"),
  ("Lubbock", "TX"),
  ("Topeka", "KS"),
  ("Monroe", "LA"),
  ("El Dorado", "AR"),
  ("Beaumont", "TX"),
  ("Port Arthur", "TX"),
  ("Odessa", "TX"),
  ("Midland", "TX"),
  ("Palm Springs", "CA"),
  ("Anchorage", "AK"),
  ("Minot", "ND"),
  ("Bismarck", "ND"),
  ("Dickinson", "ND"),
  ("Williston", "ND"),
  ("Panama City", "FL"),
  ("Sioux City", "IA"),
  ("Wichita Falls", "TX"),
  ("Lawton", "OK"),
  ("Joplin", "MO"),
  ("Pittsburg", "KS"),
  ("Albany", "GA"),
  ("Rochester", "MN"),
  ("Mason City", "IA"),
  ("Austin", "MN"),
  ("Erie", "PA"),
  ("Idaho Falls", "ID"),
  ("Pocatello", "ID"),
  ("Jackson", "WY"),
  ("Bangor", "ME"),
  ("Gainesville", "FL"),
  ("Biloxi", "MS"),
  ("Gulfport", "MS"),
  ("Terre Haute", "IN"),
  ("Sherman", "TX"),
  ("Ada", "OK"),
  ("Missoula", "MT"),
  ("Binghamton", "NY"),
  ("Wheeling", "WV"),
  ("Steubenville", "OH"),
  ("Yuma", "AZ"),
  ("El Centro", "CA"),
  ("Billings", "MT"),
  ("Abilene", "TX"),
  ("Sweetwater", "TX"),
  ("Bluefield", "WV"),
  ("Beckley", "WV"),
  ("Oak Hill", "WV"),
  ("Hattiesburg", "MS"),
  ("Laurel", "MS"),
  ("Rapid City", "SD"),
  ("Dothan", "AL"),
  ("Utica", "NY"),
  ("Clarksburg", "WV"),
  ("Weston", "WV"),
  ("Harrisonburg", "VA"),
  ("Jackson", "TN"),
  ("Quincy", "IL"),
  ("Hannibal", "MO"),
  ("Keokuk", "IA"),
  ("Charlottesville", "VA"),
  ("Lake Charles", "LA"),
  ("Elmira", "NY"),
  ("Corning", "NY"),
  ("Watertown", "NY"),
  ("Bowling Green", "KY"),
  ("Marquette", "MI"),
  ("Jonesboro", "AR"),
  ("Alexandria", "LA"),
  ("Laredo", "TX"),
  ("Butte", "MT"),
  ("Bozeman", "MT"),
  ("Bend", "OR"),
  ("Grand Junction", "CO"),
  ("Montrose", "CO"),
  ("Twin Falls", "ID"),
  ("Lafayette", "IN"),
  ("Lima", "OH"),
  ("Great Falls", "MT"),
  ("Meridian", "MS"),
  ("Cheyenne", "WY"),
  ("Scottsbluff", "NE"),
  ("Parkersburg", "WV"),
  ("Greenwood", "MS"),
  ("Greenville", "MS"),
  ("Eureka", "CA"),
  ("San Angelo", "TX"),
  ("Casper", "WY"),
  ("Riverton", "WY"),
  ("Mankato", "MN"),
  ("Ottumwa", "IA"),
  ("Kirksville", "MO"),
  ("St. Joseph", "MO"),
  ("Fairbanks", "AK"),
  ("Zanesville", "OH"),
  ("Victoria", "TX"),
  ("Helena", "MT"),
  ("Presque Isle", "ME"),
  ("Juneau", "AK"),
  ("Alpena", "MI"),
  ("North Platte", "NE"),
  ("Glendive", "MT"),
]


BRAND_NAME = "Peephole Installation Company"

COST_TITLE = "Peephole Installation Cost"
HOWTO_TITLE = "How to Install a Peephole"

H1_TITLE = "Exterior Door Viewer/Eyehole/Peephole Installation Services"


# =========================
# MAIN PAGE (H2_SHARED)
# =========================

H2_SHARED = [
    "What Is a Peephole in a Door?",
    "What Is Peephole Installation?",
    "How Do Peepholes Work?",
    "Best Height for a Door Peephole",
    "Types of Door Peepholes and Viewers",
    "Professional Peephole Installation vs DIY",
    "When to Hire a Peephole Installation Professional",
]

P_SHARED = [
    "A peephole, also known as a door viewer or door eye, is a small optical device installed in an exterior door that allows someone inside to see who is outside before opening the door. Peepholes are commonly used on entry doors to improve personal safety and visibility.",

    "Peephole installation is the process of drilling a precise hole through a door and securely installing a door viewer. Proper installation ensures a clear viewing angle, correct placement, and a clean finish without damaging the door.",

    "Peepholes work using a wide-angle lens that allows a person inside to see a broad area outside the door. This design makes it possible to identify visitors, deliveries, or unexpected guests without opening the door.",

    "The standard peephole height is typically between 58 and 62 inches from the floor. This range provides a comfortable viewing angle for most adults. In some homes, alternative heights or wide-angle viewers are used to accommodate children, wheelchair users, or multiple occupants.",

    "There are several types of door peepholes available, including standard optical peepholes, wide-angle viewers, privacy-enhanced models, and digital door viewers. The best option depends on door thickness, desired viewing angle, and security needs.",

    "DIY peephole installation may seem simple, but improper drilling or incorrect placement can permanently damage the door or reduce visibility. Professional installation ensures the peephole is centered correctly, sealed properly, and aligned for clear viewing.",

    "Hiring a professional is recommended when installing a peephole in a metal or reinforced door, when precise placement is important, or when avoiding damage to the door is a priority."
]


# =========================
# HOW-TO PAGE (H2_HOWTO)
# =========================

H2_HOWTO = [
    "Can You Install a Peephole Yourself?",
    "How to Install a Peephole in a Door",
    "How to Add a Peephole to a Front Door",
    "Installing a Peephole in a Metal Door",
    "Tools Needed for Peephole Installation",
    "Common Peephole Installation Mistakes",
    "When DIY Peephole Installation Is Not Recommended",
]

P_HOWTO = [
    "Some homeowners can install a basic peephole themselves using the correct tools and careful measurements. However, drilling mistakes can damage the door or result in poor visibility. For many people, professional {peephole installation services} provide a safer and more precise solution.",

    "Installing a peephole involves measuring the correct height, drilling a clean hole through the door, inserting the interior and exterior viewer components, and tightening them securely. Precision is essential to ensure proper alignment and functionality.",

    "Adding a peephole to a front door follows the same general process as standard installation, but extra care is needed to avoid damaging decorative panels, finishes, or internal door components.",

    "Installing a peephole in a metal door requires slow, controlled drilling and the correct drill bit. Incorrect techniques can damage the door’s finish or compromise its internal structure.",

    "Common tools for peephole installation include a drill, properly sized drill bit or hole saw, measuring tape, pencil, and screwdriver. Using the wrong tools increases the risk of door damage.",

    "Common DIY mistakes include drilling at the wrong height, using an incorrect drill bit size, overtightening the viewer, or misaligning the lens. These issues often lead to poor visibility or require professional correction.",

    "DIY installation is not recommended for metal doors, fire-rated doors, or rental properties with restrictions. In these cases, contacting a provider that offers {peephole installation services} is the safest option."
]


# =========================
# COST PAGE (H2_COST)
# =========================

H2_COST = [
    "How Much Does Peephole Installation Cost?",
    "What Affects the Cost of Peephole Installation?",
    "Peephole Installation Cost vs DIY",
    "Cost to Install a Peephole in a Metal Door",
    "Are Peepholes Allowed in Rental Doors?",
    "When Professional Peephole Installation Is Worth the Cost",
]

P_COST = [
    "Professional peephole installation typically costs between $75 and $200, depending on the door type and the viewer selected. Many homeowners compare DIY options against professional {peephole installation services} before making a decision.",

    "Several factors affect the cost of peephole installation, including door material, door thickness, type of viewer, labor time, and whether the door is metal or reinforced.",

    "DIY installation may appear cheaper, but mistakes can lead to damaged doors, misaligned viewers, or the need for replacement hardware. Professional installation reduces the risk of costly errors.",

    "Installing a peephole in a metal door often costs more due to the need for specialized tools and careful drilling techniques.",

    "Rental policies vary, but many landlords allow peepholes as a security feature if installed properly. In some cases, professional installation is required to comply with lease or building rules.",

    "Professional installation is worth the cost when precision matters, the door material is difficult to work with, or long-term durability is important. In these cases, professional {peephole installation services} provide reliable results and peace of mind."
]

"""
ALSO_MENTIONED = [
    "pest control",
    "spray",
    "spray bottle",
    "dish soap",
    "wasp stings",
    "price",
    "removal",
    "nest",
    "wasp",
]
"""


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


def city_h1(service: str, city: str, state: str) -> str:
    return clamp_title(f"{service} in {city}, {state}", 70)


def write_text(out_path: Path, content: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")


def reset_output_dir(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)


def copy_site_image(*, src_dir: Path, out_dir: Path, filename: str) -> None:
    src = src_dir / filename
    if not src.exists():
        raise FileNotFoundError(f"Missing image next to generate.py: {src}")
    shutil.copyfile(src, out_dir / filename)


# -----------------------
# THEME (pure CSS, minimal, fast)
# Home-services vibe: warmer neutrals + trustworthy green CTA.
# -----------------------
CSS = """
:root{
  --bg:#fafaf9;
  --surface:#ffffff;
  --ink:#111827;
  --muted:#4b5563;
  --line:#e7e5e4;
  --soft:#f5f5f4;

  --cta:#16a34a;
  --cta2:#15803d;

  --max:980px;
  --radius:16px;
  --shadow:0 10px 30px rgba(17,24,39,0.06);
  --shadow2:0 10px 24px rgba(17,24,39,0.08);
}
*{box-sizing:border-box}
html{color-scheme:light}
body{
  margin:0;
  font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;
  color:var(--ink);
  background:var(--bg);
  line-height:1.6;
}
a{color:inherit}
a:focus{outline:2px solid var(--cta); outline-offset:2px}

.topbar{
  position:sticky;
  top:0;
  z-index:50;
  background:rgba(250,250,249,0.92);
  backdrop-filter:saturate(140%) blur(10px);
  border-bottom:1px solid var(--line);
}
.topbar-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:12px 18px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
}
.brand{
  font-weight:900;
  letter-spacing:-0.02em;
  text-decoration:none;
}
.nav{
  display:flex;
  align-items:center;
  gap:12px;
  flex-wrap:wrap;
  justify-content:flex-end;
}
.nav a{
  text-decoration:none;
  font-size:13px;
  color:var(--muted);
  padding:7px 10px;
  border-radius:12px;
  border:1px solid transparent;
}
.nav a:hover{
  background:var(--soft);
  border-color:var(--line);
}
.nav a[aria-current="page"]{
  color:var(--ink);
  background:var(--soft);
  border:1px solid var(--line);
}

.btn{
  display:inline-block;
  padding:9px 12px;
  background:var(--cta);
  color:#fff;
  border-radius:12px;
  text-decoration:none;
  font-weight:900;
  font-size:13px;
  border:1px solid rgba(0,0,0,0.04);
  box-shadow:0 8px 18px rgba(22,163,74,0.18);
}
.btn:hover{background:var(--cta2)}
.btn:focus{outline:2px solid var(--cta2); outline-offset:2px}

/* IMPORTANT: nav links apply grey text; ensure CTA stays white in the toolbar */
.nav a.btn{
  color:#fff;
  background:var(--cta);
  border-color:rgba(0,0,0,0.04);
}
.nav a.btn:hover{background:var(--cta2)}
.nav a.btn:focus{outline:2px solid var(--cta2); outline-offset:2px}

header{
  border-bottom:1px solid var(--line);
  background:
    radial-gradient(1200px 380px at 10% -20%, rgba(22,163,74,0.08), transparent 55%),
    radial-gradient(900px 320px at 95% -25%, rgba(17,24,39,0.06), transparent 50%),
    #fbfbfa;
}
.hero{
  max-width:var(--max);
  margin:0 auto;
  padding:34px 18px 24px;
  display:grid;
  gap:10px;
  text-align:left;
}
.hero h1{
  margin:0;
  font-size:30px;
  letter-spacing:-0.03em;
  line-height:1.18;
}
.sub{margin:0; color:var(--muted); max-width:78ch; font-size:14px}

main{
  max-width:var(--max);
  margin:0 auto;
  padding:22px 18px 46px;
}
.card{
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:var(--radius);
  padding:18px;
  box-shadow:var(--shadow);
}
.img{
  margin-top:14px;
  border-radius:14px;
  overflow:hidden;
  border:1px solid var(--line);
  background:var(--soft);
  box-shadow:var(--shadow2);
}
.img img{display:block; width:100%; height:auto}

h2{
  margin:18px 0 8px;
  font-size:16px;
  letter-spacing:-0.01em;
}
p{margin:0 0 10px}
.muted{color:var(--muted); font-size:13px}
hr{border:0; border-top:1px solid var(--line); margin:18px 0}

.city-grid{
  list-style:none;
  padding:0;
  margin:10px 0 0;
  display:grid;
  gap:10px;
  grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
}
.city-grid a{
  display:block;
  text-decoration:none;
  color:var(--ink);
  background:#fff;
  border:1px solid var(--line);
  border-radius:14px;
  padding:12px 12px;
  font-weight:800;
  font-size:14px;
  box-shadow:0 10px 24px rgba(17,24,39,0.05);
}
.city-grid a:hover{
  transform:translateY(-1px);
  box-shadow:0 14px 28px rgba(17,24,39,0.08);
}

.callout{
  margin:16px 0 12px;
  padding:14px 14px;
  border-radius:14px;
  border:1px solid rgba(22,163,74,0.22);
  background:linear-gradient(180deg, rgba(22,163,74,0.08), rgba(22,163,74,0.03));
}
.callout-title{
  display:flex;
  align-items:center;
  gap:10px;
  font-weight:900;
  letter-spacing:-0.01em;
  margin:0 0 6px;
}
.badge{
  display:inline-block;
  padding:3px 10px;
  border-radius:999px;
  background:rgba(22,163,74,0.14);
  border:1px solid rgba(22,163,74,0.22);
  color:var(--ink);
  font-size:12px;
  font-weight:900;
}
.callout p{margin:0; color:var(--muted); font-size:13px}

footer{
  border-top:1px solid var(--line);
  background:#fbfbfa;
}
.footer-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:28px 18px;
  display:grid;
  gap:10px;
  text-align:left;
}
.footer-inner h2{margin:0; font-size:18px}
.footer-links{display:flex; gap:12px; flex-wrap:wrap}
.footer-links a{color:var(--muted); text-decoration:none; font-size:13px; padding:6px 0}
.small{color:var(--muted); font-size:12px; margin-top:8px}
""".strip()


# -----------------------
# HTML BUILDING BLOCKS
# -----------------------
def nav_html(current: str) -> str:
    def item(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if current == key else ""
        return f'<a href="{esc(href)}"{cur}>{esc(label)}</a>'

    return (
        '<nav class="nav" aria-label="Primary navigation">'
        + item("/", "Home", "home")
        + item("/cost/", "Cost", "cost")
        + item("/how-to/", "How-To", "howto")
        + f'<a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>'
        + "</nav>"
    )


def base_html(*, title: str, canonical_path: str, description: str, current_nav: str, body: str) -> str:
    # title == h1 is enforced by callers; keep this thin.
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
  <div class="topbar">
    <div class="topbar-inner">
      <a class="brand" href="/">{esc(BRAND_NAME)}</a>
      {nav_html(current_nav)}
    </div>
  </div>
{body}
</body>
</html>
"""


def header_block(*, h1: str, sub: str) -> str:
    return f"""
<header>
  <div class="hero">
    <h1>{esc(h1)}</h1>
  </div>
</header>
""".rstrip()


def footer_block() -> str:
    return f"""
<footer>
  <div class="footer-inner">
    <h2>Next steps</h2>
    <p class="sub">Ready to move forward? Request a free quote.</p>
    <div>
      <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    </div>
    <div class="footer-links">
      <a href="/">Home</a>
      <a href="/cost/">Cost</a>
      <a href="/how-to/">How-To</a>
    </div>
    <div class="small">© {esc(BRAND_NAME)}. All rights reserved.</div>
  </div>
</footer>
""".rstrip()


def page_shell(*, h1: str, sub: str, inner_html: str) -> str:
    # Single image used everywhere. Since we copy picture.png into /public/,
    # it can be referenced as "/picture.png" from any route.
    img_src = f"/{CONFIG.image_filename}"
    return (
        header_block(h1=h1, sub=sub)
        + f"""
<main>
  <section class="card">
    <div class="img">
      <img src="{esc(img_src)}" alt="Service image" loading="lazy" />
    </div>
    {inner_html}
  </section>
</main>
"""
        + footer_block()
    ).rstrip()


# -----------------------
# CONTENT SECTIONS
# -----------------------
def shared_sections_html(*, local_line: str | None = None) -> str:
    local = f' <span class="muted">{esc(local_line)}</span>' if local_line else ""
    return f"""
<h2>{esc(H2_SHARED[0])}</h2>
<p>{esc(P_SHARED[0])}</</p>

<h2>{esc(H2_SHARED[1])}</h2>
<p>{esc(P_SHARED[1])}</</p>

<h2>{esc(H2_SHARED[2])}</h2>
<p>{esc(P_SHARED[2])}</</p>

<h2>{esc(H2_SHARED[3])}</h2>
<p>{esc(P_SHARED[3])}</</p>

<h2>{esc(H2_SHARED[4])}</h2>
<p>{esc(P_SHARED[4])}</</p>

<h2>{esc(H2_SHARED[5])}</h2>
<p>{esc(P_SHARED[5])}</</p>
""".rstrip()


def cost_sections_html() -> str:
    return f"""
<h2>{esc(H2_COST[0])}</h2>
<p>{esc(P_COST[0])}</p>

<h2>{esc(H2_COST[1])}</h2>
<p>{esc(P_COST[1])}</p>

<h2>{esc(H2_COST[2])}</h2>
<p>{esc(P_COST[2])}</p>

<h2>{esc(H2_COST[3])}</h2>
<p>{esc(P_COST[3])}</p>

<h2>{esc(H2_COST[4])}</h2>
<p>{esc(P_COST[4])}</p>

<h2>{esc(H2_COST[5])}</h2>
<p>{esc(P_COST[5])}</p>

<hr />

<p class="muted">
  Typical installed range (single nest, many homes): ${CONFIG.cost_low}–${CONFIG.cost_high}. Final pricing depends on access, nest location, and time on site.
</p>
""".rstrip()


def howto_sections_html() -> str:
    return f"""
<h2>{esc(H2_HOWTO[0])}</h2>
<p>{esc(P_HOWTO[0])}</p>

<h2>{esc(H2_HOWTO[1])}</h2>
<p>{esc(P_HOWTO[1])}</p>

<h2>{esc(H2_HOWTO[2])}</h2>
<p>{esc(P_HOWTO[2])}</p>

<h2>{esc(H2_HOWTO[3])}</h2>
<p>{esc(P_HOWTO[3])}</p>

<h2>{esc(H2_HOWTO[4])}</h2>
<p>{esc(P_HOWTO[4])}</p>

<h2>{esc(H2_HOWTO[5])}</h2>
<p>{esc(P_HOWTO[5])}</p>
""".rstrip()


def city_cost_callout_html(city: str, state: str) -> str:
    # Subtle, high-impact conversion element for city pages.
    return f"""
<div class="callout" role="note" aria-label="Typical cost range">
  <div class="callout-title">
    <span class="badge">Typical range</span>
    <span>${CONFIG.cost_low}–${CONFIG.cost_high} for one nest</span>
  </div>
  <p>
    In {esc(city)}, {esc(state)}, most pricing comes down to access and where the nest is located.
    If you want a fast, no-pressure estimate, use the “{esc(CONFIG.cta_text)}” button above.
  </p>
</div>
""".rstrip()


# -----------------------
# PAGE FACTORY
# -----------------------
def make_page(*, h1: str, canonical: str, description: str, nav_key: str, sub: str, inner: str) -> str:
    h1 = clamp_title(h1, 70)
    title = h1  # enforce title == h1
    return base_html(
        title=title,
        canonical_path=canonical,
        description=clamp_title(description, 155),
        current_nav=nav_key,
        body=page_shell(h1=h1, sub=sub, inner_html=inner),
    )


def homepage_html() -> str:
    h1 = H1_TITLE
    city_links = "\n".join(
        f'<li><a href="{esc("/" + city_state_slug(city, state) + "/")}">{esc(city)}, {esc(state)}</a></li>'
        for city, state in CITIES
    )
    inner = (
        shared_sections_html()
        + """
<hr />
<h2>Choose your city</h2>
<p class="muted">Select a city page for the same guide with a light local line.</p>
<ul class="city-grid">
"""
        + city_links
        + """
</ul>
<hr />
<p class="muted">
  Also available: <a href="/cost/">Wasp Nest Removal Cost</a> and <a href="/how-to/">How to Get Rid of Wasp Nest</a>.
</p>
"""
    )

    return make_page(
        h1=h1,
        canonical="/",
        description="Straight answers on wasp nest removal and wasp control.",
        nav_key="home",
        sub="How removal works, what prevents repeat activity, and when to call help.",
        inner=inner,
    )


def city_page_html(city: str, state: str) -> str:
    inner = (
        shared_sections_html(local_line=f"Serving {city}, {state}.")
        + city_cost_callout_html(city, state)
        + f"""
<hr />
<h2>Wasp Nest Removal Cost</h2>
<p class="muted">
  Typical installed range for one nest often falls around ${CONFIG.cost_low}–${CONFIG.cost_high}. Access and nest location drive most pricing.
  See the <a href="/cost/">cost page</a> for details.
</p>
"""
    )

    return make_page(
        h1=city_h1(H1_TITLE, city, state),
        canonical=f"/{city_state_slug(city, state)}/",
        description=f"Wasp nest removal and wasp control guide with local context for {city}, {state}.",
        nav_key="home",
        sub="Same core guide, plus a quick local note and a typical cost range.",
        inner=inner,
    )


def cost_page_html() -> str:
    return make_page(
        h1=COST_TITLE,
        canonical="/cost/",
        description="Typical wasp nest removal cost ranges and what changes pricing.",
        nav_key="cost",
        sub="Simple ranges and the factors that usually move the price.",
        inner=cost_sections_html(),
    )


def howto_page_html() -> str:
    return make_page(
        h1=HOWTO_TITLE,
        canonical="/how-to/",
        description="Clear steps for dealing with a wasp nest without making it worse.",
        nav_key="howto",
        sub="A practical guide that prioritizes safety and reduces repeat activity.",
        inner=howto_sections_html(),
    )


# -----------------------
# ROBOTS + SITEMAP
# -----------------------
def robots_txt() -> str:
    return "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"


def sitemap_xml(urls: list[str]) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>\n"
    )


# -----------------------
# MAIN
# -----------------------
def main() -> None:
    script_dir = Path(__file__).resolve().parent
    out = CONFIG.output_dir

    reset_output_dir(out)

    # Copy the single shared image into /public/ so all pages can reference "/picture.png".
    copy_site_image(src_dir=script_dir, out_dir=out, filename=CONFIG.image_filename)

    # Core pages
    write_text(out / "index.html", homepage_html())
    write_text(out / "cost" / "index.html", cost_page_html())
    write_text(out / "how-to" / "index.html", howto_page_html())

    # City pages
    for city, state in CITIES:
        write_text(out / city_state_slug(city, state) / "index.html", city_page_html(city, state))

    # robots + sitemap
    urls = ["/", "/cost/", "/how-to/"] + [f"/{city_state_slug(c, s)}/" for c, s in CITIES]
    write_text(out / "robots.txt", robots_txt())
    write_text(out / "sitemap.xml", sitemap_xml(urls))

    print(f"✅ Generated {len(urls)} pages into: {out.resolve()}")


if __name__ == "__main__":
    main()
