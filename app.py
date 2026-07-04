import os
import sys
import zipfile
import random

# Ensure local module imports work when Streamlit runs the script from the workspace root.
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from auth import signup, login
from database import conn, cursor, DB_PATH
from image_generator import generate_image, generate_image_from_image, reset_pipeline
from prompt_enhancer import enhance_prompt
from background_remover import remove_background
from gallery import show_gallery
from analytics import show_analytics
from chat_assistant import get_assistant_response


def send_assistant_request(question, history_messages=None):
    try:
        if history_messages is None:
            return get_assistant_response(question)
        return get_assistant_response(question, history_messages)
    except TypeError:
        try:
            return get_assistant_response(question, history=history_messages)
        except TypeError:
            return get_assistant_response(question)


def shorten_prompt(prompt, max_length=60):
    prompt = prompt.strip()
    if len(prompt) <= max_length:
        return prompt
    truncated = prompt[:max_length].rsplit(' ', 1)[0]
    return truncated + '...'


st.set_page_config(
    page_title="Promptify AI",
    page_icon="🎨",
    layout="wide",
)

# Styles
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: radial-gradient(circle at top left, rgba(59,130,246,0.15), transparent 18%),
                    radial-gradient(circle at bottom right, rgba(236,72,153,0.14), transparent 20%),
                    linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        color: #0f172a;
    }

    .block-container {
        padding: 32px 30px 40px !important;
        max-width: 1360px;
        margin: auto;
        background: transparent;
    }

    .stSidebar .css-1d391kg,
    .sidebar .css-1d391kg {
        background: linear-gradient(180deg, #ffffff, #eef2ff);
        border-radius: 30px;
        padding: 24px 22px 30px;
        border: 1px solid rgba(99,102,241,0.16);
        box-shadow: 0 25px 80px rgba(99,102,241,0.08);
    }

    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        gap: 16px;
        margin-bottom: 22px;
    }

    .nav-search {
        flex: 1;
        min-width: 220px;
        display: flex;
        align-items: center;
        padding: 14px 18px;
        border-radius: 22px;
        background: rgba(255,255,255,0.95);
        border: 1px solid rgba(99,102,241,0.16);
        box-shadow: 0 16px 35px rgba(99,102,241,0.08);
    }

    .nav-search input {
        width: 100%;
        border: none;
        outline: none;
        background: transparent;
        font-size: 0.96rem;
        color: #0f172a;
    }

    .nav-actions {
        display: flex;
        gap: 12px;
        align-items: center;
    }

    .nav-button {
        width: 50px;
        height: 50px;
        border-radius: 16px;
        background: rgba(255,255,255,0.95);
        border: 1px solid rgba(99,102,241,0.16);
        box-shadow: 0 18px 44px rgba(99,102,241,0.08);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        cursor: pointer;
    }

    .nav-avatar {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 12px 14px;
        border-radius: 22px;
        background: rgba(255,255,255,0.95);
        border: 1px solid rgba(99,102,241,0.16);
        box-shadow: 0 18px 44px rgba(99,102,241,0.08);
        color: #111827;
        font-weight: 700;
    }

    .notification-badge::after {
        display: none;
    }

    .hero-cta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 28px;
    }

    .cta-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 20px;
        padding: 16px 32px;
        font-size: 1rem;
        font-weight: 800;
        border: none;
        cursor: pointer;
        min-width: 160px;
    }

    .cta-button:first-child {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 55%, #ec4899 100%);
        color: white;
    }

    .cta-button:last-child {
        background: rgba(99,102,241,0.12);
        color: #111827;
    }

    .stat-card {
        background: rgba(255,255,255,0.92);
        border-radius: 26px;
        padding: 24px 22px;
        border: 1px solid rgba(99,102,241,0.14);
        box-shadow: 0 28px 86px rgba(99,102,241,0.08);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        margin-bottom: 24px;
    }

    .stat-card:hover {
        transform: translateY(-4px);
    }

    .stat-card-icon {
        width: 52px;
        height: 52px;
        border-radius: 18px;
        background: rgba(99,102,241,0.12);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 18px;
        font-size: 1.4rem;
        color: #4f46e5;
    }

    .stat-card-title {
        margin: 0;
        font-size: 0.98rem;
        color: #475569;
        font-weight: 600;
    }

    .stat-card-value {
        margin: 12px 0 0;
        font-size: 2rem;
        font-weight: 900;
        color: #111827;
    }

    .prompt-day-card,
    .trending-card,
    .upgrade-card {
        background: #ffffff;
        border-radius: 30px;
        border: 1px solid rgba(99,102,241,0.14);
        padding: 26px;
        box-shadow: 0 26px 90px rgba(99,102,241,0.08);
    }

    .trending-grid {
        display: grid;
        gap: 14px;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        margin-top: 16px;
    }

    .trending-pill {
        padding: 14px 16px;
        border-radius: 18px;
        background: rgba(99,102,241,0.08);
        color: #1e293b;
        font-weight: 700;
        text-align: center;
    }

    .floating-blobs {
        position: absolute;
        inset: 0;
        pointer-events: none;
        z-index: 0;
    }

    .blob {
        position: absolute;
        border-radius: 50%;
        filter: blur(90px);
        opacity: 0.45;
    }

    .blob-1 { width: 320px; height: 320px; background: rgba(56,189,248,0.25); top: -100px; left: -60px; }
    .blob-2 { width: 260px; height: 260px; background: rgba(236,72,153,0.22); bottom: -90px; right: 40px; }
    .blob-3 { width: 180px; height: 180px; background: rgba(99,102,241,0.2); top: 180px; right: 120px; }

    .grid-gallery {
        display: grid;
        gap: 18px;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        margin-top: 18px;
    }

    .gallery-card-inner {
        border-radius: 26px;
        overflow: hidden;
        border: 1px solid rgba(99,102,241,0.14);
        background: #ffffff;
        box-shadow: 0 24px 90px rgba(99,102,241,0.08);
    }

    .gallery-card-inner img {
        width: 100%;
        display: block;
    }

    .gallery-card-caption {
        padding: 14px 14px 18px;
        color: #475569;
        font-size: 0.95rem;
    }

    .upgrade-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(99,102,241,0.12), rgba(236,72,153,0.06));
    }

    .upgrade-card::before {
        content: "";
        position: absolute;
        width: 160px;
        height: 160px;
        background: rgba(99,102,241,0.14);
        border-radius: 50%;
        top: -50px;
        right: -50px;
    }

    .upgrade-card .upgrade-badge {
        display: inline-flex;
        padding: 10px 14px;
        border-radius: 999px;
        background: rgba(236,72,153,0.14);
        color: #7c3aed;
        font-weight: 700;
        margin-bottom: 18px;
    }

    .upgrade-card strong {
        display: block;
        font-size: 1.35rem;
        color: #111827;
        margin-bottom: 10px;
    }

    .upgrade-card p {
        color: #475569;
        margin-bottom: 20px;
    }

    .footer-social {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-top: 40px;
        padding-top: 24px;
        border-top: 1px solid rgba(148,163,184,0.24);
        color: #64748b;
    }

    .footer-social a {
        color: #64748b;
        text-decoration: none;
        margin-right: 12px;
    }

    .footer-social a:hover {
        color: #111827;
    }

    .dark-switch {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 10px 16px;
        border-radius: 999px;
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(99,102,241,0.18);
        box-shadow: 0 20px 48px rgba(99,102,241,0.08);
    }

    .dark-switch input[type=checkbox] {
        width: 44px;
        height: 24px;
        -webkit-appearance: none;
        appearance: none;
        border-radius: 999px;
        background: #cbd5e1;
        position: relative;
        outline: none;
        cursor: pointer;
        transition: background 0.2s ease;
    }

    .dark-switch input[type=checkbox]::after {
        content: "";
        position: absolute;
        top: 3px;
        left: 4px;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: white;
        transition: transform 0.2s ease;
        box-shadow: 0 4px 10px rgba(15,23,42,0.12);
    }

    .dark-switch input[type=checkbox]:checked {
        background: linear-gradient(90deg, #6366f1, #ec4899);
    }

    .dark-switch input[type=checkbox]:checked::after {
        transform: translateX(20px);
    }

    .stSidebar .css-1d391kg .css-1v0mbdj.e16nr0p30,
    .sidebar .css-1d391kg .css-1v0mbdj.e16nr0p30 {
        background: transparent;
    }

    .sidebar .css-1d391kg .stTextInput>div>div>input,
    .sidebar .css-1d391kg .stTextArea>div>div>textarea,
    .sidebar .css-1d391kg .stSelectbox>div>div>div>div,
    .sidebar .css-1d391kg .stRadio>div>div {
        background: #ffffff;
        color: #111827;
        border: 1px solid rgba(99,102,241,0.18);
        border-radius: 18px;
    }

    .sidebar .css-1d391kg .stButton>button {
        width: 100%;
        min-height: 52px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 55%, #ec4899 100%) !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        padding: 14px 20px !important;
        font-weight: 700 !important;
        box-shadow: 0 20px 40px rgba(99,102,241,0.22);
    }

    .stSidebar .css-1d391kg .stRadio>div>div>label {
        font-weight: 700;
    }

    .hero-section {
        position: relative;
        padding: 32px 36px 34px;
        border-radius: 32px;
        background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(248,250,252,0.72));
        border: 1px solid rgba(99,102,241,0.14);
        box-shadow: 0 40px 120px rgba(99,102,241,0.08);
        overflow: hidden;
    }

    .hero-section::before {
        content: "";
        position: absolute;
        top: -60px;
        right: -30px;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: rgba(99,102,241,0.18);
        filter: blur(36px);
    }

    .hero-section::after {
        content: "";
        position: absolute;
        bottom: -50px;
        left: -30px;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: rgba(236,72,153,0.16);
        filter: blur(36px);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 14px 22px;
        border-radius: 999px;
        font-size: 0.95rem;
        font-weight: 700;
        color: #111827;
        background: rgba(99,102,241,0.12);
        border: 1px solid rgba(99,102,241,0.16);
        margin-bottom: 22px;
        z-index: 1;
        position: relative;
    }

    .hero-title {
        font-size: clamp(3rem, 4.6vw, 4.6rem);
        margin: 0;
        font-weight: 900;
        line-height: 1;
        color: #111827;
        z-index: 1;
        position: relative;
    }

    .hero-title span {
        background: linear-gradient(90deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        margin-top: 18px;
        font-size: 1.05rem;
        color: #475569;
        max-width: 680px;
        line-height: 1.75;
        z-index: 1;
        position: relative;
    }

    .hero-visual img {
        border-radius: 30px;
        border: 1px solid rgba(99,102,241,0.16);
        box-shadow: 0 28px 80px rgba(99,102,241,0.14);
    }

    .feature-card {
        background: #ffffff;
        border-radius: 30px;
        padding: 28px 24px;
        border: 1px solid rgba(99,102,241,0.14);
        box-shadow: 0 28px 80px rgba(99,102,241,0.08);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        margin-bottom: 24px;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 36px 100px rgba(99,102,241,0.14);
    }

    .feature-card strong {
        display: block;
        font-size: 1.1rem;
        margin-bottom: 12px;
        color: #111827;
    }

    .feature-card div {
        color: #475569;
        line-height: 1.75;
    }

    .recent-panel {
        background: #ffffff;
        border-radius: 28px;
        padding: 20px;
        border: 1px solid rgba(99,102,241,0.12);
        box-shadow: 0 24px 90px rgba(99,102,241,0.08);
    }

    .recent-panel h3 {
        margin-top: 0;
        color: #111827;
    }

    .recent-panel .stButton>button {
        min-width: 120px !important;
        padding: 10px 18px !important;
        font-size: 0.95rem !important;
        margin-top: 14px !important;
    }

    .recent-panel img {
        border-radius: 20px;
        box-shadow: 0 24px 60px rgba(99,102,241,0.08);
    }

    .recent-panel .stCaption {
        color: #64748b;
    }

    .stMarkdown p,
    .stText {
        color: #475569;
    }

    div.stButton > button,
    .stDownloadButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 45%, #ec4899 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 16px 36px !important;
        min-height: 54px !important;
        border-radius: 22px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        box-shadow: 0 24px 70px rgba(99,102,241,0.22);
        transition: transform 0.22s ease, box-shadow 0.22s ease, opacity 0.22s ease;
    }

    div.stButton > button:hover,
    .stDownloadButton>button:hover {
        transform: translateY(-1px);
        opacity: 0.98;
    }

    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div>div,
    .stRadio>div>div {
        border-radius: 18px !important;
        border: 1px solid rgba(99,102,241,0.18) !important;
        background: #ffffff !important;
    }

    .footer, .css-18e3th9, .css-1y0tads {
        background: transparent !important;
    }

    .sidebar .css-1d391kg .stSidebarHeader,
    .sidebar .css-1d391kg .stRadio>div>div>label {
        color: #111827 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
 

# Session defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "admin_username" not in st.session_state:
    st.session_state.admin_username = ""
if "assistant_history" not in st.session_state:
    st.session_state.assistant_history = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        .stApp { background: #020617 !important; color: #e2e8f0 !important; }
        .main-content, .feature-card, .right-panel, .stSidebar .css-1d391kg { background: rgba(15,23,42,0.92) !important; border-color: rgba(148,163,184,0.18) !important; color: #e2e8f0 !important; }
        .stTextArea textarea, .stTextInput>div>div>input, .stSelectbox>div>div, .stRadio>div>div { background: #0f172a !important; color: #e2e8f0 !important; border-color: rgba(148,163,184,0.3) !important; }
        .feature-card, .gallery-card, .prompt-card { box-shadow: 0 24px 80px rgba(0,0,0,0.45) !important; }
        .stButton>button, .stDownloadButton>button { box-shadow: 0 24px 80px rgba(99,102,241,0.22) !important; }
        .stMarkdown p { color: #cbd5e1 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Login / Signup / Admin Login
if not st.session_state.logged_in and not st.session_state.admin_logged_in:
    st.title("Promptify AI")
    menu = st.selectbox("Select", ["Login", "Signup", "Admin Login"]) 

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Signup":
        if st.button("Create Account"):
            if signup(username, password):
                st.success("Account Created Successfully")
            else:
                st.error("Username Already Exists")

    elif menu == "Login":
        if st.button("Login"):
            if login(username, password):
                if username == "admin":
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    
                st.rerun()
            else:
                st.error("Invalid Credentials")

    elif menu == "Admin Login":
        if st.button("Login as Admin"):
            if username == "admin" and login(username, password):
                st.session_state.admin_logged_in = True
                st.session_state.admin_username = username
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.rerun()
            else:
                st.error("Invalid Admin Credentials")

# Admin dashboard
elif st.session_state.admin_logged_in:
    st.sidebar.title("Admin Panel")
    st.sidebar.markdown(f"**DB:** `{DB_PATH}`")
    st.sidebar.markdown(f"**admin_logged_in:** `{st.session_state.admin_logged_in}`")
    st.sidebar.markdown(f"**admin_username:** `{st.session_state.admin_username}`")

    admin_nav = st.sidebar.radio("Admin", ["Overview", "Analytics", "Manage Users"])    

    if st.sidebar.button("Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.admin_username = ""
        st.rerun()

    if admin_nav == "Analytics":
        st.title("Admin Analytics")
        show_analytics()

    elif admin_nav == "Overview":
        st.title("Admin Dashboard")

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM history")
        total_images = cursor.fetchone()[0]

        cursor.execute(
            "SELECT users.username, IFNULL(COUNT(history.id), 0) as generated_images "
            "FROM users LEFT JOIN history ON users.username = history.username "
            "GROUP BY users.username ORDER BY generated_images DESC"
        )
        user_activity = cursor.fetchall()

        cursor.execute(
            "SELECT prompt, COUNT(*) as cnt FROM history GROUP BY prompt ORDER BY cnt DESC LIMIT 10"
        )
        top_prompts = cursor.fetchall()

        left_spacer, content_col, right_spacer = st.columns([1, 4, 1])
        with content_col:
            st.subheader("Recent Generations")
            btn_left, btn_center, btn_right = st.columns([1, 2, 1])
            with btn_center:
                if st.button("View all", key="view_all_recent"):
                    st.info("Open Gallery to view all generated images.")

            cursor.execute("SELECT image_path, prompt, created_at FROM history WHERE username = ? ORDER BY created_at DESC LIMIT 6", (st.session_state.get("username") or "unknown",))
            recent = cursor.fetchall()
            if recent:
                for r in recent:
                    path = r[0]
                    p = r[1]
                    created = r[2] if len(r) > 2 else ""
                    if os.path.exists(path):
                        col_img, col_meta, col_dl = st.columns([1,4,1])
                        with col_img:
                            st.image(path, width=100)
                        with col_meta:
                            st.markdown(f"<div style='font-weight:700;margin-bottom:6px'>{p}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div style='color:#64748b;font-size:0.85rem'>{created}</div>", unsafe_allow_html=True)
                        with col_dl:
                            try:
                                with open(path, "rb") as fh:
                                    btn_key = f"dl_{os.path.basename(path)}"
                                    st.download_button("", fh, file_name=os.path.basename(path), key=btn_key, help="Download image")
                            except Exception:
                                st.button("Download", key=f"dl_fallback_{os.path.basename(path)}")
                        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            else:
                st.info("No images yet\nYour generated images will appear here")

        # st.markdown("---")
        # st.subheader("Popular Ideas")

        st.markdown("---")
        st.subheader("Recent Generation History")
        cursor.execute("SELECT username, prompt, image_path, created_at FROM history ORDER BY created_at DESC LIMIT 20")
        recent_history = cursor.fetchall()
        if recent_history:
            st.dataframe([
                {"Username": row[0], "Prompt": row[1], "Image Path": row[2], "Created At": row[3]} for row in recent_history
            ], use_container_width=True)
        else:
            st.info("No recent history records to display.")

    else:
        # Manage Users
        st.title("Manage Users")
        cursor.execute("SELECT id, username FROM users ORDER BY username")
        users = cursor.fetchall()

        if not users:
            st.info("No registered users found.")
        else:
            user_table = [{"Username": row[1]} for row in users]
            st.dataframe(user_table, use_container_width=True)

            usernames = [row[1] for row in users]
            selected_username = st.selectbox("Select a user to manage", usernames)

            new_password = st.text_input("New password", type="password")
            update_password = st.button("Update Password")
            delete_user = st.button("Delete User")
            clear_history = st.button("Clear User History")

            if update_password:
                if selected_username == "admin":
                    st.error("Cannot change admin password here.")
                elif not new_password:
                    st.warning("Enter a new password before updating.")
                else:
                    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, selected_username))
                    conn.commit()
                    st.success(f"Password updated for {selected_username}.")

            if delete_user:
                if selected_username == "admin":
                    st.error("Admin account cannot be deleted.")
                else:
                    cursor.execute("DELETE FROM users WHERE username = ?", (selected_username,))
                    cursor.execute("DELETE FROM history WHERE username = ?", (selected_username,))
                    conn.commit()
                    st.success(f"Deleted user {selected_username} and their history.")

            if clear_history:
                cursor.execute("DELETE FROM history WHERE username = ?", (selected_username,))
                conn.commit()
                st.success(f"Cleared history for {selected_username}.")

# Regular user
else:
    dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=st.session_state.get("dark_mode", False), key="dark_mode")
    if "page_select" not in st.session_state:
        st.session_state.page_select = "Generate Image"
    if st.session_state.get("navigate_to_gallery", False):
        st.session_state.page_select = "Gallery"
        st.session_state.navigate_to_gallery = False
    navigation_items = ["Generate Image", "Gallery", "Background Remover", "Chat Assistant"]
    page = st.sidebar.radio("Navigation", navigation_items, key="page_select")

    # Generate Image page
    if page == "Generate Image":
        # Main layout: wider main column + right sidebar
        main, right = st.columns([6, 4])

        with main:
            st.markdown(
                """
                <div class='floating-blobs'>
                    <div class='blob blob-1'></div>
                    <div class='blob blob-2'></div>
                    <div class='blob blob-3'></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            nav_left, nav_right = st.columns([4, 2])
            # with nav_left:
            #     st.text_input("", placeholder="Search prompts, styles, gallery...", key="top_search")
            with nav_right:
                st.markdown(
                    f"""
                    <div class='top-navbar'>
                        <div class='nav-actions'>
                            <div class='nav-button notification-badge'>🔔</div>
                            <div class='nav-avatar'>
                                <span>👋</span>
                                <span>Hi, {st.session_state.get('username', 'User')}</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with main:
            left_hero, right_hero = st.columns([2, 1])
            with left_hero:
                st.markdown(
                    '''
                    <div class="hero-section">
                        <div class="hero-badge">✨ AI Powered Creativity</div>
                        <h1 class="hero-title">Create Stunning<br><span>Visuals</span> with AI</h1>
                        <p class="hero-subtitle">Generate professional-quality images from simple text prompts. Smart style presets, lightning-fast generation and pro results.</p>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                hero_cta_left, _, hero_cta_right = st.columns([1, 0.15, 1])
                hero_generate = hero_cta_left.button("Generate Now", key="hero_generate")
                hero_explore = hero_cta_right.button("Explore Gallery", key="hero_explore")
                if hero_explore:
                    st.session_state.navigate_to_gallery = True
                    st.rerun()
                if hero_generate:
                    st.session_state.generate_now = True
                    st.rerun()
            with right_hero:
                asset_root = os.path.join(os.path.dirname(__file__), "assets")
                robot_path = os.path.join(asset_root, "robottt.png")
                robot_fallback = os.path.join(asset_root, "robot.png")
                if os.path.exists(robot_path):
                    st.image(robot_path, width=380)
                elif os.path.exists(robot_fallback):
                    st.image(robot_fallback, width=380)
                # else:
                #     st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=760&q=80", width=380)

            # Hero stats
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown("""
                <div class='stat-card'>
                    <div class='stat-card-icon'>📸</div>
                    <div class='stat-card-title'>Images Generated</div>
                    <div class='stat-card-value'>50K+</div>
                </div>
            """, unsafe_allow_html=True)
            c2.markdown("""
                <div class='stat-card'>
                    <div class='stat-card-icon'>😊</div>
                    <div class='stat-card-title'>Happy Users</div>
                    <div class='stat-card-value'>10K+</div>
                </div>
            """, unsafe_allow_html=True)
            c3.markdown("""
                <div class='stat-card'>
                    <div class='stat-card-icon'>⚡</div>
                    <div class='stat-card-title'>Uptime</div>
                    <div class='stat-card-value'>99.9%</div>
                </div>
            """, unsafe_allow_html=True)
            c4.markdown("""
                <div class='stat-card'>
                    <div class='stat-card-icon'>⭐</div>
                    <div class='stat-card-title'>Rating</div>
                    <div class='stat-card-value'>4.9★</div>
                </div>
            """, unsafe_allow_html=True)

        # with main:
        #     st.markdown(
        #         """
        #         # <div class='prompt-day-card'>
        #         #     <h4>Prompt of the Day</h4>
        #         #     <p>“A futuristic creative studio with neon lighting, floating holographic interfaces, and an AI design assistant at work.”</p>
        #         # </div>
        #         # """,
        #         unsafe_allow_html=True,
        #     )

            # st.markdown(
            #     """
            #     <div class='trending-card'>
            #         <h4>Trending Styles</h4>
            #         <div class='trending-grid'>
            #             <div class='trending-pill'>Realistic</div>
            #             <div class='trending-pill'>Digital Art</div>
            #             <div class='trending-pill'>Cinematic</div>
            #             <div class='trending-pill'>Anime</div>
            #             <div class='trending-pill'>Fantasy</div>
            #             <div class='trending-pill'>3D Render</div>
            #         </div>
            #     </div>
            #     """,
            #     unsafe_allow_html=True,
            # )

            # st.markdown("<h4 style='margin-top: 32px; color: #111827;'>Usage Analytics</h4>", unsafe_allow_html=True)
            # st.line_chart({"Generations": [120, 180, 150, 220, 195, 240, 270]})

        with main:
            f1, f2, f3 = st.columns(3)
            f1.markdown("<div class='feature-card'><strong>High Quality</strong><div style='opacity:0.8;margin-top:6px'>Generate high-resolution images with stunning detail.</div></div>", unsafe_allow_html=True)
            f2.markdown("<div class='feature-card'><strong>Fast & Smart</strong><div style='opacity:0.8;margin-top:6px'>Optimized pipelines for quick results.</div></div>", unsafe_allow_html=True)
            f3.markdown("<div class='feature-card'><strong>Easy to Use</strong><div style='opacity:0.8;margin-top:6px'>Simple, intuitive interface for everyone.</div></div>", unsafe_allow_html=True)

        with main:
            # st.markdown("<div class='prompt-card'>", unsafe_allow_html=True)
            mode = st.selectbox("Mode", ["Text Only", "Image to Image"], index=0)

            prompt = st.text_area("Describe the image you want to generate...", height=160, placeholder="Example: A futuristic city at sunset with flying cars and neon lights...", key="prompt_input")

            def set_prompt_input(value):
                st.session_state.prompt_input = value

            st.markdown("### Popular Prompt Ideas")
            suggestions = ["Cyberpunk City", "Anime Girl", "Luxury Car", "Fantasy Castle", "Realistic Portrait"]
            cols = st.columns(len(suggestions))
            for c, text in zip(cols, suggestions):
                c.button(text, key=f"suggest_{text}", on_click=set_prompt_input, args=(text,))

            uploaded_img = None
            img_strength = 0.75
            if mode == "Image to Image":
                uploaded_file = st.file_uploader("Upload source image", type=["png","jpg","jpeg"], key="img2img_upload")
                if uploaded_file:
                    os.makedirs("uploads", exist_ok=True)
                    upload_path = os.path.join("uploads", uploaded_file.name)
                    with open(upload_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    uploaded_img = upload_path
                    st.image(uploaded_img, width=300)
                img_strength = st.slider("Strength (preserve vs transform)", 0.0, 1.0, 0.75)

            col_ar, col_style, col_quality = st.columns([1,1,1])
            with col_ar:
                aspect = st.selectbox("Aspect Ratio", ["1:1 (Square)", "16:9 (Landscape)", "9:16 (Portrait)"], index=1)
            with col_style:
                style = st.selectbox("Style", ["Realistic", "Digital Art", "Cartoon", "Cinematic"], index=0)
            with col_quality:
                quality = st.selectbox("Quality", ["Low", "Medium", "High"], index=2)

            # Surprise me
            examples = [
                "A serene mountain lake at sunrise with mist",
                "Cyberpunk street market lit by neon signs",
                "Fantasy castle floating among the clouds",
                "Portrait of an astronaut with watercolor style",
            ]

            def _set_prompt(val):
                st.session_state.prompt_input = val

            # st.button("Surprise Me", on_click=lambda: _set_prompt(random.choice(examples)))

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            generate_clicked = st.button("Generate Image", key="gen_large")
            generate_triggered = generate_clicked or st.session_state.pop("generate_now", False)
            if generate_triggered:
                if not prompt or not prompt.strip():
                    st.warning("Please enter a prompt before generating an image.")
                else:
                    trimmed_prompt = prompt
                    if len(prompt.strip()) > 220:
                        st.warning("Prompt is very long. Trimming it slightly for more reliable generation.")
                        trimmed_prompt = prompt.strip()[:220].rsplit(' ', 1)[0]
                    enhanced_prompt = enhance_prompt(trimmed_prompt)
                    status_placeholder = st.empty()
                    status_placeholder.info("Preparing your image... this may take a moment.")

                    try:
                        with status_placeholder.container():
                            with st.spinner("Loading model and generating image..."):
                                username = st.session_state.get("username")
                                output_dir = os.path.join("generated_images", username or "unknown")
                                os.makedirs(output_dir, exist_ok=True)
                                if mode == "Text Only":
                                    image_path = generate_image(enhanced_prompt, output_dir=output_dir)
                                else:
                                    if not uploaded_img:
                                        st.warning("Please upload a source image for Image-to-Image mode.")
                                        image_path = None
                                    else:
                                        image_path = generate_image_from_image(
                                            uploaded_img,
                                            enhanced_prompt,
                                            strength=img_strength,
                                            width=768,
                                            height=768,
                                            output_dir=output_dir,
                                        )

                        if image_path and os.path.exists(image_path):
                            status_placeholder.success("Image Generated")
                            st.image(image_path, width=700)
                            try:
                                cursor.execute("INSERT INTO history(username, prompt, image_path) VALUES (?, ?, ?)", (st.session_state.get("username") or "unknown", enhanced_prompt, image_path))
                                conn.commit()
                            except Exception as db_exc:
                                st.error(f"Failed to save history: {db_exc}")

                            with open(image_path, "rb") as f:
                                st.download_button("Download Image", f, file_name=os.path.basename(image_path), mime="image/png")
                        else:
                            st.error("Image generation failed.")
                    except Exception as exc:
                        st.error(f"Image generation failed: {exc}")

        with right:
            st.markdown(
                """
                <div class='recent-panel'>
                    <h3 style='margin-top:2'>Recent Generations</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            spacer, btn_col = st.columns([1, 2])
            with spacer:
                st.write("")
            with btn_col:
                if st.button("View all", key="view_all_recent_right"):
                    st.session_state.navigate_to_gallery = True
                    st.rerun()

            cursor.execute("SELECT image_path, prompt, created_at FROM history WHERE username = ? ORDER BY created_at DESC LIMIT 6", (st.session_state.get("username") or "unknown",))
            recent = cursor.fetchall()

            if recent:
                cols = st.columns(2)
                for idx, r in enumerate(recent):
                    path = r[0]
                    prompt_text = r[1]
                    if os.path.exists(path):
                        col = cols[idx % 2]
                        col.image(path, width=160)
                        col.caption(shorten_prompt(prompt_text, max_length=55))
            else:
                st.info("No images yet\nYour generated images will appear here")

            st.markdown('---')
            st.markdown(
                """
                <div class='upgrade-card'>
                    <span class='upgrade-badge'>Upgrade to Pro</span>
                    <strong>Unlock premium styles</strong>
                    <p>Get faster generations, exclusive image formats, more daily credits, and ad-free workflow.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Upgrade Now", key="upgrade_now"):
                st.success("Upgrade to Pro is coming soon! Stay tuned.")

            # st.markdown(
            #     """
            #     # <div class='footer-social'>
            #     #     <div>Connect with us:</div>
            #     #     <div>
            #     #         <a href='#'>🐦 Twitter</a>
            #     #         <a href='#'>📸 Instagram</a>
            #     #         <a href='#'>💼 LinkedIn</a>
            #     #     </div>
            #     # </div>
            #     """,
            #     unsafe_allow_html=True,
            # )

    # Gallery
    elif page == "Gallery":
        show_gallery()
        if st.button("Download ZIP"):
            zip_name = "images.zip"
            with zipfile.ZipFile(zip_name, "w") as zipf:
                username = st.session_state.get("username")
                user_folder = os.path.join("generated_images", username or "unknown")
                for root, dirs, files in os.walk(user_folder):
                    for file in files:
                        zipf.write(os.path.join(root, file))
            with open(zip_name, "rb") as f:
                st.download_button("Download All Images", f, zip_name)

    # Background Remover
    elif page == "Background Remover":
        st.title("Background Remover")
        uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])
        if uploaded_file:
            os.makedirs("uploads", exist_ok=True)
            filepath = os.path.join("uploads", uploaded_file.name)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            try:
                output_path = remove_background(filepath)
                st.image(output_path, width=700)
            except Exception as exc:
                st.error(f"Background removal failed: {exc}")

    # Chat Assistant
    elif page == "Chat Assistant":
        st.title("🤖 Chat Assistant")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if not st.session_state.messages:
            st.info("Start the chat below — your conversation history will appear here.")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("Type your message...")

        if prompt:
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
            })

            history_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]

            with st.spinner("Thinking..."):
                answer = get_assistant_response(prompt, history_messages)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )
                st.rerun()

        if st.button("🗑 Clear Chat"):
            st.session_state.messages = []
            st.rerun()
           
    #     for m in st.session_state.messages[:-1]:
    #         history_messages.append(
    #             {
    #                 "role": m["role"],
    #                 "content": m["content"]
    #             }
    #         )

    #     with st.spinner("Thinking..."):
    #         answer = get_assistant_response(
    #             prompt,
    #             history_messages
    #         )

    #     st.session_state.messages.append(
    #         {
    #             "role": "assistant",
    #             "content": answer
    #         }
    #     )

    #     st.rerun()

    # st.markdown("---")

    # if st.button("🗑 Clear Chat"):
    #     st.session_state.messages = []
    #     st.rerun()
    # elif page == "Chat Assistant":
    #     st.title("ChatGPT-style Assistant")
    #     st.markdown(
    #         "Ask anything about image prompts, AI features, or creative ideas, and get instant help."
    #     )
    #     # st.markdown('<div class="main-content">', unsafe_allow_html=True)

    #     question = st.text_area("Ask your question here...", height=140, key="assistant_question")
    #     if st.button("Ask", key="ask_button"):
    #         if not question or not question.strip():
    #             st.warning("Please type a question to ask the assistant.")
    #         else:
    #             with st.spinner("Thinking..."):
    #                 history_messages = []
    #                 for q, a in st.session_state.assistant_history:
    #                     history_messages.append({"role": "user", "content": q})
    #                     history_messages.append({"role": "assistant", "content": a})

    #                 answer = send_assistant_request(question, history_messages)
    #                 history_list = st.session_state.assistant_history
    #                 history_list.append((question, answer))
    #                 st.session_state.assistant_history = history_list

    #     if st.session_state.assistant_history:
    #         st.markdown("---")
    #         st.subheader("Conversation")
    #         for q, a in reversed(st.session_state.assistant_history[-10:]):
    #             st.markdown(f"<div class='chat-bubble chat-user'><span class='chat-avatar'>You</span><div>{q}</div></div>", unsafe_allow_html=True)
    #             st.markdown(f"<div class='chat-bubble chat-assistant'><span class='chat-avatar'>Assistant</span><div>{a}</div></div>", unsafe_allow_html=True)
    #         if st.button("Clear Conversation", key="clear_assistant_history"):
    #             st.session_state.assistant_history = []

    #     st.markdown('</div>', unsafe_allow_html=True)

    # Logout button for users
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()