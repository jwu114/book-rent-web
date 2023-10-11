from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from json import load

from . import login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    firstname = db.Column(db.String(64), index = True)
    lastname = db.Column(db.String(64), index = True)
    
    def __repr__(self):
        return "<user %r>" % self.email
    
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(64), index = True)
    author = db.Column(db.String(64), index = True)
    country = db.Column(db.String(64), index = True)
    language = db.Column(db.String(64), index = True)
    year = db.Column(db.Integer, index = True)
    pages = db.Column(db.Integer, index = True)
    imageLink = db.Column(db.String(64), index = True)

class Rent(db.Model):
    __tablename__ = "rent_list"
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(64), index = True)
    book = db.Column(db.Integer, db.ForeignKey("books.id"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def verify_email(email):
    return User.query.filter_by(email=email).first() == None

def add_book(title, author, country, language, year, pages, imageLink):
    book = Book(title = title, author = author, country = country, language = language, year = year, pages = pages, imageLink = imageLink)
    db.session.add(book)
    db.session.commit()

def get_book(book_id):
    return Book.query.get(int(book_id))

def get_all_books():
    return Book.query.all()

def search_books(key):
    if key == None:
        return get_all_books()
    else:
        book = Book.query.filter(Book.title.contains(key))
        return book
    
def is_rented(email, book_id):
    return Rent.query.filter_by(user=email, book=book_id).first() != None

def rent_book(email, book_id):
    rent = Rent(user = email, book = book_id)
    db.session.add(rent)
    db.session.commit()

def unrent_book(email, book_id):
    Rent.query.filter_by(user=email, book=book_id).delete()
    db.session.commit()

def get_rented_books(email):
    return Rent.query.filter_by(user=email)

def init_books():
    bookList = load(open("app/books.json", "r"))
    for i in range(len(bookList)):
        book = bookList[i]
        add_book(book['title'], book['author'], book['country'], book['language'], book['year'], book['pages'], book['imageLink'])