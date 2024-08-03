from flask import Flask, redirect, render_template, request, session, flash, url_for
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField, ValidationError, SelectField # type: ignore
from wtforms.validators import DataRequired, EqualTo, InputRequired # type: ignore
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import jinja2
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# Create Flask Instance
app = Flask(__name__)

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config["SECRET_KEY"] = "12345"

# Initializa Database
db = SQLAlchemy(app)

# Flask_Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Loads user when logged in
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Temporary Communities List
communities = ["Art", "Books", "Film", "Gaming", "Lifestyle", "Politics"]

# Create Form Class
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Posts', backref='users', lazy=True)

    password_hash = db.Column(db.String(50), nullable=False)

    @property
    def password(self):
        raise AttributeError('password not readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    body = db.Column(db.String(1000), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    community = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(50), nullable=False)
    comments = db.relationship('Comments', backref='posts', lazy=True)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

with app.app_context():
    db.create_all()

class Login(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Log In")

class Signup(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password_hash = PasswordField(validators=[DataRequired(), EqualTo('confirm', message='Passwords must match!')])
    confirm = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Sign Up")

class Post(FlaskForm):
    title = StringField(validators=[InputRequired()])
    body = TextAreaField(validators=[InputRequired()])
    community = SelectField(validators=[DataRequired()], choices=[("Select a Community"), ("Art"), ("Books"), ("Film"), ("Gaming"), ("Lifestyle"), ("Politics")])
    post = SubmitField("Post")

class Comment(FlaskForm):
    comment = StringField(validators=[InputRequired()])
    submit = SubmitField("Comment")


@app.route("/", methods=["GET"])
def index():
    post_history = Posts.query.order_by(Posts.date_created.desc())

    return render_template("index.html", communities=communities, post_history=post_history)

@app.route("/community/", methods=["GET"])
def community():
    
    post_community = Posts.query.filter_by(community=Posts.community).order_by(Posts.date_created.desc())

    return render_template("community.html", communities=communities, post_community=post_community)

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    form = Post()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, body=form.body.data, community=form.community.data, user_id=current_user.id, username=current_user.username)

        # Commit post to post db
        db.session.add(post)
        db.session.commit()

        # Clear form data
        form.title.data = ""
        form.body.data = ""

        flash("Post created!")

    return render_template("post.html", communities=communities, form=form)

app.route("/post/edit/<int:id>", methods=["GET", "POST"])
@login_required
def post_edit(id):
    form = Post()
    post = Posts.query.get_or_404(id)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.community = form.community.data

        # Update the post db
        db.session.add(post)
        db.session.commit

        flash("Changes made successfully.")

        return redirect(url_for('post', id=post.id), communities=communities)
    
    form.title.data = post.title
    form.body.data = post.body
    form.community.data = post.community
    
    return render_template("post_edit.html", communities=communities, form=form)

@app.route("/post/<int:id>", methods=["GET", "POST"])
def post_page(id):
    form = Comment()

    post = Posts.query.get_or_404(id)

    if form.validate_on_submit():
        comment = Comments(body=form.comment.data, username=current_user.username, post_id=post.id)

        # Commit comment to comment db
        db.session.add(comment)
        db.session.commit()

        # Clear form data
        form.comment.data = ""

    # Display comments for specified post in order of newest 
    comments = Comments.query.filter_by(post_id=post.id).order_by(Comments.date_created.desc())
    return render_template("post_page.html", communities=communities, post=post, comments=comments, form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = Login()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()

        if user is None:
            flash("User does not exist.")
            return redirect("/login")
        
        else:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successful!")
            
            else:
                flash("Incorrect password.")
                
            return redirect("/dashboard")

    return render_template("login.html", communities=communities, form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    username = None
    form = Signup()


    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()

        if user is None:
            # Hash password
            hashed_pw = generate_password_hash(form.password_hash.data)

            user = Users(username=form.username.data, password_hash=hashed_pw)

            # Commit user to user db
            db.session.add(user)
            db.session.commit()

            # Clear form data
            form.username.data = ""
            form.password_hash.data = ""

            flash("User added successfully!")
            return redirect("/login")
        
        else:
            flash("User already exists!")
            return redirect("/signup")
        
    user = Users.query.order_by(Users.date_created)
    return render_template("signup.html", communities=communities, form=form)

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html", communities=communities)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logout successful.")
    return redirect("/")
    
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", communities=communities), 404

# Internal Server Error
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", communities=communities), 500
