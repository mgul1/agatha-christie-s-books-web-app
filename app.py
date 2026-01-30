import sqlite3
from flask import Flask, g, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", series = get_series(), type = get_type(), book = "none")

@app.route("/filter", methods=["POST"])
def filter():
    # get data from filter form
    series_req = request.form.get("series")
    type_req = request.form.get("type")
    reading_status_req = request.form.get("reading status")

    # sql command
    cmd = ""

    if series_req and type_req and reading_status_req is not None:
        cmd = f"SELECT id, title, read FROM Books WHERE series = '{series_req}' AND type = '{type_req}' AND read = '{reading_status_req}' ORDER BY first_published"
    elif series_req and type_req is not None:
        cmd = f"SELECT id, title, read FROM Books WHERE series = '{series_req}' AND type = '{type_req}' ORDER BY first_published"
    elif series_req and reading_status_req is not None:
        cmd = f"SELECT id, title, read FROM Books WHERE series = '{series_req}' AND read = '{reading_status_req}' ORDER BY first_published"
    elif type_req and reading_status_req is not None:
        cmd = f"SELECT id, title, read FROM Books WHERE type = '{type_req}' AND read = '{reading_status_req}' ORDER BY first_published"
    elif series_req is not None:
        cmd = f"SELECT id, title, read FROM Books WHERE series = '{series_req}' ORDER BY first_published"
    elif type_req is not None:
        cmd = f"SELECT id, title, read FROM Books WHERE type = '{type_req}' ORDER BY first_published"
    else:
        cmd = f"SELECT id, title, read FROM Books WHERE read = '{reading_status_req}' ORDER BY first_published"
    
    # fetch data from database
    book = get_book(cmd)
    
    # if no book found
    if not book:
        book = "invalid"

    return render_template("index.html", series = get_series(), type = get_type(), book = book)

@app.route("/update", methods=["POST"])
def update():
    book_id = request.form.get("book")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE Books SET read = 1 WHERE id = ?", (book_id,))
    db.commit()
    return render_template("index.html", series = get_series(), type = get_type(), book = "updated")

def get_series():
    db = get_db()
    cursor = db.cursor()
    data = cursor.execute("SELECT DISTINCT series FROM Books ORDER BY title DESC").fetchall()
    data = [str(row[0]) for row in data] 
    return data

def get_type():
    db = get_db()
    cursor = db.cursor()
    data = cursor.execute("SELECT DISTINCT type FROM Books").fetchall()
    data = [str(row[0]) for row in data] 
    return data

def get_book(cmd):
    db = get_db()
    cursor = db.cursor()
    data = cursor.execute(cmd).fetchall()
    return data

# connect to database
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("books.db")
    return db

# close connection to database
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

if __name__ in "__main__":
    app.run()