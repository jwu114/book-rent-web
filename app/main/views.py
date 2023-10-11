from flask import session
from flask import render_template, redirect, url_for, flash, send_from_directory, request
from . import main
from .. import db
from ..models import User, get_all_books, get_book, search_books, verify_email, rent_book, unrent_book, is_rented, get_rented_books
from .forms import RegisterForm, LoginForm

from flask_login import login_required, current_user
from flask_login import login_user, logout_user

import os

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@main.route("/", methods = ["GET", "POST"])
def index():
    imageLinks = []
    titles = []
    ids = []
    books = get_all_books()

    if current_user.is_authenticated:
        session['url_logout'] = request.url
    else:
        session['url_login'] = request.url

    if(request.method == 'POST'):
        form_data = request.form["search"]
        return redirect("/search_result?search=" + form_data)

    for book in books[:6]:
        imageLinks.append(url_for('static', filename=book.imageLink))
        titles.append(book.title)
        ids.append(str(book.id))

    return render_template("homepage.html", ziplist=zip(imageLinks, titles, ids), login=current_user.is_authenticated)

@main.route("/search_result", methods = ["GET", "POST"])
def books():
    key = request.args.get('search')
    imageLinks = []
    titles = []
    ids = []
    books = search_books(key)

    if current_user.is_authenticated:
        session['url_logout'] = request.url
    else:
        session['url_login'] = request.url

    if(request.method == 'POST'):
        form_data = request.form["search"]
        return redirect("/search_result?search=" + form_data)
        
    for book in books:
        imageLinks.append(url_for('static', filename=book.imageLink))
        titles.append(book.title)
        ids.append(str(book.id))

    return render_template("bookspage.html", ziplist=zip(imageLinks, titles, ids), num=len(titles), login=current_user.is_authenticated)
    
@main.route("/book/<id>", methods=["GET", "POST"])
def book(id):
    book = get_book(id)
    login = current_user.is_authenticated
    rented = False

    if login:
        rented = is_rented(current_user.email, id)

    if login:
        session['url_logout'] = request.url
    else:
        session['url_login'] = request.url

    if(request.method == 'POST'):
        form_data = request.form["search"]
        return redirect("/search_result?search=" + form_data)
    
    return render_template("bookpage.html", id=book.id, title=book.title, author=book.author, country=book.country, language=book.language, year=str(book.year), pages=str(book.pages), imageLink=url_for('static', filename=book.imageLink), login=current_user.is_authenticated, rented=rented)
    

@main.route("/profile", methods = ["GET", "POST"])
@login_required
def profile():
    imageLinks = []
    titles = []
    ids = []
    rented_books = get_rented_books(current_user.email)

    if current_user.is_authenticated:
        session['url_logout'] = url_for("main.index")

    if(request.method == 'POST'):
        form_data = request.form["search"]
        return redirect("/search_result?search=" + form_data)

    for rent in rented_books:
        imageLinks.append(url_for('static', filename=get_book(rent.book).imageLink))
        titles.append(get_book(rent.book).title)
        ids.append(str(get_book(rent.book).id))
    
    return render_template("profilepage.html", email=current_user.email, firstname=current_user.firstname, lastname=current_user.lastname, ziplist=zip(imageLinks, titles, ids))


@main.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        session['url_logout'] = request.url

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        fname = form.fname.data
        lname = form.lname.data
        password = form.password.data
        if verify_email(email):
            createUser(email, password, fname, lname)
            return redirect(url_for("main.index"))
        flash("The email has been used")
    return render_template("registerpage.html", form = form, login=current_user.is_authenticated)

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        session['url_logout'] = request.url

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, True)
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                if 'url_login' in session:
                    next = session['url_login']
                else:
                    next = url_for("main.index")
            return redirect(next)
        flash("Oops, that's not a match")
    return render_template("signpage.html", form = form, login=current_user.is_authenticated)

@main.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    if 'url_logout' in session:
        return redirect(session['url_logout'])
    return redirect(url_for("main.index"))

@main.route("/rent/<id>", methods = ["GET", "POST"])
@login_required
def rent(id):
    if is_rented(current_user.email, id):
        unrent_book(current_user.email, id)
    else:
        rent_book(current_user.email, id)

    if 'url_logout' in session:
        return redirect(session['url_logout'])
    elif 'url_login' in session:
        return redirect(session['url_login'])
        
    return redirect(url_for("main.index"))
 
def createUser(email, password, fname, lname):
    user = User(email = email, password=password, firstname = fname, lastname = lname)
    db.session.add(user)
    db.session.commit()