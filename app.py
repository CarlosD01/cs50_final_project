from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import jinja2

# Configure application
app = Flask(__name__)

# Add db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///forums.db"

# Initialize db (pass app)
db = SQLAlchemy(app)

communities = ["Movies", "Games", "Sports", "Politics", "Reading"]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/post")
def post():
    return render_template("post.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        return redirect("/")

    else:
        return render_template("signup.html")
    
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500
