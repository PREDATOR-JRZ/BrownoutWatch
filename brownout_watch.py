from {
  "python.analysis.regenerateStdLibIndices": true
} import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "brownout_secret_key"

DB = "database/brownout_watch.db"

def get_db():
    return sqlite3.connect(DB)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid login"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT COUNT(*) FROM outages")
    total = cur.fetchone()[0]

    cur.execute("SELECT zone, COUNT(*) as c FROM outages GROUP BY zone ORDER BY c DESC LIMIT 1")
    top_zone = cur.fetchone()

    return render_template("dashboard.html", total=total, top_zone=top_zone)

# ---------------- ADD INCIDENT ----------------
@app.route("/add", methods=["POST"])
def add():
    zone = request.form["zone"]
    duration = request.form["duration"]
    cause = request.form["cause"]
    date = datetime.now()

    db = get_db()
    cur = db.cursor()

    cur.execute("INSERT INTO outages(zone, duration, cause, date) VALUES (?, ?, ?, ?)",
                (zone, duration, cause, date))
    db.commit()

    return redirect("/dashboard")

# ---------------- API FOR CHART ----------------
@app.route("/api/chart")
def chart():
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT zone, COUNT(*) FROM outages GROUP BY zone")
    data = cur.fetchall()

    zones = [x[0] for x in data]
    counts = [x[1] for x in data]

    return jsonify({"zones": zones, "counts": counts})

if __name__ == "__main__":
    app.run(debug=True)