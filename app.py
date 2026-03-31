import time
import os
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# ✅ Get DB connection (works everywhere)
def get_db():
    host = os.getenv("DB_HOST", "localhost")  # dynamic host

    for i in range(5):
        try:
            conn = mysql.connector.connect(
                host=host,
                user="root",
                password="root",
                database="testdb"
            )
            return conn
        except Exception as e:
            print("DB not ready, retrying...", e)
            time.sleep(5)

    raise Exception("Database connection failed")

# ✅ Initialize database (create table)
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# Initialize DB when app starts
init_db()

# ✅ Home route
@app.route("/")
def home():
    return "Python + MySQL Docker App Running 🚀"

# ✅ Add user
@app.route("/add", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "User added successfully ✅"})

# ✅ Get users
@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    users = [{"id": row[0], "name": row[1]} for row in rows]
    return jsonify(users)

# ✅ Entry point
if __name__ == "__main__":
    # 👉 For CI/CD testing (GitHub Actions)
    if os.getenv("CI") == "true":
        print("Running in CI mode...")
        conn = get_db()
        print("Database connected successfully ✅")
    else:
        # 👉 For normal app run
        app.run(host="0.0.0.0", port=5000)
