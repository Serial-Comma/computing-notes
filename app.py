import os
from flask import Flask, render_template, send_from_directory, url_for, g, request, redirect
from werkzeug.utils import secure_filename
import sqlite3
import datetime

app = Flask(__name__)

# Define the directory where PDF files are stored
PDF_DIR = './pdfs'
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

def custom_title(s):
    words = s.split(' ')
    title_words = [word.capitalize() if word.islower() else word for word in words]
    return ' '.join(title_words)

# Create a connection to the database
conn = sqlite3.connect(DB_PATH)

# Create the pdf_files table if it doesn't already exist
with conn:
    conn.execute(SCHEMA)
    conn.execute("CREATE TABLE IF NOT EXISTS visitor_count (count INT, month INT, year INT);")

# Add all PDF files to the database
for filename in os.listdir(PDF_DIR):
    if filename.endswith('.pdf'):
        filepath = os.path.join('', filename)
        securefilename = secure_filename(filename)
        clean_filename = os.path.splitext(securefilename)[0]  # Remove ".pdf" extension
        with conn:
            conn.execute('INSERT OR IGNORE INTO pdf_files (filename, filepath) VALUES (?, ?);', (clean_filename, filepath))


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

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
    return send_from_directory(PDF_DIR,filename)

@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year
    c.execute('SELECT count FROM visitor_count WHERE month = ? AND year = ?',(current_month, current_year))
    result = c.fetchone()
    if result:
        count = result[0]
    else:
        count = 0
        c.execute('INSERT INTO visitor_count VALUES(?, ?, ?)', (count, current_month, current_year))
    count +=1
    c.execute('UPDATE visitor_count SET count = ? WHERE month = ? AND year = ?',(count, current_month, current_year))
    conn.commit()
    conn.close()
    if count == 69:
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)
    count = ordinal(int(count))
    return render_template('index.html', count=count)

# Define the route for the PDF list page

@app.route('/pdfs')
def pdfs():
    if 'query' in request.args:
        query = request.args['query']
        if query == "69":
            return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)
        conn = get_db()
        pdf_files = conn.execute('SELECT filename, filepath FROM pdf_files WHERE filename LIKE ? ORDER BY filename ASC;', ('%' + query + '%', )).fetchall()
        clean_pdf_files = []
        for filename, filepath in pdf_files:
            clean_pdf_files.append((custom_title(filename.replace('_', ' '))[3:], filepath))
        if not clean_pdf_files:  # No results found
            return render_template('pdfs.html', pdf_files=None, no_results=True)
        return render_template('pdfs.html', pdf_files=clean_pdf_files)
    else:
        conn = get_db()
        pdf_files = conn.execute('SELECT filename, filepath FROM pdf_files ORDER BY filename ASC').fetchall()
        clean_pdf_files = []
        for filename, filepath in pdf_files:
            clean_pdf_files.append((custom_title(filename.replace('_', ' '))[3:], filepath))
        return render_template('pdfs.html', pdf_files=clean_pdf_files)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run()
