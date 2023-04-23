import os
import sqlite3
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'pdfs'
app.config['DATABASE'] = 'pdfs.db'

# Define the database schema and create a connection
def create_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pdf_files
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT NOT NULL,
                  path TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Add PDF files to the database
def add_pdf_files_to_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith('.pdf'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            secure_filename = filename.replace(' ', '_')
            c.execute("INSERT INTO pdf_files (filename, path) VALUES (?, ?)",
                      (secure_filename, filepath))
    conn.commit()
    conn.close()

# Retrieve PDF files from the database
def get_pdf_files_from_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("SELECT filename, path FROM pdf_files")
    pdf_files = c.fetchall()
    conn.close()
    return pdf_files

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdfs')
def pdfs():
    pdf_files = get_pdf_files_from_db()
    return render_template('pdfs.html', pdf_files=pdf_files)

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    create_db()
    add_pdf_files_to_db()
    app.run(debug=True)
