from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from database import get_db
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def landing():
    return "<h1>AI Start Map</h1><p>Coming soon.</p>"


@app.route('/start')
def start_interview():
    return "<h1>Interview startet hier</h1>"


# CREATE - Neue Session anlegen
@app.route('/sessions', methods=['POST'])
def create_session():
    data = request.get_json()

    user_name = data.get('user_name')
    email = data.get('email')
    business_type = data.get('business_type')
    ai_experience_level = data.get('ai_experience_level')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sessions (user_name, email, business_type, ai_experience_level)
        VALUES (?, ?, ?, ?)
    """, (user_name, email, business_type, ai_experience_level))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'session_id': session_id,
        'message': 'Session erfolgreich erstellt'
    }), 201


# READ - Session laden
@app.route('/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()
    conn.close()

    if session is None:
        return jsonify({'error': 'Session nicht gefunden'}), 404

    return jsonify(dict(session)), 200


# DELETE - Session löschen
@app.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()

    if session is None:
        conn.close()
        return jsonify({'error': 'Session nicht gefunden'}), 404

    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Session {session_id} gelöscht'}), 200


if __name__ == '__main__':
    app.run(debug=True)