from flask import Flask, request, jsonify
import psycopg2
import os
from urllib.parse import urlparse

app = Flask(__name__)


# Подключение к БД
def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        url = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        return conn
    return None


# Создание таблицы при старте
def init_db():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()
        conn.close()


# Инициализируем БД при запуске
init_db()


@app.route('/')
def hello():
    return "Hello, Serverless! 🚀"


@app.route('/echo', methods=['POST'])
def echo():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "No JSON data provided"}), 400

        return jsonify({
            "status": "received",
            "you_sent": data,
            "length": len(str(data))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/save', methods=['POST'])
def save_message():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database not connected"}), 500

        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400

        message = data['message']

        with conn.cursor() as cur:
            cur.execute("INSERT INTO messages (content) VALUES (%s)", (message,))
        conn.commit()
        conn.close()

        return jsonify({"status": "saved", "message": message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/messages')
def get_messages():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database not connected"}), 500

        with conn.cursor() as cur:
            cur.execute("SELECT id, content, created_at FROM messages ORDER BY created_at DESC LIMIT 10")
            rows = cur.fetchall()

        conn.close()

        messages = []
        for row in rows:
            messages.append({
                "id": row[0],
                "text": row[1],
                "time": row[2].isoformat() if row[2] else None
            })

        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)