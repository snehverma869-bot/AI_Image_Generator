import os
import streamlit as st
from database import cursor


def show_gallery():
    st.title("Gallery")

    username = None
    if st.session_state.get("logged_in"):
        username = st.session_state.get("username")
    elif st.session_state.get("admin_logged_in"):
        username = st.session_state.get("admin_username")

    if not username:
        st.info("Please log in to view your gallery.")
        return

    cursor.execute(
        "SELECT image_path FROM history WHERE username = ? ORDER BY created_at DESC",
        (username,)
    )
    rows = cursor.fetchall()
    image_paths = [row[0] for row in rows if row[0] and os.path.exists(row[0])]

    st.write(f"Viewing gallery for: {username}")
    st.write(f"Found history rows: {len(rows)}")
    st.write(f"Image paths used: {image_paths}")

    if not image_paths:
        st.info("No generated images found for your account. Create an image first.")
        return

    cols = st.columns(3)
    for idx, image_path in enumerate(image_paths):
        col = cols[idx % 3]
        with col:
            st.image(
                image_path,
                caption=os.path.basename(image_path),
                width='stretch'
            )
