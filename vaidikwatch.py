import streamlit as st
import swisseph as swe
import datetime, pytz, math
import pandas as pd
import hashlib

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
("सूर्य", swe.SUN, "☉"),
("चन्द्र", swe.MOON,"☽"),
("मंगल", swe.MARS,"♂"),
("बुध", swe.MERCURY,"☿"),
("बृहस्पति", swe.JUPITER,"♃"),
("शुक्र", swe.VENUS,"♀"),
("शनि", swe.SATURN,"♄"),
("राहु", swe.MEAN_NODE,"☊")
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

# ================= BLUE CLOCK SVG =================
def generate_svg(pos):
    svg = """
    <svg width="700" height="700" viewBox="0 0 700 700" style="margin:auto;display:block">
    <defs>
        <radialGradient id="glow">
            <stop offset="70%" stop-color="#0a1e3a"/>
            <stop offset="100%" stop-color="#3fa9f5"/>
        </radialGradient>
    </defs>
    <circle cx="350" cy="350" r="330" fill="url(#glow)"/>
    <circle cx="350" cy="350" r="270" fill="#050b18" stroke="#88c9ff" stroke-width="3"/>
    """

    for i in range(12):
        ang = math.radians(90 - i*30)
        x = 350 + 260 * math.cos(ang)
        y = 350 - 260 * math.sin(ang)
        svg += f"<line x1='350' y1='350' x2='{x}' y2='{y}' stroke='#ffd700'/>"
        svg += f"<text x='{350 + 210*math.cos(ang)}' y='{350 - 210*math.sin(ang)}' fill='#00e6ff' font-size='22' text-anchor='middle'>{SIGNS[i]}</text>"

    for name, code, sym in PLANETS:
        lon = pos[name]
        ang = math.radians(90 - lon)
        px = 350 + 200 * math.cos(ang)
        py = 350 - 200 * math.sin(ang)
        svg += f"""
        <circle cx="{px}" cy="{py}" r="22" fill="#ffd27f"/>
        <text x="{px}" y="{py}" text-anchor="middle" dominant-baseline="middle">{sym}</text>
        """

    svg += "</svg>"
    return svg

# ================= UI =================
st.title("🪐 वेदिक ग्रह घड़ी — Drik Panchang")

c1, c2, c3 = st.columns(3)
today = datetime.date.today()
date = c1.date_input("तारीख़", today)
time = c2.time_input("समय")

if c3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    date, time = now.date(), now.time()

ist = pytz.timezone("Asia/Kolkata")
dt_ist = ist.localize(datetime.datetime.combine(date, time))
dt_utc = dt_ist.astimezone(pytz.utc)

pos, retro, jd = get_positions(dt_utc)

# ===== CORRECT DRIK PANCHANG LAGNA =====
ascmc, _ = swe.houses_ex(jd, LAT, LON, b'P', FLAGS)
lagna_deg = ascmc[0] % 360
lagna_sign = SIGNS[int(lagna_deg // 30)]

# ================= LAYOUT =================
left, right = st.columns([2, 1])

with left:
    st.components.v1.html(generate_svg(pos), height=720)

with right:
    st.subheader("🌙 ज्योतिष सार")

    moon_nak, moon_lord, moon_pada = nakshatra_pada(pos["चन्द्र"])

    summary = [
        ["चन्द्र नक्षत्र", moon_nak],
        ["नक्षत्र पाद", moon_pada],
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
        f"{nak} (पाद {pada})",
        "🔁 वक्री" if retro[p] else "➡️ मार्गी"
    ])

# --- ADD KETU (Shadow Planet) ---
nak, lord, pada = nakshatra_pada(pos["केतु"])
rows.append([
    "केतु",
    f"{pos['केतु']:.2f}°",
    SIGNS[int(pos["केतु"]//30)],
    f"{nak} (पाद {pada})",
    "🔁 वक्री" if retro["केतु"] else "➡️ मार्गी"
   ])


    st.table(pd.DataFrame(
        rows,
        columns=["ग्रह","डिग्री","राशि","नक्षत्र","स्थिति"]
    ))

st.success("IST समय: " + dt_ist.strftime("%d-%b-%Y %H:%M:%S"))

st.markdown("""
---
### *Gaurav Singh Yadav*  
**Quant Trader | Energy & Commodity Intelligence**  
📧 yadav.gauravsingh@gmail.com  
<sub>Built with ❤️ using Swiss Ephemeris & Streamlit</sub>
""")
