import os
import json
import urllib.request
from datetime import datetime, timedelta

USERNAME = "SamarSharma26"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
STATIC = os.environ.get("STATIC", "0") == "1"

# Palette: Warm paper, deep ink, electric cobalt accent
BG = "#FAF9F6"
CARD_BG = "#FFFFFF"
INK = "#141413"
MUTED = "#6B6A65"
BORDER = "#E5E3DC"
ACCENT = "#1D4ED8"
ACCENT_SOFT = "#DBEAFE"
RED_TILE = "#DC2626"
AMBER_TILE = "#D97706"

os.makedirs("cards", exist_ok=True)
os.makedirs("data", exist_ok=True)


def github_graphql(query: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": USERNAME,
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_data() -> dict:
    if not TOKEN and os.path.exists("data/contributions.json"):
        with open("data/contributions.json") as f:
            return json.load(f)

    query = f"""
    query {{
      user(login: "{USERNAME}") {{
        repositories(first: 4, privacy: PUBLIC, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
          totalCount
          nodes {{
            name
            description
            url
            stargazerCount
            primaryLanguage {{ name color }}
          }}
        }}
        contributionsCollection {{
          contributionCalendar {{
            totalContributions
            weeks {{
              contributionDays {{
                date
                contributionCount
                contributionLevel
              }}
            }}
          }}
        }}
      }}
    }}
    """
    raw = github_graphql(query)["data"]["user"]
    with open("data/contributions.json", "w") as f:
        json.dump(raw, f, indent=2)
    return raw


def esc(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def compute_stats(weeks: list) -> dict:
    days = [d for w in weeks for d in w["contributionDays"]]
    monthly = {}
    active_days = 0
    busiest_day = ("—", 0)

    for d in days:
        c = d["contributionCount"]
        m = d["date"][:7]
        monthly[m] = monthly.get(m, 0) + c
        if c > 0:
            active_days += 1
        if c > busiest_day[1]:
            busiest_day = (d["date"], c)

    # Current & longest streak
    longest = cur = 0
    for d in days:
        if d["contributionCount"] > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0

    current_streak = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            current_streak += 1
        elif d["date"] != datetime.utcnow().strftime("%Y-%m-%d"):
            break

    last_12 = sorted(monthly.items())[-12:]
    return {
        "days": days,
        "weeks": weeks,
        "monthly": last_12,
        "active_days": active_days,
        "busiest_day": busiest_day,
        "longest_streak": longest,
        "current_streak": current_streak,
    }


def base_style(extra: str = "") -> str:
    anim_off = "" if not STATIC else "* { animation: none !important; opacity: 1 !important; transform: none !important; }"
    return f"""
    <style>
      .serif {{ font-family: Georgia, 'Times New Roman', serif; }}
      .sans {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }}
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
      @keyframes riseIn {{
        0% {{ opacity: 0; transform: translateY(14px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
      }}
      @keyframes popIn {{
        0% {{ opacity: 0; transform: scale(0.4); }}
        100% {{ opacity: 1; transform: scale(1); }}
      }}
      @keyframes growBar {{
        0% {{ transform: scaleY(0); }}
        100% {{ transform: scaleY(1); }}
      }}
      @keyframes pulseDot {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.45; transform: scale(1.35); }}
      }}
      @media (prefers-reduced-motion: reduce) {{
        * {{ animation: none !important; opacity: 1 !important; transform: none !important; }}
      }}
      {extra}
      {anim_off}
    </style>
    """


def render_hero():
    ascii_art = [
        "      .::://///::.      ",
        "    ://++++++++++//:    ",
        "   /++///:::::///+++/   ",
        "  /+/:  .::::.  :/+/  ",
        "  /+:  :++++++:  :+/  ",
        "  /+:  :+/  /+:  :+/  ",
        "  /+/:  '::::'  :/+/  ",
        "   /+++//:::://+++/   ",
        "    ://++++++++//:    ",
        "   .://++++++++//:.   ",
        "  ://++//:::://++//:  ",
        " ://++/        /++//: ",
    ]
    rows_svg = []
    for i, line in enumerate(ascii_art):
        delay = round(i * 0.04, 2)
        rows_svg.append(
            f'<text x="640" y="{54 + i * 16}" class="mono" font-size="13" fill="{INK}" '
            f'style="opacity:0;animation:riseIn 0.35s ease forwards {delay}s">{esc(line)}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="270" viewBox="0 0 880 270">
      <defs>
        <linearGradient id="shine" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="{INK}" />
          <stop offset="45%" stop-color="{INK}" />
          <stop offset="50%" stop-color="{ACCENT}" />
          <stop offset="55%" stop-color="{INK}" />
          <stop offset="100%" stop-color="{INK}" />
          <animateTransform attributeName="gradientTransform" type="translate" from="-1 0" to="1 0" dur="4s" repeatCount="indefinite" />
        </linearGradient>
      </defs>
      {base_style()}
      <rect x="1" y="1" width="878" height="268" rx="16" fill="{BG}" stroke="{BORDER}" stroke-width="1.5" />
      <circle cx="44" cy="44" r="5" fill="{ACCENT}" style="transform-box:fill-box;transform-origin:center;animation:pulseDot 2.2s infinite;" />
      <text x="58" y="48" class="mono" font-size="12" fill="{MUTED}">INDIA · GITHUB DEVELOPER PROGRAM · @SAMARSHARMA26</text>

      <text x="40" y="118" class="serif" font-size="56" font-weight="700" fill="{INK}"
            style="opacity:0;animation:riseIn 0.5s ease forwards 0.1s">Samar</text>
      <text x="40" y="176" class="serif" font-size="56" font-weight="700" fill="url(#shine)"
            style="opacity:0;animation:riseIn 0.5s ease forwards 0.22s">Sharma.</text>

      <text x="40" y="216" class="sans" font-size="16" fill="{INK}"
            style="opacity:0;animation:riseIn 0.5s ease forwards 0.34s">AI &amp; Data Science Student · Building AI Systems, Web Apps &amp; Creative Code</text>
      <text x="40" y="242" class="mono" font-size="12" fill="{MUTED}"
            style="opacity:0;animation:riseIn 0.5s ease forwards 0.44s">YouTube @TheSamarCode · X @samar2607 · LinkedIn in/samar-sharma2607</text>

      {''.join(rows_svg)}
    </svg>"""
    with open("cards/hero.svg", "w") as f:
        f.write(svg)


def render_heatmap(weeks: list, total: int):
    level_colors = {
        "NONE": "#EFECE6",
        "FIRST_QUARTILE": "#BFDBFE",
        "SECOND_QUARTILE": "#60A5FA",
        "THIRD_QUARTILE": "#2563EB",
        "FOURTH_QUARTILE": "#1E3A8A",
    }
    cells = []
    recent_weeks = weeks[-52:]
    for wi, w in enumerate(recent_weeks):
        x = 36 + wi * 15.6
        delay = round(0.4 + wi * 0.015, 3)
        for di, d in enumerate(w["contributionDays"]):
            y = 58 + di * 15.6
            color = level_colors.get(d["contributionLevel"], "#EFECE6")
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="12" height="12" rx="3" fill="{color}" '
                f'style="opacity:0;transform-box:fill-box;transform-origin:center;animation:popIn 0.25s ease forwards {delay}s" />'
            )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="190" viewBox="0 0 880 190">
      {base_style()}
      <rect x="1" y="1" width="878" height="188" rx="16" fill="{CARD_BG}" stroke="{BORDER}" stroke-width="1.5" />
      <text x="36" y="36" class="mono" font-size="12" font-weight="600" fill="{INK}">CONTRIBUTION GRAPH</text>
      <text x="844" y="36" text-anchor="end" class="mono" font-size="12" fill="{ACCENT}">{total} contributions in the last year</text>
      {''.join(cells)}
    </svg>"""
    with open("cards/heatmap.svg", "w") as f:
        f.write(svg)


def render_activity(stats: dict):
    monthly = stats["monthly"]
    max_val = max([v for _, v in monthly] + [1])
    bars = []
    for idx, (ym, val) in enumerate(monthly):
        x = 40 + idx * 46
        h = max(6, int((val / max_val) * 95))
        y = 165 - h
        is_best = val == max_val and val > 0
        fill = ACCENT if is_best else "#D6D3CB"
        delay = round(0.8 + idx * 0.04, 2)
        label = datetime.strptime(ym, "%Y-%m").strftime("%b")
        bars.append(
            f'<rect x="{x}" y="{y}" width="30" height="{h}" rx="5" fill="{fill}" '
            f'style="transform-box:fill-box;transform-origin:bottom;animation:growBar 0.45s ease forwards {delay}s" />'
        )
        if is_best:
            bars.append(
                f'<text x="{x + 15}" y="{y - 6}" text-anchor="middle" class="mono" font-size="11" font-weight="700" fill="{ACCENT}">{val}</text>'
            )
        bars.append(
            f'<text x="{x + 15}" y="184" text-anchor="middle" class="mono" font-size="11" fill="{MUTED}">{label}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="210" viewBox="0 0 880 210">
      {base_style()}
      <rect x="1" y="1" width="878" height="208" rx="16" fill="{CARD_BG}" stroke="{BORDER}" stroke-width="1.5" />
      <text x="40" y="36" class="mono" font-size="12" font-weight="600" fill="{INK}">MONTHLY CADENCE</text>
      {''.join(bars)}

      <line x1="610" y1="30" x2="610" y2="185" stroke="{BORDER}" stroke-width="1.5" />
      <text x="636" y="54" class="mono" font-size="11" fill="{MUTED}">LONGEST STREAK</text>
      <text x="636" y="82" class="serif" font-size="30" font-weight="700" fill="{INK}">{stats['longest_streak']} days</text>

      <text x="636" y="116" class="mono" font-size="11" fill="{MUTED}">ACTIVE DAYS</text>
      <text x="636" y="144" class="serif" font-size="30" font-weight="700" fill="{INK}">{stats['active_days']} days</text>

      <text x="636" y="176" class="mono" font-size="11" fill="{MUTED}">PEAK DAY: <tspan fill="{ACCENT}" font-weight="700">{stats['busiest_day'][1]} commits</tspan> ({stats['busiest_day'][0]})</text>
    </svg>"""
    with open("cards/activity.svg", "w") as f:
        f.write(svg)


def render_tile(filename: str, tag: str, title: str, metric: str, sub: str, color: str, delay: float):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="280" height="190" viewBox="0 0 280 190">
      {base_style()}
      <rect x="1" y="1" width="278" height="188" rx="16" fill="{color}"
            style="opacity:0;animation:riseIn 0.45s ease forwards {delay}s" />
      <text x="24" y="38" class="mono" font-size="12" font-weight="700" fill="#FFFFFF" opacity="0.85">{esc(tag)} ↗</text>
      <text x="24" y="114" class="serif" font-size="44" font-weight="700" fill="#FFFFFF">{esc(metric)}</text>
      <text x="24" y="146" class="sans" font-size="16" font-weight="600" fill="#FFFFFF">{esc(title)}</text>
      <text x="24" y="168" class="mono" font-size="11" fill="#FFFFFF" opacity="0.85">{esc(sub)}</text>
    </svg>"""
    with open(f"cards/{filename}", "w") as f:
        f.write(svg)


def render_repos(repos: list):
    cards = []
    for i, r in enumerate(repos[:4]):
        col = i % 2
        row = i // 2
        x = 36 + col * 412
        y = 58 + row * 92
        lang = (r.get("primaryLanguage") or {}).get("name", "Code")
        lcolor = (r.get("primaryLanguage") or {}).get("color", ACCENT)
        desc = (r.get("description") or "Public repository on GitHub")[:52]
        delay = round(1.3 + i * 0.1, 2)
        cards.append(f"""
        <g style="opacity:0;animation:riseIn 0.4s ease forwards {delay}s">
          <rect x="{x}" y="{y}" width="396" height="78" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="1.2" />
          <text x="{x + 16}" y="{y + 28}" class="mono" font-size="14" font-weight="700" fill="{INK}">{esc(r['name'])}</text>
          <text x="{x + 16}" y="{y + 50}" class="sans" font-size="12" fill="{MUTED}">{esc(desc)}</text>
          <circle cx="{x + 22}" cy="{y + 66}" r="4" fill="{lcolor}" />
          <text x="{x + 32}" y="{y + 70}" class="mono" font-size="11" fill="{MUTED}">{esc(lang)} · ★ {r.get('stargazerCount', 0)}</text>
        </g>
        """)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="256" viewBox="0 0 880 256">
      {base_style()}
      <rect x="1" y="1" width="878" height="254" rx="16" fill="{CARD_BG}" stroke="{BORDER}" stroke-width="1.5" />
      <text x="36" y="36" class="mono" font-size="12" font-weight="600" fill="{INK}">RECENT REPOSITORIES</text>
      {''.join(cards)}
    </svg>"""
    with open("cards/repos.svg", "w") as f:
        f.write(svg)


if __name__ == "__main__":
    data = fetch_data()
    cal = data["contributionsCollection"]["contributionCalendar"]
    stats = compute_stats(cal["weeks"])
    repo_count = data["repositories"]["totalCount"]
    repos = data["repositories"]["nodes"]

    render_hero()
    render_heatmap(stats["weeks"], cal["totalContributions"])
    render_activity(stats)
    render_tile("tile-build.svg", "BUILD", "Public Repos", f"0{repo_count}" if repo_count < 10 else str(repo_count), "github.com/SamarSharma26", ACCENT, 1.05)
    render_tile("tile-create.svg", "CREATE", "TheSamarCode", "YT", "Tutorials & Dev Videos", RED_TILE, 1.15)
    render_tile("tile-connect.svg", "CONNECT", "Let's Collaborate", "IN / X", "@samar2607 · LinkedIn", AMBER_TILE, 1.25)
    render_repos(repos)
    print("Rendered all SVG cards into cards/")
