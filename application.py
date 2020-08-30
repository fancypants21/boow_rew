from flask import Flask, session, redirect, url_for, render_template, request
from flask_session import Session
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
import requests

app = Flask(__name__)

# Check for environment variable
if not "postgres://xvqgrrhdrnnlxc:e9af57d1d766ba516dcb631e4cee8a1fe805f1ee4c4523babf1099e9c2f1ee37@ec2-34-248-165-3.eu-west-1.compute.amazonaws.com:5432/d702ham2elhgno":
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://xvqgrrhdrnnlxc:e9af57d1d766ba516dcb631e4cee8a1fe805f1ee4c4523babf1099e9c2f1ee37@ec2-34-248-165-3.eu-west-1.compute.amazonaws.com:5432/d702ham2elhgno"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'super secret key'
db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).scalar()
        if user == None:
            user = User(username=username,password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("sign"))
        else:
            return render_template("error.html",message="User already exists")
    return render_template("register.html")

@app.route("/sign",methods=["GET","POST"])
def sign():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).all()
        print(user)
        if user == []:
            return render_template("error.html",message="No such username.")
        else:
            user = user[0]
            print(user.password)
            if user.password != password:
                return render_template("error.html",message="Wrong Password")
            else:
                print(user.id)
                session["user_id"] = user.id
                return redirect(url_for("home",user_id=user.id))
    return render_template("sign.html")

@app.route("/<int:user_id>",methods=["GET","POST"])
def home(user_id):
    if session["user_id"] != user_id:
        return redirect(url_for('sign'))
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        search = request.form.get("search")
        return redirect(url_for("search",search=search))
    return render_template("home.html",user=user)

@app.route("/search=<string:search>",methods=["POST","GET"])
def search(search):
    if session["user_id"] == None:
        return redirect(url_for('sign'))
    user = User.query.get(session["user_id"])
    books = Book.query.filter(or_(Book.title.like(f"%{search}%"),Book.author.like(f"%{search}%"),Book.isbn.like(f"%{search}%"))).all()
    print(books)
    return render_template("search.html",books=books)

@app.route("/home/search/<int:book_id>",methods=["GET","POST"])
def book(book_id):
    if session["user_id"] == None:
        return redirect(url_for('sign'))
    user = User.query.get(session["user_id"])
    book = Book.query.get(book_id)
    if request.method == "POST":
        comment = request.form.get("comment")
        book.add_comment(comment,user.id)
        return redirect(url_for("book",book_id=book.id))
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "FvSBmyWw5ccPn4T7Gc0Q", "isbns": book.isbn})
    if res.status_code != 200:
        return render_template("error.html",message="Something went wrong")
    data = res.json()
    return render_template("book.html",book = book,comments=book.comments,data=data)

@app.route("/home/search/user=<int:user_id>")
def user(user_id):
    if session["user_id"] == None:
        return redirect(url_for("sign"))
    looked_user = User.query.get(user_id)
    return render_template("user.html",user=looked_user)

@app.route("/out",methods=["POST"])
def out():
    session["user_id"] = None
    return render_template("out.html")
