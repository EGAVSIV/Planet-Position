import streamlit as st
import swisseph as swe
import datetime, pytz, math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import tempfile

st.set_page_config(page_title="🪐 सम्पूर्ण वैदिक पंचांग", layout="wide")

# =============================
# CONSTANT DATA
# =============================
SIGNS = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या",
         "तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"]

NAKSHATRAS = [
"अश्विनी","भरणी","कृत्तिका","रोहिणी","मृगशिरा","आर्द्रा",
"पुनर्वसु","पुष्य","आश्लेषा","मघा","पूर्व फाल्गुनी","उत्तर फाल्गुनी",
"हस्त","चित्रा","स्वाति","विशाखा","अनुराधा","ज्येष्ठा",
"मूला","पूर्वाषाढ़ा","उत्तराषाढ़ा","श्रवण","धनिष्ठा","शतभिषा",
"पूर्वभाद्रपदा","उत्तरभाद्रपदा","रेवती"
]

PLANETS = [
("सूर्य", swe.SUN),("चन्द्र", swe.MOON),("मंगल", swe.MARS),
("बुध", swe.MERCURY),("बृहस्पति", swe.JUPITER),
("शुक्र", swe.VENUS),("शनि", swe.SATURN),("राहु", swe.MEAN_NODE)
]

TITHIS = [
"प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पंचमी","षष्ठी","सप्तमी",
"अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","पूर्णिमा",
"प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पंचमी","षष्ठी","सप्तमी",
"अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","अमावस्या"
]

HORA_SEQ = ["सूर्य","शुक्र","बुध","चन्द्र","शनि","बृहस्पति","मंगल"]
CHOGHADIYA_DAY = ["उद्वेग","चर","लाभ","अमृत","काल","शुभ","रोग","उद्वेग"]

swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
IST = pytz.timezone("Asia/Kolkata")

# =============================
# CORE FUNCTIONS
# =============================
def get_positions(dt_utc):
    jd = swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,
                    dt_utc.hour+dt_utc.minute/60)
    ay = swe.get_ayanamsa_ut(jd)
    pos={}
    for n,c in PLANETS:
        r=swe.calc_ut(jd,c)
        pos[n]=(r[0][0]-ay)%360
    pos["केतु"]=(pos["राहु"]+180)%360
    return pos

def get_tithi(pos):
    diff=(pos["चन्द्र"]-pos["सूर्य"])%360
    return TITHIS[int(diff//12)]

def nakshatra_pada(lon):
    size=13+1/3
    idx=int(lon//size)
    pada=int((lon%size)//(size/4))+1
    return NAKSHATRAS[idx],pada

def hora_of_time(dt_ist):
    sunrise=dt_ist.replace(hour=6,minute=0)
    diff=int((dt_ist-sunrise).total_seconds()//3600)
    lord=HORA_SEQ[dt_ist.weekday()]
    return HORA_SEQ[(HORA_SEQ.index(lord)+diff)%7]

def choghadiya_of_time(dt_ist):
    sunrise=dt_ist.replace(hour=6,minute=0)
    part=int((dt_ist-sunrise).total_seconds()//(90*60))
    return CHOGHADIYA_DAY[part%8]

def list_amavasya_purnima(year):
    out=[]
    for i in range(366):
        d=datetime.datetime(year,1,1,tzinfo=pytz.utc)+datetime.timedelta(days=i)
        t=get_tithi(get_positions(d))
        if t in ["अमावस्या","पूर्णिमा"]:
            out.append([d.astimezone(IST).date(),t])
    return out

def festival_calendar(year):
    fest=[]
    lunar=list_amavasya_purnima(year)
    for d,t in lunar:
        fest.append([d,t])
    fest += [
        [datetime.date(year,3,25),"रामनवमी"],
        [datetime.date(year,8,19),"रक्षाबंधन"],
        [datetime.date(year,8,26),"कृष्ण जन्माष्टमी"],
        [datetime.date(year,10,12),"दशहरा"],
        [datetime.date(year,11,1),"दीपावली"],
        [datetime.date(year,3,8),"होली"],
        [datetime.date(year,2,14),"बसंत पंचमी"]
    ]
    return sorted(fest)

# =============================
# PDF EXPORT
# =============================
def export_pdf(title, rows):
    tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
    doc=SimpleDocTemplate(tmp.name,pagesize=A4)
    styles=getSampleStyleSheet()
    flow=[Paragraph(title,styles["Title"]),Spacer(1,12)]
    flow.append(Table(rows))
    doc.build(flow)
    return tmp.name

# =============================
# UI
# =============================
st.title("🪐 सम्पूर्ण वैदिक पंचांग")

date=st.date_input("तारीख़ चुनें",datetime.date.today())
time=st.time_input("समय चुनें")

dt_ist=IST.localize(datetime.datetime.combine(date,time))
dt_utc=dt_ist.astimezone(pytz.utc)
pos=get_positions(dt_utc)

st.subheader("🕉️ लाइव पंचांग")
st.write("**तिथि:**",get_tithi(pos))
st.write("**नक्षत्र:**",nakshatra_pada(pos["चन्द्र"]))
st.write("**Hora:**",hora_of_time(dt_ist))
st.write("**Choghadiya:**",choghadiya_of_time(dt_ist))

tabs=st.tabs(["🌑 अमावस्या/पूर्णिमा","📅 त्यौहार","📄 PDF Export"])

with tabs[0]:
    year=st.number_input("वर्ष",date.year)
    ap=list_amavasya_purnima(year)
    st.table(ap)

with tabs[1]:
    fest=festival_calendar(date.year)
    st.table(fest)

with tabs[2]:
    if st.button("📄 Export Panchang PDF"):
        pdf=export_pdf("वैदिक पंचांग",[
            ["तिथि",get_tithi(pos)],
            ["Hora",hora_of_time(dt_ist)],
            ["Choghadiya",choghadiya_of_time(dt_ist)]
        ])
        with open(pdf,"rb") as f:
            st.download_button("Download PDF",f,file_name="panchang.pdf")
