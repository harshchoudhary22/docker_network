import time
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# Retry connection (important for Docker startup delay)
def get_db():
    for i in range(5):
        try:
            conn = mysql.connector.connect(
                host="mysql",   # Docker service name
                user="root",
                password="root",
                database="testdb"
            )
            return conn
        except Exception as e:
            print("DB not ready, retrying...", e)
            time.sleep(5)
    raise Exception("Database connection failed")

# Create table if not exists
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

# Initialize DB at startup
init_db()

# Home route
@app.route("/")
def home():
    return "Python + MySQL Docker App Running 🚀"

# Add user
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

# Get all users
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

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)