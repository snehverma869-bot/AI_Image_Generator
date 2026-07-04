import os
import shutil
import sqlite3

BASE = os.path.dirname(__file__)
SRC = os.path.join(BASE, "generated_images")
DST = os.path.join(SRC, "unknown")
DB = os.path.join(BASE, "users.db")

os.makedirs(DST, exist_ok=True)
conn = sqlite3.connect(DB)
cur = conn.cursor()
count = 0
for name in os.listdir(SRC):
    src_path = os.path.join(SRC, name)
    if os.path.isfile(src_path):
        dst_path = os.path.join(DST, name)
        print("Moving", src_path, "->", dst_path)
        shutil.move(src_path, dst_path)
        cur.execute("INSERT INTO history(username,prompt,image_path) VALUES (?,?,?)", ("unknown", "migrated", dst_path))
        count += 1
conn.commit()
conn.close()
print(f"Migrated {count} files into {DST}")
