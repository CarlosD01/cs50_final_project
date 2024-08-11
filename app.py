from flask import Flask, redirect, render_template, request, session, flash, url_for
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField, ValidationError, SelectField # type: ignore
from wtforms.validators import DataRequired, EqualTo, InputRequired # type: ignore
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import jinja2
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor, CKEditorField
from flask_migrate import Migrate
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Create Flask Instance
app = Flask(__name__)

# Add CKEditor
ckeditor = CKEditor(app)

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config["SECRET_KEY"] = "12345"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initializa Database
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Flask_Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Loads user when logged in
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Declare Admin IDs
admin_user = [1]

# Create Form Class
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(50))
    username = db.Column(db.String(50), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String())
    user_bio = db.Column(db.String(1000))
    posts = db.relationship('Posts', backref='users', lazy=True)
    comments = db.relationship('Comments', backref='commenter', lazy=True)
    user_like = db.relationship('Like', backref='user_like', lazy=True)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_like = db.relationship('Like', backref='post_like', lazy=True)
    post_like = db.relationship('Comments', backref='post_comment', lazy=True)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Communities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    community = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(1000))

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

class Update(FlaskForm):
    display_name = StringField()
    profile_pic = FileField()
    user_bio = TextAreaField()
    delete = delete = SubmitField("Delete")
    save = SubmitField("Save")
    upload = SubmitField("Upload")

class Post(FlaskForm):
    title = StringField(validators=[DataRequired()])
    body = CKEditorField(validators=[DataRequired()])
    community = SelectField(validators=[DataRequired()])
    post = SubmitField("Post")
    delete = SubmitField("Delete")

class Community(FlaskForm):
    name = StringField(validators=[DataRequired()])
    description = TextAreaField()
    create = SubmitField("Create")
    save = SubmitField("Save")
    delete = SubmitField("Delete")

class Comment(FlaskForm):
    comment = StringField(validators=[InputRequired()])
    submit = SubmitField("Comment")

@app.route("/", methods=["GET"])
def index():
    post_history = Posts.query.order_by(Posts.date_created.desc())

    communities = Communities.query.order_by(Communities.community)

    return render_template("index.html", admin_user=admin_user, communities=communities, post_history=post_history)

@app.route("/like/<int:id>", methods=["GET"])
@login_required
def post_like(id):
    post = Posts.query.get_or_404(id)

    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for('post_page', id=post.id))

@app.route("/f/<community>", methods=["GET"])
def community(community):
    post_community = Posts.query.filter_by(community=community).order_by(Posts.date_created.desc())

    communities = Communities.query.order_by(Communities.community)

    community_bio = Communities.query.filter_by(community=community).first()

    return render_template("community.html", admin_user=admin_user, communities=communities, community_bio=community_bio, post_community=post_community)

@app.route("/community/add", methods=["GET", "POST"])
@login_required
def community_add():
    form = Community()

    communities = Communities.query.order_by(Communities.community)
    
    if form.validate_on_submit():

        communities_new = Communities(community=form.name.data, description=form.description.data)

        # Add changes to post db
        db.session.add(communities_new)
        db.session.commit()

        flash("Community successfully added.")
        return redirect("/")
    
    return render_template("community_add.html", admin_user=admin_user, communities=communities, form=form)

@app.route("/community/edit/<int:id>", methods=["GET", "POST"])
@login_required
def community_edit(id):
    form = Community()

    community_edit = Communities.query.get_or_404(id)

    communities = Communities.query.order_by(Communities.community)
    
    if form.validate_on_submit():
        if form.save.data:

            community_edit.community = form.name.data
            community_edit.description = form.description.data

            # Add changes to post db
            db.session.add(community_edit)

            # Update the post db
            db.session.commit()

            flash("Changes made successfully.")
            return redirect("/")

        elif form.delete.data:
            
            # Delete post from post db
            db.session.delete(community_edit)

            # Update the post db
            db.session.commit()

            flash("Community successfully deleted.")
            return redirect("/")
    
    form.name.data = community_edit.community
    form.description.data = community_edit.description
    
    return render_template("community_edit.html", admin_user=admin_user, communities=communities, form=form)

@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    form = Post()

    communities = Communities.query.order_by(Communities.community)

    form.community.choices = [(i.community, i.community) for i in communities]

    if form.validate_on_submit():
        post = Posts(title=form.title.data, body=form.body.data, community=form.community.data, user_id=current_user.id)

        # Commit post to post db
        db.session.add(post)
        db.session.commit()

        # Clear form data
        form.title.data = ""
        form.body.data = ""

        flash("Post created.")

    return render_template("post.html", admin_user=admin_user, communities=communities, form=form)

@app.route("/post/edit/<int:id>", methods=["GET", "POST"])
@login_required
def post_edit(id):
    form = Post()
    
    post = Posts.query.get_or_404(id)

    communities = Communities.query.order_by(Communities.community)
    
    if form.validate_on_submit():
        if form.post.data:

            post.title = form.title.data
            post.body = form.body.data
            post.community = form.community.data

            # Add changes to post db
            db.session.add(post)

            # Update the post db
            db.session.commit()

            flash("Changes made successfully.")
            return redirect(url_for('post_page', id=post.id))

        elif form.delete.data:
            
            # Delete post from post db
            db.session.delete(post)

            # Update the post db
            db.session.commit()

            flash("Post successfully deleted.")
            return redirect("/")
    
    form.title.data = post.title
    form.body.data = post.body
    form.community.data = post.community
    
    return render_template("post_edit.html", admin_user=admin_user, communities=communities, form=form)

@app.route("/post/<int:id>", methods=["GET", "POST"])
def post_page(id):
    form = Comment()

    post = Posts.query.get_or_404(id)

    communities = Communities.query.order_by(Communities.community)

    if form.validate_on_submit():
        comment = Comments(body=form.comment.data, username=current_user.username, post_id=post.id, user_id=current_user.id)

        # Commit comment to comment db
        db.session.add(comment)
        db.session.commit()

        # Clear form data
        form.comment.data = ""

    # Display comments for specified post in order of newest 
    comments = Comments.query.filter_by(post_id=post.id).order_by(Comments.date_created)

    return render_template("post_page.html", admin_user=admin_user, communities=communities, post=post, comments=comments, form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    communities = Communities.query.order_by(Communities.community)

    form = Login()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()

        if user is None:
            flash("User does not exist.")
            return redirect("/login")
        
        else:
            if check_password_hash(user.password_hash, form.password.data):

                login_user(user)

                flash("Login successful.")
            
            else:
                flash("Incorrect password.")
                
        return redirect(url_for('dashboard', id=user.id))

    return render_template("login.html", communities=communities, form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    communities = Communities.query.order_by(Communities.community)

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

            flash("User added successfully.")
            return redirect("/login")
        
        else:
            flash("User already exists.")
            return redirect("/signup")
        
    return render_template("signup.html", communities=communities, form=form)

@app.route("/dashboard/user/<int:id>", methods=["GET", "POST"])
@login_required
def dashboard(id):
    form = Update()

    user = Users.query.get_or_404(id)

    communities = Communities.query.order_by(Communities.community)
    
    if request.method == "POST":
        if form.save.data:

            user.display_name = request.form["display_name"]
            user.user_bio = request.form["user_bio"]
            
            db.session.commit()

            flash("Changes made successfully.")

        elif form.upload.data:
            user.profile_pic = request.files["profile_pic"]


            # Get image name
            pic_name = secure_filename(user.profile_pic.filename)

            # Set UUID
            pic_id = str(uuid.uuid1()) + "_" + pic_name

            # Save image
            saver = request.files["profile_pic"]
            
            # Change to string
            user.profile_pic = pic_id

            # Update the post db
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_id))

            flash("Photo upload successful.")

        elif form.delete.data:
            
            # Delete post from post db
            db.session.delete(user)

            # Update the post db
            db.session.commit()

            flash("User successfully deleted.")
            return redirect("/")
    
    form.display_name.data = user.display_name
    form.user_bio.data = user.user_bio
    form.profile_pic.process_data(url_for('static', filename='images/' + user.profile_pic))
    post_history = Posts.query.filter_by(user_id=id).order_by(Posts.date_created.desc())

    return render_template("dashboard.html", admin_user=admin_user, communities=communities, post_history=post_history, form=form)

@app.route("/view/<int:id>", methods=["GET"])
def view(id):

    user = Users.query.get_or_404(id)

    communities = Communities.query.order_by(Communities.community)
    
    post_history = Posts.query.filter_by(user_id=user.id).order_by(Posts.date_created.desc())

    comments = Comments.query.filter_by(user_id=user.id).order_by(Comments.date_created)

    return render_template("view.html", admin_user=admin_user, communities=communities, post_history=post_history, comments=comments, user=user)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logout successful.")
    return redirect("/")
    
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    communities = Communities.query.order_by(Communities.community)

    return render_template("404.html", communities=communities), 404

# Internal Server Error
@app.errorhandler(500)
def server_error(e):
    communities = Communities.query.order_by(Communities.community)

    return render_template("500.html", communities=communities), 500
