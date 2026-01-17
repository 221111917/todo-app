import os
import sqlite3
from datetime import datetime
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename  # Tambah untuk logging sederhana (demo monitoring)

app = Flask(__name__, template_folder='templates', static_folder='static')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfigurasi
DB_PATH = '/data/todos.db'
UPLOAD_FOLDER = '/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs('/data', exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS todos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  status TEXT DEFAULT 'undone',
                  photo TEXT,
                  created_at TEXT)''')
    conn.commit()
    conn.close()
    logging.info("Database initialized")

init_db()

# API Endpoints

@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM todos ORDER BY created_at DESC")
    todos = c.fetchall()
    conn.close()
    logging.info("Fetched todos")
    return jsonify([{
        'id': row[0],
        'title': row[1],
        'description': row[2],
        'status': row[3],
        'photo': row[4],
        'created_at': row[5]
    } for row in todos])

@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.form
    title = data.get('title')
    description = data.get('description')
    status = data.get('status', 'undone')
    photo = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            photo = filename
            logging.info(f"Uploaded photo: {filename}")
        else:
            logging.warning("Invalid file upload attempt")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO todos (title, description, status, photo, created_at) VALUES (?, ?, ?, ?, ?)",
              (title, description, status, photo, created_at))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    logging.info(f"Added todo ID: {new_id}")
    return jsonify({'id': new_id, 'message': 'Todo added'}), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def edit_todo(todo_id):
    data = request.form
    title = data.get('title')
    description = data.get('description')
    status = data.get('status')
    photo = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo = filename
            logging.info(f"Updated photo for ID {todo_id}: {filename}")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    updates = []
    params = []
    if title:
        updates.append("title = ?")
        params.append(title)
    if description:
        updates.append("description = ?")
        params.append(description)
    if status:
        updates.append("status = ?")
        params.append(status)
    if photo:
        updates.append("photo = ?")
        params.append(photo)
    if updates:
        params.append(todo_id)
        c.execute(f"UPDATE todos SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        logging.info(f"Updated todo ID: {todo_id}")
    conn.close()
    return jsonify({'message': 'Todo updated'})

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    logging.info(f"Deleted todo ID: {todo_id}")
    return jsonify({'message': 'Todo deleted'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        abort(404)

# Frontend Route
@app.route('/')
def index():
    logging.info("Accessed index page")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)