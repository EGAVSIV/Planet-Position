import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import swisseph as swe
import pytz, datetime, math, time, sys

st.set_page_config(page_title="वेदिक ग्रह घड़ी", layout="wide")

LAT = 19.0760
LON = 72.8777
ELEV = 14

SIGNS = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक",
         "धनु","मकर","कुंभ","मीन"]

NAKSHATRAS = [
("अश्विनी","केतु"),("भरणी","शुक्र"),("कृत्तिका","सूर्य"),
("रोहिणी","चन्द्र"),("मृगशिरा","मंगल"),("आर्द्रा","राहु"),
("पुनर्वसु","बृहस्पति"),("पुष्य","शनि"),("आश्लेषा","बुध"),
("मघा","केतु"),("पूर्व फाल्गुनी","शुक्र"),("उत्तर फाल्गुनी","सूर्य"),
("हस्त","चन्द्र"),("चित्रा","मंगल"),("स्वाति","राहु"),
("विशाखा","बृहस्पति"),("अनुराधा","शनि"),("ज्येष्ठा","बुध"),
("मूला","केतु"),("पूर्वाषाढा","शुक्र"),("उत्तराषाढा","सूर्य"),
("श्रवण","चन्द्र"),("धनिष्ठा","मंगल"),("शतभिषा","राहु"),
("पूर्वभाद्रपदा","बृहस्पति"),("उत्तरभाद्रपदा","शनि"),("रेवती","बुध"),
]

PLANETS = {
"सूर्य":(swe.SUN,"🜚"),"चन्द्र":(swe.MOON,"☽"),"मंगल":(swe.MARS,"♂"),
"बुध":(swe.MERCURY,"☿"),"बृहस्पति":(swe.JUPITER,"♃"),
"शुक्र":(swe.VENUS,"♀"),"शनि":(swe.SATURN,"♄"),
"राहु":(swe.TRUE_NODE,"☊")
}

PLANET_SYMBOL_OVERRIDE={
"सूर्य":"🜚","चन्द्र":"☽","मंगल":"♂","बुध":"☿","बृहस्पति":"♃",
"शुक्र":"♀","शनि":"♄","राहु":"☊","केतु":"☋",
}

PLANET_COLOR={
"सूर्य":"#FFB86B","चन्द्र":"#BFE9FF","मंगल":"#FF8A8A","बुध":"#B6FF9C",
"बृहस्पति":"#FFD88A","शुक्र":"#F9B0FF","शनि":"#C0C8FF",
"राहु":"#FFCF66","केतु":"#FFCF66"
}

swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)

# ------------------------------------------------------
# SAME ASTRO LOGIC AS ORIGINAL — NO CHANGE
# ------------------------------------------------------
def compute_positions():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)
    jd_ut = swe.julday(now.year, now.month, now.day,
                       now.hour+now.minute/60+now.second/3600) - (5.5/24)
    pos={}
    speed={}
    for pname,(pcode,_) in PLANETS.items():
        r=swe.calc_ut(jd_ut,pcode)
        lon=r[0][0]; sp=r[0][3]
        ay=swe.get_ayanamsa_ut(jd_ut)
        sid=(lon-ay)%360
        pos[pname]=sid; speed[pname]=(sp<0)

    if "राहु" in pos:
        pos["केतु"]=(pos["राहु"]+180)%360
        speed["केतु"]=speed["राहु"]

    return pos, speed, now

def nakshatra_info(lon):
    each=13+1/3
    i=int(lon//each)%27
    p=int((lon%each)//(each/4))+1
    return *NAKSHATRAS[i], p

# ------------------------------------------------------
# GRAPHICS – same rendering code
# ------------------------------------------------------
def draw_chart(positions, retro):
    size=650
    img=Image.new("RGBA",(size,size),(0,0,0,255))
    d=ImageDraw.Draw(img)
    cx=cy=size//2; radius=220

    for i in range(12):
        ang=90-i*30
        x=cx+(radius+15)*math.cos(math.radians(ang))
        y=cy-(radius+15)*math.sin(math.radians(ang))
        d.text((x,y),SIGNS[i],fill="white")

    for pname,sid in positions.items():
        ang=90-sid; r=radius
        x=cx+r*math.cos(math.radians(ang))
        y=cy-r*math.sin(math.radians(ang))

        d.ellipse([x-15,y-15,x+15,y+15],
                  fill=PLANET_COLOR[pname])
        d.text((x,y),PLANET_SYMBOL_OVERRIDE[pname],
               fill="black")

        nak, lord, pd=nakshatra_info(sid)
        d.text((x,y-30),nak,fill="yellow")

        if retro[pname]:
            d.text((x,y+28),"℞",fill="red")

    return img

# ------------------------------------------------------
# STREAMLIT UI
# ------------------------------------------------------
st.title("वेदिक ग्रह घड़ी — 3D Hindi UI")
if st.button("Refresh"):
    st.rerun()

pos, retro, now=compute_positions()

col1,col2=st.columns([1.4,1])

with col1:
    im=draw_chart(pos,retro)
    st.image(im, use_container_width=True)

with col2:
    st.subheader("Planets Table")
    rows=[]
    for pname in pos:
        lon=pos[pname]
        nak,lord,pd=nakshatra_info(lon)
        rows.append([
            pname,
            PLANET_SYMBOL_OVERRIDE[pname],
            f"{lon:.4f}°",
            SIGNS[int(lon//30)],
            nak,
            "Retro" if retro[pname] else "Direct"
        ])
    st.dataframe(rows,
        column_config={
            0:"Planet",1:"Symbol",2:"Longitude",
            3:"Rashi",4:"Nakshatra",5:"Motion"
        }, hide_index=True)

st.info(f"Last Updated: {now.strftime('%d-%b-%Y %H:%M:%S')}")

st.experimental_rerun()
