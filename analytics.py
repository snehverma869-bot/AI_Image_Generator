import streamlit as st
from database import cursor


def show_analytics():
    st.title("Analytics")

    cursor.execute("SELECT COUNT(*) FROM history")
    total_images = cursor.fetchone()[0]

    cursor.execute("SELECT username, COUNT(*) FROM history GROUP BY username ORDER BY COUNT(*) DESC")
    user_counts = cursor.fetchall()

    cursor.execute("SELECT prompt, COUNT(*) as cnt FROM history GROUP BY prompt ORDER BY cnt DESC LIMIT 5")
    top_prompts = cursor.fetchall()

    st.metric("Total Generated Images", total_images)

    st.subheader("Top Users")
    if user_counts:
        for username, count in user_counts:
            st.write(f"- **{username}**: {count}")
    else:
        st.info("No user history available yet.")

    st.subheader("Top Prompts")
    if top_prompts:
        for prompt, count in top_prompts:
            st.write(f"- **{prompt}**: {count}")
    else:
        st.info("No prompt data available yet.")
