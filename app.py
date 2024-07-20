from flask import Flask, redirect, render_template, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, InputRequired
from datetime import datetime
import jinja2

# Configure application
app = Flask(__name__)


# Create Form Class
class Login(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Log In")

class Signup(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    confirm = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Sign Up")

class Post(FlaskForm):
    title = StringField(validators=[InputRequired()])
    body = TextAreaField(validators=[InputRequired()])
    save = SubmitField("Save Draft")
    post = SubmitField("Post")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/post", methods=["GET", "POST"])
def post():
    title = None
    body = None
    form = Post()

    if request.method == "POST":
        if form.validate_on_submit():

            title = form.title.data
            body = form.body.data
            form.title.data = ""
            form.body.data = ""

            if form.post.data:
                return render_template("index.html", title=title, body=body, form=form)
            
            elif form.save.data:
                return render_template("post.html", title=title, body=body, form=form)

    
    else:
        return render_template("post.html", title=title, body=body, form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    username = None
    password = None
    form = Login()

    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            form.username.data = ""
            form.password.data = ""

        return render_template("login.html", username=username, password=password, form=form)
    
    else:
        return render_template("login.html", username=username, password=password, form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    username = None
    password = None
    confirm = None
    form = Signup()

    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            confirm = form.confirm.data
            form.username.data = ""
            form.password.data = ""
            form.confirm.data = ""

            return render_template("signup.html", username=username, password=password, confirm=confirm, form=form)
    
    else:
        return render_template("signup.html", username=username, password=password, confirm=confirm, form=form)
    
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500
