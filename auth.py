from database import conn, cursor

def signup(username, password):
    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )
        conn.commit()
        return True
    except:
        return False

def login(username, password):  
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()

    if user:
        return True

    return False