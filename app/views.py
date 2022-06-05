from datetime import datetime
from flask import redirect, render_template, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    login_user,
    login_required,
    current_user,
    logout_user,
)

from app import app, db, login_manager
from app.utils import get_user_name
from app.forms import UserLoginForm, UserRegisterForm, CreatePostForm
from app.models import BlogPost, User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET"])
def get_all_posts():
    if current_user.is_authenticated:
        posts = BlogPost.query.all()
    else:
        posts = None
    return render_template(
        "index.html",
        all_posts=posts,
        logged_user=get_user_name(),
        logged_in=current_user.is_authenticated,
    )


@app.route("/user-posts", methods=["GET"])
def user_posts():
    posts = BlogPost.query.filter_by(author=current_user).all()
    return render_template(
        "index.html",
        all_posts=posts,
        logged_user=get_user_name(),
        logged_in=current_user.is_authenticated,
    )


@app.route("/post/<int:index>", methods=["GET"])
def show_post(index):
    requested_post = BlogPost.query.get(index)
    return render_template(
        "post.html",
        post=requested_post,
        logged_user=get_user_name(),
        logged_in=current_user.is_authenticated,
    )


@app.route("/edit-post/<int:index>", methods=["GET", "POST"])
@login_required
def edit_post(index):
    edited_post: BlogPost = BlogPost.query.get(index)
    edit_form = CreatePostForm(
        title=edited_post.title,  # pre populating the form by provided blog
        subtitle=edited_post.subtitle,
        img_url=edited_post.img_url,
        author=edited_post.author,
        body=edited_post.body,
    )
    if request.method == "GET":
        return render_template(
            "make-post.html",
            form=edit_form,
            index=index,
            logged_user=get_user_name(),
            logged_in=current_user.is_authenticated,
        )
    edited_post.title = edit_form.title.data
    edited_post.subtitle = edit_form.subtitle.data
    edited_post.body = edit_form.body.data
    edited_post.author = current_user
    edited_post.img_url = edit_form.img_url.data
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/make-post", methods=["GET", "POST"])
@login_required
def make_post():
    new_post_form = CreatePostForm()
    if request.method == "GET":
        return render_template(
            "make-post.html",
            form=new_post_form,
            logged_user=get_user_name(),
            logged_in=current_user.is_authenticated,
        )
    new_post = BlogPost(
        title=new_post_form.title.data,
        subtitle=new_post_form.subtitle.data,
        date=datetime.today().strftime("%Y-%m-%d"),
        body=new_post_form.body.data,
        author=current_user,
        img_url=new_post_form.img_url.data,
    )
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/delete-post/<int:index>", methods=["GET", "POST"])
@login_required
def delete_post(index):
    deleted_post = BlogPost.query.filter_by(id=index).first()
    db.session.delete(deleted_post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template(
        "about.html",
        logged_user=get_user_name(),
        logged_in=current_user.is_authenticated,
    )


@app.route("/contact")
def contact():
    return render_template(
        "contact.html",
        logged_user=get_user_name(),
        logged_in=current_user.is_authenticated,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    form_user: UserRegisterForm = UserRegisterForm()
    if request.method == "POST":
        new_user = User(
            name=form_user.name.data,
            email=form_user.email.data,
            password=generate_password_hash(password=form_user.password.data),
        )
        if User.query.filter_by(email=new_user.email).first():
            flash("Email already registered")
            return redirect(url_for("login"))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template(
        "register.html",
        form=form_user,
        logged_user=get_user_name(),
        logged_in=current_user.is_authenticated,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    form_user: UserLoginForm = UserLoginForm()
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        user: User = User.query.filter_by(email=user_email).first()
        if user is None:
            flash("User does not exist")
            return redirect(url_for("login"))
        if check_password_hash(user.password, user_password):
            login_user(user)
            return redirect(url_for("get_all_posts"))
        else:
            flash("Wrong password")
    return render_template("login.html", form=form_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))
