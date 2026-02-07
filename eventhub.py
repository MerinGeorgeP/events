import streamlit as st
import sqlite3
import os

# ---------------- CONFIG ----------------
st.set_page_config("EventHub", layout="wide")
DB = "eventhub.db"
POSTERS = "uploads/posters"
CERTS = "uploads/certificates"

os.makedirs(POSTERS, exist_ok=True)
os.makedirs(CERTS, exist_ok=True)
PROFILE_PICS = "uploads/profile_pics"
os.makedirs(PROFILE_PICS, exist_ok=True)


# ---------------- DB ----------------
conn = sqlite3.connect(DB, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    name TEXT,
    college TEXT,
    interests TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS events(
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

c.execute("""
CREATE TABLE IF NOT EXISTS certificates(
    event_id INTEGER,
    participant TEXT,
    file TEXT
)
""")
conn.commit()

# ---------------- SESSION INIT ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.page = "login"
    st.rerun()

def get_organiser_profile(username):
    c.execute(
        "SELECT college, description, profile_pic FROM organisers WHERE username=?",
        (username,)
    )
    return c.fetchone()
def get_organiser_details(username):
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
        """
        <p style="font-size:16px; color:gray; margin-top:-10px;">
        EventHub is a unified university platform that connects students and organisers across BTech colleges. It enables personalised event discovery, seamless event management, and certificate access. With role-based dashboards, smart filters, and interest-based suggestions, EventHub ensures students never miss important technical or cultural events.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Login")

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


def register_page():
    st.title("📝 Register on EventHub")

    # -------- BACK BUTTON --------
    if st.button("⬅ Back to Login"):
        st.session_state.page = "login"
        st.rerun()

    st.markdown("---")

    role = st.selectbox("Account Type", ["participant", "organiser"])

    # ==================================================
    # PARTICIPANT REGISTRATION
    # ==================================================
    if role == "participant":
        st.subheader("👤 Participant Registration")

        name = st.text_input("Full Name")
        college = st.text_input("College Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        interests = st.multiselect(
            "Select Your Interests",
            [
                "AI/ML", "Web Development", "App Development",
                "Cybersecurity", "Robotics", "Data Science",
                "Music", "Dance", "Drama", "Photography"
            ]
        )

        if st.button("Create Participant Account"):
            if not all([name, college, username, password]):
                st.error("Please fill all required fields.")
                return

            c.execute("SELECT 1 FROM users WHERE username=?", (username,))
            if c.fetchone():
                st.error("Username already exists. Choose another.")
                return

            c.execute(
                "INSERT INTO users VALUES (?,?,?,?,?,?)",
                (
                    username,
                    password,
                    "participant",
                    name,
                    college,
                    ",".join(interests)
                )
            )
            conn.commit()

            st.success("Participant registered successfully! Please login.")
            st.session_state.page = "login"
            st.rerun()

    # ==================================================
    # ORGANISER REGISTRATION
    # ==================================================
    else:
        st.subheader("🎯 Organiser Registration")

        college = st.text_input("College Name")
        club = st.text_input("Club Name (Username)")
        desc = st.text_area("Club Description")
        pic = st.file_uploader(
            "Club Logo / Profile Picture",
            type=["png", "jpg", "jpeg"]
        )
        password = st.text_input("Password", type="password")

        if st.button("Create Organiser Account"):
            if not all([college, club, desc, password]):
                st.error("Please fill all required fields.")
                return

            # Check username uniqueness
            c.execute("SELECT 1 FROM users WHERE username=?", (club,))
            if c.fetchone():
                st.error("Club name already exists. Choose a different username.")
                return

            # Save profile picture
            pic_path = None
            if pic:
                import uuid
                filename = f"{club}_{uuid.uuid4().hex}.png"
                pic_path = f"{PROFILE_PICS}/{filename}"
                with open(pic_path, "wb") as f:
                    f.write(pic.read())

            # Insert into users table
            c.execute(
                "INSERT INTO users VALUES (?,?,?,?,?,?)",
                (
                    club,
                    password,
                    "organiser",
                    club,
                    college,
                    ""
                )
            )

            # Insert into organisers table
            c.execute(
                "INSERT INTO organisers VALUES (?,?,?,?)",
                (
                    club,
                    college,
                    desc,
                    pic_path
                )
            )

            conn.commit()

            st.success("Organiser registered successfully! Please login.")
            st.session_state.page = "login"
            st.rerun()




# ==================================================
# ORGANISER DASHBOARD
# ==================================================
def organiser_dashboard():
    profile = get_organiser_profile(st.session_state.user[0])

    col1, col2, col3 = st.columns([1.2, 4, 1])

    # Profile Picture
    with col1:
        if profile and profile[2]:
            st.image(profile[2], width=120)
        else:
            st.image("https://via.placeholder.com/120")

    # Club Info
    with col2:
        st.markdown(f"## {st.session_state.user[0]}")
        if profile:
            st.markdown(
                f"<span style='color:gray'>{profile[0]}</span>",
                unsafe_allow_html=True
            )
            st.write(profile[1])

    # Logout Button
    with col3:
        if st.button("🚪 Logout"):
            logout()

    st.markdown("---")

    

    if st.button("➕ Create New Event"):
        st.session_state.page = "create_event"
        st.rerun()

    st.subheader("📁 Events")

    c.execute("SELECT * FROM events WHERE organiser=?",
              (st.session_state.user[0],))
    events = c.fetchall()

    for e in events:
        with st.container(border=True):
            st.subheader(e[2])
            st.write(f"{e[3]} | {e[4]} | {e[5]}")

            if st.button("View Event", key=e[0]):
                st.session_state.selected_event = e
                st.session_state.page = "event_page"
                st.rerun()

# ==================================================
# CREATE EVENT PAGE
# ==================================================
def create_event_page():
    
    st.title("➕ Create New Event")

    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "organiser_dashboard"
        st.rerun()


    name = st.text_input("Event Name")
    date = st.date_input("Date")
    time = st.time_input("Time")
    venue = st.text_input("Venue")
    poster = st.file_uploader("Event Poster")
    desc = st.text_area("Description")

    fees = st.selectbox("Registration Fees", ["Free", "Paid"])
    link = st.text_input("Registration Link")

    level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
    topics = st.multiselect(
        "Topics",
        ["AI/ML", "Web Dev", "App Dev", "Cybersecurity",
         "Robotics", "Music", "Dance", "Drama"]
    )
    points = st.selectbox("Activity Points", ["0", "5", "10", "20"])

    if st.button("Create Event"):
        poster_path = ""
        if poster:
            poster_path = f"{POSTERS}/{name}.png"
            with open(poster_path, "wb") as f:
                f.write(poster.read())

        c.execute("""INSERT INTO events (
        organiser,
        name,
        date,
        time,
        venue,
        poster,
        description,
        fees,
        reg_link,
        level,
        topics,
        activity_points
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        st.session_state.user[0],
        name,
        str(date),
        str(time),
        venue,
        poster_path,
        desc,
        fees,
        link,
        level,
        ",".join(topics),
        points
    ))

        conn.commit()

        st.success("Event Created Successfully")
        st.session_state.page = "organiser_dashboard"
        st.rerun()

# ==================================================
# PARTICIPANT DASHBOARD
# ==================================================
def participant_dashboard():
    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.header("🔍 Filter Events")

        

        topic_filter = st.multiselect(
            "Topics",
            ["AI/ML", "Web Dev", "App Dev", "Cybersecurity",
             "Robotics", "Data Science",
             "Music", "Dance", "Drama", "Photography"]
        )

        level_filter = st.selectbox(
            "Level",
            ["All", "Beginner", "Intermediate", "Advanced"]
        )

        fee_filter = st.selectbox(
            "Registration Fees",
            ["All", "Free", "Paid"]
        )

        points_filter = st.selectbox(
            "Activity Points",
            ["All", "0", "5", "10", "20"]
        )

        st.markdown("---")

        if st.button("🚪 Logout"):
            logout()

    # ---------- MAIN CONTENT ----------
    st.title(f"👋 {st.session_state.user[0]}")

    search = st.text_input("🔍 Search Event")
    st.subheader("⭐ Suggested Events")

    

    c.execute("SELECT * FROM events")
    events = c.fetchall()

    for e in events:
        event_name = e[2].lower()
        event_level = e[10]
        event_topics = e[11].split(",") if e[11] else []
        event_fees = e[8]
        event_points = e[12]

        # SEARCH FILTER
        if search and search.lower() not in event_name:
            continue

        # TOPIC FILTER
        if topic_filter and not any(t in event_topics for t in topic_filter):
            continue

        # LEVEL FILTER
        if level_filter != "All" and event_level != level_filter:
            continue

        # FEES FILTER
        if fee_filter != "All" and event_fees != fee_filter:
            continue

        # ACTIVITY POINTS FILTER
        if points_filter != "All" and event_points != points_filter:
            continue

        # EVENT CARD
        with st.container(border=True):
            col1, col2 = st.columns([1.2, 4])

            # Event Poster
            with col1:
                if e[6]:
                    st.image(e[6], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/150", use_container_width=True)

            # Event Details
            with col2:
                st.subheader(e[2])
                st.write(f"📅 {e[3]} | ⏰ {e[4]}")
                st.write(f"📍 {e[5]}")
                st.write(f"🏷 {e[10]} | {e[8]} | {e[12]} pts")

                if st.button("View Event", key=f"view_{e[0]}"):
                    st.session_state.selected_event = e
                    st.session_state.page = "event_page"
                    st.rerun()


    

    

# ==================================================
# EVENT PAGE
# ==================================================
def event_page():
    # -------- BACK BUTTON (TOP) --------
    if st.button("⬅ Back"):
        st.session_state.page = (
            "organiser_dashboard"
            if st.session_state.role == "organiser"
            else "participant_dashboard"
        )
        st.rerun()

    e = st.session_state.selected_event


    organiser = get_organiser_details(e[1])

    # -------- ORGANISER HEADER --------
    col1, col2 = st.columns([1.2, 4])

    with col1:
        if organiser and organiser[2]:
            st.image(organiser[2], use_container_width=True)
        else:
            st.image("https://via.placeholder.com/120", use_container_width=True)

    with col2:
        st.markdown(f"### {e[1]}")  # Club name
        if organiser:
            st.markdown(
                f"<span style='color:gray'>{organiser[0]}</span>",
                unsafe_allow_html=True
            )
            st.write(organiser[1])

    st.markdown("---")

    

    # -------- EVENT SECTION (DETAILS LEFT, POSTER RIGHT) --------
    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Event Name (bigger & bold)
        st.markdown(
            f"<h1 style='font-size:36px'>{e[2]}</h1>",
            unsafe_allow_html=True
        )

        # Date, Time, Venue (bigger)
        st.markdown(
            f"""
            <p style='font-size:18px'>
            📅 <b>{e[3]}</b> &nbsp;&nbsp;
            ⏰ <b>{e[4]}</b><br>
            📍 <b>{e[5]}</b>
            </p>
            """,
            unsafe_allow_html=True
        )

        # Description (readable)
        st.markdown(
            f"<p style='font-size:18px'>{e[7]}</p>",
            unsafe_allow_html=True
        )

        # Tags
        st.markdown(
            f"""
            <p style='font-size:16px'>
            <b>Level:</b> {e[10]}<br>
            <b>Topics:</b> {e[11]}<br>
            <b>Fees:</b> {e[8]}<br>
            <b>Activity Points:</b> {e[12]}
            </p>
            """,
            unsafe_allow_html=True
        )

        st.link_button("🔗 Register Now", e[9])

    with col_right:
        if e[6]:
            st.image(e[6], use_container_width=True)
        else:
            st.image("https://via.placeholder.com/400x500", use_container_width=True)



# ==================================================
# PAGE ROUTER
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
