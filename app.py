import os
from flask import Flask, render_template, send_from_directory, url_for, g
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)

# Define the directory where PDF files are stored
PDF_DIR = 'pdfs'

# Define the name of the SQLite database file
DB_FILENAME = 'pdfs.db'

# Define the full path to the database file
DB_PATH = os.path.join(app.root_path, DB_FILENAME)

# Define the database schema
SCHEMA = '''
CREATE TABLE IF NOT EXISTS pdf_files (
    id INTEGER PRIMARY KEY,
    filename TEXT UNIQUE,
    filepath TEXT
);
'''

# Create a connection to the database
conn = sqlite3.connect(DB_PATH)

# Create the pdf_files table if it doesn't already exist
with conn:
    conn.execute(SCHEMA)

# Add all PDF files to the database
for filename in os.listdir(PDF_DIR):
    if filename.endswith('.pdf'):
        filepath = os.path.join(PDF_DIR, filename)
        securefilename = secure_filename(filename)
        with conn:
            conn.execute('INSERT OR IGNORE INTO pdf_files (filename, filepath) VALUES (?, ?);', (securefilename, filepath))

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('pdfs.db')
    return g.db

# Define the route for serving PDF files
@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

@app.route('/')
def index():
    return render_template('index.html')

# Define the route for the PDF list page

@app.route('/pdfs')
def pdfs():
    conn = get_db()
    pdf_files = conn.execute('SELECT filename, filepath FROM pdf_files').fetchall()
    return render_template('pdfs.html', pdf_files=pdf_files)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run()
