import streamlit as st
import swisseph as swe
import datetime, pytz, math
import pandas as pd
from collections import defaultdict
import hashlib
import time


# ================= LOGIN =================
def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

USERS = st.secrets["users"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in USERS and hash_pwd(p) == USERS[u]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# ================= CONFIG =================
st.set_page_config(
    page_title="🪐 वेदिक ग्रह घड़ी — Drik Panchang",
    layout="wide",
    page_icon="🪐"
)

LAT, LON = 19.07598, 72.87766  # Mumbai
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ================= SESSION DEFAULTS =================
if "sel_date" not in st.session_state:
    st.session_state.sel_date = datetime.date.today()

if "sel_time" not in st.session_state:
    st.session_state.sel_time = datetime.datetime.now(
        pytz.timezone("Asia/Kolkata")
    ).time()


# ================= DATA =================
SIGNS = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या",
         "तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"]

NAKSHATRAS = [
("अश्विनी","केतु"),("भरणी","शुक्र"),("कृत्तिका","सूर्य"),
("रोहिणी","चन्द्र"),("मृगशिरा","मंगल"),("आर्द्रा","राहु"),
("पुनर्वसु","बृहस्पति"),("पुष्य","शनि"),("आश्लेषा","बुध"),
("मघा","केतु"),("पूर्व फाल्गुनी","शुक्र"),("उत्तर फाल्गुनी","सूर्य"),
("हस्त","चन्द्र"),("चित्रा","मंगल"),("स्वाति","राहु"),
("विशाखा","बृहस्पति"),("अनुराधा","शनि"),("ज्येष्ठा","बुध"),
("मूला","केतु"),("पूर्वाषाढा","शुक्र"),("उत्तराषाढा","सूर्य"),
("श्रवण","चन्द्र"),("धनिष्ठा","मंगल"),("शतभिषा","राहु"),
("पूर्वभाद्रपदा","बृहस्पति"),("उत्तरभाद्रपदा","शनि"),("रेवती","बुध")
]

PLANETS = [
("सूर्य", swe.SUN, "सू."),
("चन्द्र", swe.MOON,"च."),
("मंगल", swe.MARS,"मं."),
("बुध", swe.MERCURY,"बु."),
("बृहस्पति", swe.JUPITER,"बृह"),
("शुक्र", swe.VENUS,"शु"),
("शनि", swe.SATURN,"शनि"),
("राहु", swe.MEAN_NODE,"रा.")
]

# ================= FUNCTIONS =================
def nakshatra_pada(lon):
    nak_size = 13 + 1/3
    pada_size = nak_size / 4
    idx = int(lon // nak_size) % 27
    pada = int((lon % nak_size) // pada_size) + 1
    return NAKSHATRAS[idx][0], NAKSHATRAS[idx][1], pada

def get_positions(dt_utc):
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60)

    pos, retro = {}, {}
    ay = swe.get_ayanamsa_ut(jd)

    for name, code, sym in PLANETS:
        r, _ = swe.calc_ut(jd, code)
        lon = (r[0] - ay) % 360
        pos[name] = lon
        retro[name] = r[3] < 0

    pos["केतु"] = (pos["राहु"] + 180) % 360
    retro["केतु"] = retro["राहु"]

    return pos, retro, jd

def generate_mini_clock():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.datetime.now(ist)
    now_utc = now_ist.astimezone(pytz.utc)

    pos, retro, _ = get_positions(now_utc)

    cx, cy = 150, 150
    BASE_R = 85

    svg = f"""
    <svg width="300" height="300" viewBox="0 0 300 300"
         style="margin:auto;display:block">

    <circle cx="{cx}" cy="{cy}" r="140"
            fill="#050b18"
            stroke="#3fa9f5"
            stroke-width="4"/>

    <circle cx="{cx}" cy="{cy}" r="110"
            fill="none"
            stroke="#88c9ff"
            stroke-width="2"/>
    """

    # Divider lines
    for i in range(12):
        ang = math.radians(90 - i * 30)
        x = cx + 110 * math.cos(ang)
        y = cy - 110 * math.sin(ang)
        svg += f"<line x1='{cx}' y1='{cy}' x2='{x}' y2='{y}' stroke='#ffd700'/>"

    # Planets (simple — no stacking needed in mini)
    for name, code, sym in PLANETS:
        lon = pos[name]
        ang = math.radians(90 - lon)
        px = cx + BASE_R * math.cos(ang)
        py = cy - BASE_R * math.sin(ang)

        color = "#ff4d4d" if retro.get(name, False) else "#79e887"

        svg += f"""
        <circle cx="{px}" cy="{py}" r="6" fill="{color}"/>
        <text x="{px}" y="{py+2}"
              font-size="7"
              text-anchor="middle"
              fill="black">{sym}</text>
        """

    svg += "</svg>"
    return svg, now_ist


def generate_svg(pos, retro):
    from collections import defaultdict

    cx, cy = 350, 350

    # Radii
    OUTER_R = 330
    INNER_R = 270
    LINE_R  = 260
    TEXT_R  = 210
    BASE_PLANET_R = 200
    STACK_GAP = 18

    svg = f"""
    <svg width="700" height="700" viewBox="0 0 700 700"
         style="margin:auto;display:block">

    <defs>
        <radialGradient id="glow">
            <stop offset="70%" stop-color="#0a1e3a"/>
            <stop offset="100%" stop-color="#3fa9f5"/>
        </radialGradient>
    </defs>

    <circle cx="{cx}" cy="{cy}" r="{OUTER_R}" fill="url(#glow)"/>
    <circle cx="{cx}" cy="{cy}" r="{INNER_R}"
            fill="#050b18"
            stroke="#88c9ff"
            stroke-width="3"/>
    """

    # =================================================
    # 🔶 RASHI DIVIDER LINES
    # =================================================
    for i in range(12):
        ang = math.radians(90 - i * 30)
        x = cx + LINE_R * math.cos(ang)
        y = cy - LINE_R * math.sin(ang)

        svg += f"""
        <line x1="{cx}" y1="{cy}"
              x2="{x}" y2="{y}"
              stroke="#ffd700"
              stroke-width="2"/>
        """

    # =================================================
    # 🔷 RASHI NAMES (CENTERED)
    # =================================================
    for i in range(12):
        ang = math.radians(90 - (i * 30 + 15))
        x = cx + TEXT_R * math.cos(ang)
        y = cy - TEXT_R * math.sin(ang)

        svg += f"""
        <text x="{x}" y="{y}"
              fill="#00e6ff"
              font-size="22"
              font-weight="bold"
              text-anchor="middle"
              dominant-baseline="middle">
            {SIGNS[i]}
        </text>
        """

    # =================================================
    # 🪐 PLANETS (INCLUDING KETU) — NO OVERLAP
    # =================================================

    groups = defaultdict(list)

    # --- Main planets ---
    for name, code, sym in PLANETS:
        rashi = int(pos[name] // 30)
        groups[rashi].append((name, sym))

    # --- ADD KETU ---
    groups[int(pos["केतु"] // 30)].append(("केतु", "के."))

    # --- Draw planets ---
    for rashi, plist in groups.items():

        ang = math.radians(90 - (rashi * 30 + 15))

        for i, (name, sym) in enumerate(plist):
            r = BASE_PLANET_R - i * STACK_GAP

            px = cx + r * math.cos(ang)
            py = cy - r * math.sin(ang)

            # 🔴 Retrograde = Red | 🟢 Direct = Green
            color = "#ff4d4d" if retro.get(name, False) else "#79e887"

            svg += f"""
            <circle cx="{px}" cy="{py}"
                    r="11"
                    fill="{color}"
                    stroke="#0b3d1f"
                    stroke-width="1"/>

            <text x="{px}" y="{py}"
                  font-size="11"
                  font-weight="bold"
                  fill="black"
                  text-anchor="middle"
                  dominant-baseline="middle">
                {sym}
            </text>
            """

    svg += "</svg>"
    return svg






# ================= UI =================
st.title("🪐 वेदिक ग्रह घड़ी — Drik Panchang")

c1, c2, c3 = st.columns(3)
today = datetime.date.today()
date = c1.date_input(
    "तारीख़",
    value=st.session_state.sel_date,
    min_value=today - datetime.timedelta(days=365*500),     # ✅ NO PAST LIMIT
    max_value=today + datetime.timedelta(days=365*500)     # ✅ NO FUTURE LIMIT
)

sel_time = c2.time_input("समय", value=st.session_state.sel_time)


if c3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    st.session_state.sel_date = now.date()
    st.session_state.sel_time = now.time()
    st.rerun()

ist = pytz.timezone("Asia/Kolkata")
dt_ist = ist.localize(datetime.datetime.combine(date, sel_time))
dt_utc = dt_ist.astimezone(pytz.utc)   # ✅ REQUIRED

 


pos, retro, jd = get_positions(dt_utc)

# ===== CORRECT DRIK PANCHANG LAGNA =====
ascmc, _ = swe.houses_ex(jd, LAT, LON, b'P', FLAGS)
lagna_deg = ascmc[0] % 360
lagna_sign = SIGNS[int(lagna_deg // 30)]

# ================= LAYOUT =================
left, right = st.columns([2, 1])

with left:
    st.components.v1.html(generate_svg(pos, retro), height=720)


with right:
    st.subheader("🌙 ज्योतिष सार")

    moon_nak, moon_lord, moon_pada = nakshatra_pada(pos["चन्द्र"])

    summary = [
        ["चन्द्र नक्षत्र", moon_nak],
        ["नक्षत्र पद", moon_pada],
        ["नक्षत्र स्वामी", moon_lord],
        ["लग्न", lagna_sign],
        ["लग्न अंश", f"{lagna_deg:.2f}°"],
        ["समय (IST)", dt_ist.strftime("%d-%b-%Y %H:%M")]
    ]
    st.table(pd.DataFrame(summary, columns=["तत्व", "मान"]))

    st.subheader("🪐 ग्रह स्थिति")
    rows = []

# --- Main planets ---
    for p, code, sym in PLANETS:
        nak, lord, pada = nakshatra_pada(pos[p])
        rows.append([
            p,
            f"{pos[p]:.2f}°",
            SIGNS[int(pos[p]//30)],
            f"{nak} (पद {pada})",
            "🔁 वक्री" if retro[p] else "➡️ मार्गी"
        ])

    # --- ADD KETU (Shadow Planet) ---
    nak, lord, pada = nakshatra_pada(pos["केतु"])
    rows.append([
            "केतु",
        f"{pos['केतु']:.2f}°",
        SIGNS[int(pos["केतु"]//30)],
        f"{nak} (पद {pada})",
        "🔁 वक्री" if retro["केतु"] else "➡️ मार्गी"
        ])


    st.table(pd.DataFrame(
        rows,
        columns=["ग्रह","डिग्री","राशि","नक्षत्र","स्थिति"]
    ))

with st.sidebar:
    st.markdown("### ⏱️ Live Planet Clock")
    live_clock_on = st.toggle("Enable Live Clock", value=False)
  
    
st.markdown("""
<style>
#mini-clock {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 260px;
    height: 260px;
    background: rgba(5, 11, 24, 0.95);
    border-radius: 50%;
    border: 3px solid #3fa9f5;
    box-shadow: 0 0 25px rgba(63,169,245,0.6);
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)




# ================= LIVE CLOCK ENGINE =================
if live_clock_on:

if live_clock_on:
    st.autorefresh(interval=1000, key="live_clock")

    svg, now_ist = generate_mini_clock()

    st.components.v1.html(
        f"""
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 260px;
            height: 260px;
            background: rgba(5, 11, 24, 0.95);
            border-radius: 50%;
            border: 3px solid #3fa9f5;
            box-shadow: 0 0 25px rgba(63,169,245,0.6);
            z-index: 9999;
        ">
            {svg}
        </div>
        """,
        height=300
    )

    st.caption("Live IST: " + now_ist.strftime("%H:%M:%S"))








st.success("IST समय: " + dt_ist.strftime("%d-%b-%Y %H:%M:%S"))

st.markdown("""
---
### *Gaurav Singh Yadav*  
**Quant Trader | Energy & Commodity Intelligence**  
📧 yadav.gauravsingh@gmail.com  
<sub>Built with ❤️ using Swiss Ephemeris & Streamlit</sub>
""")
