from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    comments = db.relationship("Comment",backref="user",lazy=True)

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    author= db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    comments = db.relationship("Comment",backref="book",lazy=True)
    
    def add_comment(self, comment,usr_id):
        c = Comment(comment=comment, book_id=self.id, user_id=usr_id)
        db.session.add(c)
        db.session.commit()

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
