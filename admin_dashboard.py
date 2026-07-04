import streamlit as st
from database import cursor, conn


def show_admin_dashboard():
    st.title("Admin Dashboard")

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM history")
    total_images = cursor.fetchone()[0]

    cursor.execute(
        "SELECT username, COUNT(*) FROM history GROUP BY username ORDER BY COUNT(*) DESC"
    )
    user_activity = cursor.fetchall()

    cursor.execute(
        "SELECT prompt, COUNT(*) as cnt FROM history GROUP BY prompt ORDER BY cnt DESC LIMIT 10"
    )
    top_prompts = cursor.fetchall()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Users", total_users)
    with col2:
        st.metric("Total Images Generated", total_images)

    st.subheader("User Activity")
    if user_activity:
        for username, count in user_activity:
            st.write(f"- **{username}** generated **{count}** image(s)")
    else:
        st.info("No image generation history available yet.")

    st.subheader("Top Prompts")
    if top_prompts:
        for prompt, count in top_prompts:
            st.write(f"- **{prompt}** used **{count}** time(s)")
    else:
        st.info("No prompt history available yet.")

    st.subheader("Manage Users")
    cursor.execute(
        "SELECT users.username, IFNULL(COUNT(history.id), 0) as generated_images "
        "FROM users LEFT JOIN history ON users.username = history.username "
        "GROUP BY users.username ORDER BY generated_images DESC"
    )
    users = cursor.fetchall()

    if not users:
        st.info("No registered users found.")
        return

    st.dataframe(
        [
            {
                "Username": row[0],
                "Images Generated": row[1],
            }
            for row in users
        ],
        use_container_width=True,
    )

    usernames = [row[0] for row in users]
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
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (new_password, selected_username),
            )
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

    st.subheader("Recent Generation History")
    cursor.execute(
        "SELECT username, prompt, image_path, created_at FROM history ORDER BY created_at DESC LIMIT 20"
    )
    recent_history = cursor.fetchall()

    if recent_history:
        st.dataframe(
            [
                {
                    "Username": row[0],
                    "Prompt": row[1],
                    "Image Path": row[2],
                    "Created At": row[3],
                }
                for row in recent_history
            ],
            use_container_width=True,
        )
    else:
        st.info("No recent history records to display.")