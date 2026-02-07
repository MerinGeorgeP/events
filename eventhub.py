import streamlit as st
import sqlite3
import os
import uuid

# ================= CONFIG =================
st.set_page_config("EventHub", layout="wide")

DB = "eventhub.db"
POSTERS = "uploads/posters"
CERTS = "uploads/certificates"
PROFILE_PICS = "uploads/profile_pics"

os.makedirs(POSTERS, exist_ok=True)
os.makedirs(CERTS, exist_ok=True)
os.makedirs(PROFILE_PICS, exist_ok=True)

# ================= DATABASE =================
conn = sqlite3.connect(DB, check_same_thread=False)
c = conn.cursor()

# -------- USERS --------
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    name TEXT,
    college TEXT,
    interests TEXT
)
""")

# -------- ORGANISERS (THIS WAS MISSING ❗) --------
c.execute("""
CREATE TABLE IF NOT EXISTS organisers (
    username TEXT PRIMARY KEY,
    college TEXT,
    description TEXT,
    profile_pic TEXT
)
""")

# -------- EVENTS --------
c.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organiser TEXT,
    name TEXT,
    date TEXT,
    time TEXT,
    venue TEXT,
    poster TEXT,
    description TEXT,
    fees TEXT,
    reg_link TEXT,
    level TEXT,
    topics TEXT,
    activity_points TEXT
)
""")

# -------- CERTIFICATES --------
c.execute("""
CREATE TABLE IF NOT EXISTS certificates (
    event_id INTEGER,
    participant TEXT,
    file TEXT
)
""")

conn.commit()

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = "login"

# ================= HELPERS =================
def logout():
    st.session_state.clear()
    st.session_state.page = "login"
    st.rerun()

def get_organiser(username):
    c.execute(
        "SELECT college, description, profile_pic FROM organisers WHERE username=?",
        (username,)
    )
    return c.fetchone()

# ==================================================
# LOGIN PAGE
# ==================================================
def login_page():
    st.title("🎓 EventHub")
    st.markdown(
        "<p style='color:gray'>One platform to discover, manage, and participate in university events.</p>",
        unsafe_allow_html=True
    )

    role = st.selectbox("Account Type", ["participant", "organiser"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=? AND role=?",
                (username, password, role)
            )
            user = c.fetchone()
            if user:
                st.session_state.user = user
                st.session_state.role = role
                st.session_state.page = (
                    "organiser_dashboard" if role == "organiser"
                    else "participant_dashboard"
                )
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        if st.button("Register"):
            st.session_state.page = "register"
            st.rerun()

# ==================================================
# REGISTER PAGE
# ==================================================
def register_page():
    st.title("📝 Register on EventHub")

    if st.button("⬅ Back to Login"):
        st.session_state.page = "login"
        st.rerun()

    role = st.selectbox("Account Type", ["participant", "organiser"])

    # -------- PARTICIPANT --------
    if role == "participant":
        name = st.text_input("Full Name")
        college = st.text_input("College Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        interests = st.multiselect(
            "Interests",
            ["AI/ML","Web Dev","App Dev","Cybersecurity",
             "Robotics","Data Science","Music","Dance","Drama","Photography"]
        )

        if st.button("Create Participant Account"):
            c.execute("SELECT 1 FROM users WHERE username=?", (username,))
            if c.fetchone():
                st.error("Username already exists")
                return

            c.execute("""
            INSERT INTO users (username,password,role,name,college,interests)
            VALUES (?,?,?,?,?,?)
            """, (username,password,"participant",name,college,",".join(interests)))

            conn.commit()
            st.success("Registered successfully")
            st.session_state.page = "login"
            st.rerun()

    # -------- ORGANISER --------
    else:
        college = st.text_input("College Name")
        club = st.text_input("Club Name (Username)")
        desc = st.text_area("Club Description")
        pic = st.file_uploader("Club Logo", type=["png","jpg","jpeg"])
        password = st.text_input("Password", type="password")

        if st.button("Create Organiser Account"):
            c.execute("SELECT 1 FROM users WHERE username=?", (club,))
            if c.fetchone():
                st.error("Club already exists")
                return

            pic_path = None
            if pic:
                filename = f"{club}_{uuid.uuid4().hex}.png"
                pic_path = f"{PROFILE_PICS}/{filename}"
                with open(pic_path, "wb") as f:
                    f.write(pic.read())

            c.execute("""
            INSERT INTO users (username,password,role,name,college,interests)
            VALUES (?,?,?,?,?,?)
            """, (club,password,"organiser",club,college,""))

            c.execute("""
            INSERT INTO organisers (username,college,description,profile_pic)
            VALUES (?,?,?,?)
            """, (club,college,desc,pic_path))

            conn.commit()
            st.success("Organiser registered")
            st.session_state.page = "login"
            st.rerun()

# ==================================================
# ORGANISER DASHBOARD
# ==================================================
def organiser_dashboard():
    profile = get_organiser(st.session_state.user[0])

    col1,col2,col3 = st.columns([1,4,1])

    with col1:
        if profile and profile[2]:
            st.image(profile[2], width=120)
        else:
            st.image("https://via.placeholder.com/120")

    with col2:
        st.markdown(f"## {st.session_state.user[0]}")
        st.markdown(f"<span style='color:gray'>{profile[0]}</span>", unsafe_allow_html=True)
        st.write(profile[1])

    with col3:
        if st.button("🚪 Logout"):
            logout()

    st.markdown("---")

    if st.button("➕ Create New Event"):
        st.session_state.page = "create_event"
        st.rerun()

    c.execute("SELECT * FROM events WHERE organiser=?", (st.session_state.user[0],))
    for e in c.fetchall():
        if st.button(e[2], key=e[0]):
            st.session_state.selected_event = e
            st.session_state.page = "event_page"
            st.rerun()

# ==================================================
# PARTICIPANT DASHBOARD
# ==================================================
def participant_dashboard():
    with st.sidebar:
        st.header("Filters")
        topic = st.multiselect("Topics", ["AI/ML","Web Dev","Cybersecurity","Music","Dance"])
        level = st.selectbox("Level", ["All","Beginner","Intermediate","Advanced"])
        if st.button("Logout"):
            logout()

    st.title(f"👋 {st.session_state.user[0]}")
    c.execute("SELECT * FROM events")

    for e in c.fetchall():
        if topic and not any(t in e[11] for t in topic):
            continue
        if level!="All" and e[10]!=level:
            continue

        col1,col2 = st.columns([1,4])
        with col1:
            if e[6]:
                st.image(e[6], use_container_width=True)
        with col2:
            st.subheader(e[2])
            if st.button("View Event", key=f"p{e[0]}"):
                st.session_state.selected_event = e
                st.session_state.page = "event_page"
                st.rerun()

# ==================================================
# EVENT PAGE
# ==================================================
def event_page():
    if st.button("⬅ Back"):
        st.session_state.page = (
            "organiser_dashboard" if st.session_state.role=="organiser"
            else "participant_dashboard"
        )
        st.rerun()

    e = st.session_state.selected_event
    organiser = get_organiser(e[1])

    col1,col2 = st.columns([1,4])
    with col1:
        if organiser and organiser[2]:
            st.image(organiser[2], use_container_width=True)
    with col2:
        st.markdown(f"### {e[1]}")
        st.markdown(f"<span style='color:gray'>{organiser[0]}</span>", unsafe_allow_html=True)
        st.write(organiser[1])

    st.markdown("---")

    left,right = st.columns([3,2])
    with left:
        st.markdown(f"<h1>{e[2]}</h1>", unsafe_allow_html=True)
        st.write(e[7])
        st.write(f"📍 {e[5]} | 📅 {e[3]} | ⏰ {e[4]}")
        st.link_button("Register", e[9])
    with right:
        if e[6]:
            st.image(e[6], use_container_width=True)

# ==================================================
# ROUTER
# ==================================================
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.page == "organiser_dashboard":
    organiser_dashboard()
elif st.session_state.page == "participant_dashboard":
    participant_dashboard()
elif st.session_state.page == "create_event":
    create_event_page()
elif st.session_state.page == "event_page":
    event_page()
