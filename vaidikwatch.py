import streamlit as st
import swisseph as swe
import datetime, pytz, math

st.set_page_config(page_title="🪐 वेदिक ग्रह घड़ी — वेब संस्करण", layout="wide")

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

TITHIS = [
"प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पंचमी","षष्ठी","सप्तमी",
"अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","पूर्णिमा",
"प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पंचमी","षष्ठी","सप्तमी",
"अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","अमावस्या"
]

KARANS = [
"बव","बालव","कौलव","तैतिल","गर","वणिज","विष्टि",
"बव","बालव","कौलव","तैतिल","गर","वणिज","विष्टि",
"बव","बालव","कौलव","तैतिल","गर","वणिज","विष्टि",
"बव","बालव","कौलव","तैतिल","गर","वणिज","विष्टि",
"शकुनि","चतुष्पद","नाग","किंस्तुघ्न"
]

swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)

# -----------------------------
# ASTRO FUNCTIONS
# -----------------------------
def get_positions(dt_utc):
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60)
    pos = {}
    ay = swe.get_ayanamsa_ut(jd)

    for name, code, sym in PLANETS:
        r = swe.calc_ut(jd, code)
        pos[name] = (r[0][0] - ay) % 360

    pos["केतु"] = (pos["राहु"] + 180) % 360
    return pos

def nakshatra_pada(lon):
    size = 13 + 1/3
    idx = int(lon // size)
    pada = int((lon % size) // (size/4)) + 1
    return NAKSHATRAS[idx][0], pada

def get_tithi(pos):
    diff = (pos["चन्द्र"] - pos["सूर्य"]) % 360
    return TITHIS[int(diff // 12)]

def get_karan(pos):
    diff = (pos["चन्द्र"] - pos["सूर्य"]) % 360
    return KARANS[int((diff % 12) // 6 + (diff // 12)*2) % 60]

def get_lagna(dt_utc):
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60)
    ay = swe.get_ayanamsa_ut(jd)
    houses, ascmc = swe.houses_ex(jd, 28.6139, 77.2090, b'P', swe.FLG_SIDEREAL)
    lon = (ascmc[0] - ay) % 360
    return lon, SIGNS[int(lon//30)], lon%30

# -----------------------------
# SVG GENERATOR
# -----------------------------
def generate_svg(pos, lagna_lon, dt_ist):

    time_text = dt_ist.strftime("%d %b %Y  %H:%M IST")

    svg = f"""
    <svg width="700" height="740" viewBox="0 0 700 740" style="display:block;margin:auto">

    <text x="350" y="30" fill="#00ffcc" font-size="22" text-anchor="middle">
    {time_text}
    </text>

    <circle cx="350" cy="370" r="330" fill="#0a0f1e" stroke="#4da6ff" stroke-width="3"/>
    <circle cx="350" cy="370" r="270" fill="#000814" stroke="#888" stroke-width="2"/>
    """

    for i in range(12):
        ang = math.radians(90 - i*30)
        x = 350 + 260*math.cos(ang)
        y = 370 - 260*math.sin(ang)
        svg += f'<line x1="350" y1="370" x2="{x}" y2="{y}" stroke="#f7d000" stroke-width="2"/>'
        svg += f'<text x="{350+200*math.cos(ang)}" y="{370-200*math.sin(ang)}" fill="#00e6ff" font-size="22" text-anchor="middle">{SIGNS[i]}</text>'

    # Lagna Highlight
    la = math.radians(90 - lagna_lon)
    svg += f'<line x1="350" y1="370" x2="{350+310*math.cos(la)}" y2="{370-310*math.sin(la)}" stroke="red" stroke-width="5"/>'

    for name, code, sym in PLANETS:
        lon = pos[name]
        ang = math.radians(90 - lon)
        px = 350 + 210*math.cos(ang)
        py = 370 - 210*math.sin(ang)
        nak,_ = nakshatra_pada(lon)

        ring = ""
        if name=="चन्द्र":
            ring = f'<circle cx="{px}" cy="{py}" r="36" fill="none" stroke="yellow" stroke-width="4"/>'

        svg += f"""
        {ring}
        <circle cx="{px}" cy="{py}" r="26" fill="{COL[name]}" stroke="black"/>
        <text x="{px}" y="{py}" font-size="20" text-anchor="middle">{sym}</text>
        """

    svg += "</svg>"
    return svg

# -----------------------------
# UI
# -----------------------------
st.title("🪐 वेदिक ग्रह घड़ी — गौरव सिंह यादव")

c1,c2,c3 = st.columns(3)
today = datetime.date.today()

date = c1.date_input("तारीख़", today, today-datetime.timedelta(days=365*100), today+datetime.timedelta(days=365*100))
time = c2.time_input("समय")

if c3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    date, time = now.date(), now.time()

ist = pytz.timezone("Asia/Kolkata")
dt_ist = ist.localize(datetime.datetime.combine(date,time))
dt_utc = dt_ist.astimezone(pytz.utc)

pos = get_positions(dt_utc)
lagna_lon, lagna_sign, lagna_deg = get_lagna(dt_utc)

svg = generate_svg(pos, lagna_lon, dt_ist)
st.components.v1.html(svg, height=760)

st.subheader("🕉️ पंचांग")
st.write(f"**लग्न:** {lagna_sign} ({lagna_deg:.2f}°)")
st.write(f"**तिथि:** {get_tithi(pos)}")
st.write(f"**करण:** {get_karan(pos)}")

st.subheader("ग्रह तालिका")
rows=[]
for p,_,sym in PLANETS:
    nak,pada = nakshatra_pada(pos[p])
    rows.append([p,sym,f"{pos[p]:.2f}°",SIGNS[int(pos[p]//30)],nak,f"पाद {pada}"])
st.table(rows)
