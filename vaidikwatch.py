import streamlit as st
import swisseph as swe
import datetime, pytz, math
import hashlib

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

st.set_page_config(page_title=" वेदिक ग्रह घड़ी🪐 — वेब संस्करण", layout="wide",page_icon="🪐")

# -----------------------------
# ASTRO DATA
# -----------------------------
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
("सूर्य", swe.SUN, "🜚"),
("चन्द्र", swe.MOON,"☽"),
("मंगल", swe.MARS,"♂"),
("बुध", swe.MERCURY,"☿"),
("बृहस्पति", swe.JUPITER,"♃"),
("शुक्र", swe.VENUS,"♀"),
("शनि", swe.SATURN,"♄"),
("राहु", swe.MEAN_NODE,"☊")
]

COL = {
"सूर्य":"#ffcc66","चन्द्र":"#cce6ff","मंगल":"#ff9999",
"बुध":"#ccffcc","बृहस्पति":"#ffe6b3","शुक्र":"#ffccff",
"शनि":"#c2c2ff","राहु":"#ffd27f","केतु":"#ffd27f"
}

swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)

# -----------------------------
# ASTRO FUNCTIONS
# -----------------------------

def get_positions(dt):
    jd = swe.julday(dt.year, dt.month, dt.day,
                    dt.hour + dt.minute/60)
    pos = {}
    for name, code, sym in PLANETS:
        r = swe.calc_ut(jd, code)
        ay = swe.get_ayanamsa_ut(jd)
        pos[name] = (r[0][0] - ay) % 360

    pos["केतु"] = (pos["राहु"] + 180) % 360
    return pos


def nakshatra_of(lon):
    size = 13 + 1/3
    idx = int(lon // size) % 27
    return NAKSHATRAS[idx][0]

# -----------------------------
# SVG GENERATOR (Perfect Circles)
# -----------------------------

def generate_svg(pos):

    svg = """
    <svg width="700" height="700" viewBox="0 0 700 700" style="display:block;margin:auto">

        <!-- Outer Glow Ring -->
        <defs>
            <radialGradient id="outerGlow" cx="50%" cy="50%" r="50%">
                <stop offset="60%" stop-color="#0d1b2a"/>
                <stop offset="95%" stop-color="#4da6ff"/>
                <stop offset="100%" stop-color="#99ccff"/>
            </radialGradient>
        </defs>

        <circle cx="350" cy="350" r="330" fill="url(#outerGlow)" stroke="#222" stroke-width="2"/>

        <!-- Inner Circle -->
        <circle cx="350" cy="350" r="270" fill="#0a0f1e" stroke="#666" stroke-width="2"/>

        <!-- Center Text -->
        <text x="350" y="340" fill="white" font-size="30" text-anchor="middle">वेदिक घड़ी</text>
        <text x="350" y="370" fill="#cccccc" font-size="18" text-anchor="middle">(लाहिड़ी अयनांश)</text>

        <!-- Zodiac Divisions -->
    """

    # Draw 12 radial lines + zodiac names
    for i in range(12):
        ang = math.radians(90 - (i*30))
        x = 350 + 260 * math.cos(ang)
        y = 350 - 260 * math.sin(ang)

        svg += f"""
        <line x1="350" y1="350" x2="{x}" y2="{y}"
              stroke="#f7d000" stroke-width="3"/>

        <text x="{350 + 200 * math.cos(ang)}"
              y="{350 - 200 * math.sin(ang)}"
              fill="#00e6ff" font-size="24" text-anchor="middle"
              dominant-baseline="middle">{SIGNS[i]}</text>
        """

    # Planets
    for name, code, sym in PLANETS:
        lon = pos[name]
        ang = math.radians(90 - lon)

        px = 350 + 210 * math.cos(ang)
        py = 350 - 210 * math.sin(ang)

        nak = nakshatra_of(lon)
        color = COL[name]

        svg += f"""
        <circle cx="{px}" cy="{py}" r="28" fill="{color}" stroke="black" stroke-width="2"/>

        <text x="{px}" y="{py}" font-size="22" font-weight="bold"
              text-anchor="middle" dominant-baseline="middle">{sym}</text>

        <text x="{px}" y="{py + 42}" fill="white" font-size="18"
              text-anchor="middle">{name}</text>

        <text x="{px}" y="{py - 42}" fill="#ffeb99" font-size="16"
              text-anchor="middle">{nak}</text>
        """

    svg += "</svg>"
    return svg

# -----------------------------
# STREAMLIT UI
# -----------------------------

st.title("🪐 वेदिक ग्रह घड़ी — गौरव सिंह यादव")

col1, col2, col3 = st.columns(3)

today = datetime.date.today()

date = col1.date_input(
    "तारीख़ चुनें",
    value=today,
    min_value=today - datetime.timedelta(days=365*100),
    max_value=today + datetime.timedelta(days=365*100)
)

time = col2.time_input("समय चुनें")

if col3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    date, time = now.date(), now.time()

ist = pytz.timezone("Asia/Kolkata")
dt_ist = ist.localize(datetime.datetime.combine(date, time))

# Convert to UTC for Swiss Ephemeris
dt_utc = dt_ist.astimezone(pytz.utc)

pos = get_positions(dt_utc)

# Chakra Display
svg = generate_svg(pos)
st.components.v1.html(svg, height=720)

# Table
st.subheader("ग्रह तालिका")

table = []
for p, code, sym in PLANETS:
    table.append([
        p, sym,
        f"{pos[p]:.2f}°",
        SIGNS[int(pos[p]//30)],
        nakshatra_of(pos[p])
    ])

st.table(table)

st.success("समय (IST): " + dt_ist.strftime("%d-%b-%Y %H:%M:%S"))


st.markdown("""
---
### 👤 **Gaurav Singh Yadav**  
**Quant Trader | Energy & Commodity Intelligence**

📈 Market Analytics • Order Flow • Derivatives  
📞 +91-8003994518  
📧 yadav.gauravsingh@gmail.com  

<sub>Built with ❤️ using Python & Streamlit</sub>
""")

