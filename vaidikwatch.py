import streamlit as st
import swisseph as swe
import datetime, pytz, math
import pandas as pd
import hashlib

# ---------------- PASSWORD HASH ----------------
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

st.set_page_config(
    page_title="वेदिक ग्रह घड़ी — वेब संस्करण",
    layout="wide",
    page_icon="🪐"
)

# ---------------- ASTRO DATA ----------------
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

swe.set_sid_mode(swe.SIDM_LAHIRI)

# ---------------- FUNCTIONS ----------------
def get_positions(dt_utc):
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60)

    pos = {}
    retro = {}

    for name, code, sym in PLANETS:
        r, _ = swe.calc_ut(jd, code)
        ay = swe.get_ayanamsa_ut(jd)

        lon = (r[0] - ay) % 360
        speed = r[3]

        pos[name] = lon
        retro[name] = speed < 0   # 🔁 Retrograde check

    pos["केतु"] = (pos["राहु"] + 180) % 360
    retro["केतु"] = retro["राहु"]

    return pos, retro


def nakshatra_of(lon):
    size = 13 + 1/3
    idx = int(lon // size) % 27
    return NAKSHATRAS[idx][0], NAKSHATRAS[idx][1]

# ---------------- SVG ----------------
def generate_svg(pos):
    svg = """
    <svg width="700" height="700" viewBox="0 0 700 700" style="display:block;margin:auto">
    <circle cx="350" cy="350" r="300" fill="#0a0f1e" stroke="#888" stroke-width="3"/>
    """

    for i in range(12):
        ang = math.radians(90 - i*30)
        x = 350 + 260 * math.cos(ang)
        y = 350 - 260 * math.sin(ang)
        svg += f"<line x1='350' y1='350' x2='{x}' y2='{y}' stroke='#ffaa00'/>"
        svg += f"<text x='{350 + 220 * math.cos(ang)}' y='{350 - 220 * math.sin(ang)}' fill='cyan'>{SIGNS[i]}</text>"

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

# ---------------- UI ----------------
st.title("🪐 वेदिक ग्रह घड़ी — गौरव सिंह यादव")

c1, c2, c3 = st.columns(3)

today = datetime.date.today()
date = c1.date_input("तारीख़", value=today)
time = c2.time_input("समय")

if c3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    date, time = now.date(), now.time()

ist = pytz.timezone("Asia/Kolkata")
dt_ist = ist.localize(datetime.datetime.combine(date, time))
dt_utc = dt_ist.astimezone(pytz.utc)

pos, retro = get_positions(dt_utc)

# ---------------- LAYOUT ----------------
left, right = st.columns([2, 1])

# LEFT — CHAKRA
with left:
    svg = generate_svg(pos)
    st.components.v1.html(svg, height=720)

# RIGHT — ASTRO TABLE
with right:
    st.subheader("🌙 ज्योतिष विवरण")

    # Lagna
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60)
    ascmc, _ = swe.houses(jd, 19.07598, 72.87766)
    lagna_deg = ascmc[0] % 360
    lagna_sign = SIGNS[int(lagna_deg // 30)]

    moon_nak, moon_lord = nakshatra_of(pos["चन्द्र"])

    summary = [
        ["चन्द्र नक्षत्र", moon_nak],
        ["नक्षत्र स्वामी", moon_lord],
        ["लग्न", lagna_sign],
        ["लग्न अंश", f"{lagna_deg:.2f}°"],
        ["समय (IST)", dt_ist.strftime("%d-%b-%Y %H:%M")]
    ]

    st.table(pd.DataFrame(summary, columns=["तत्व", "मान"]))

    st.subheader("🪐 ग्रह स्थिति")

    rows = []
    for p, code, sym in PLANETS:
        nak, lord = nakshatra_of(pos[p])
        rows.append([
            p,
            f"{pos[p]:.2f}°",
            SIGNS[int(pos[p] // 30)],
            nak,
            "🔁 वक्री" if retro[p] else "➡️ मार्गी"
        ])

    st.table(pd.DataFrame(
        rows,
        columns=["ग्रह", "डिग्री", "राशि", "नक्षत्र", "स्थिति"]
    ))

st.success("IST समय: " + dt_ist.strftime("%d-%b-%Y %H:%M:%S"))

st.markdown("""
---
### 👤 *Gaurav Singh Yadav*  
**Quant Trader | Energy & Commodity Intelligence**

📞 +91-8003994518  
📧 yadav.gauravsingh@gmail.com  

<sub>Built with ❤️ using Python, Swiss Ephemeris & Streamlit</sub>
""")
