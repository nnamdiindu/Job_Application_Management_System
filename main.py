import os
from flask import Flask, render_template
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

load_dotenv()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("company-profile-setup.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("job-seeker-profile-setup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("employee-dashboard.html")

@app.route("/dashboards")
def dashboardd():
    return render_template("employer-dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)