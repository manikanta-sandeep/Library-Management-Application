from sqlalchemy import ForeignKey
from .database import db 
from .nophoto import images
from sqlalchemy.orm import relationship

class login(db.Model):
    __tablename__="login"
    email=db.Column(db.String, primary_key=True,unique=True)
    password=db.Column(db.String)

class user(db.Model):
    __tablename__="user"
    user_id=db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name=db.Column(db.String)
    email=db.Column(db.String, unique=True)
    dob=db.Column(db.String)
    password=db.Column(db.String)
    profile_picture=db.Column(db.LargeBinary, default=images().noimage())
    user_privileges=db.Column(db.Integer,default=0)

class books(db.Model):
    __tablename__="books"
    book_name=db.Column(db.String)
    book_isbn=db.Column(db.Integer,primary_key=True, autoincrement=True)
    authors=db.Column(db.String)
    edition=db.Column(db.Integer, default=1)
    picture=db.Column(db.LargeBinary, default=images().nodp())
    book_id=db.Column(db.Integer)
    available=db.Column(db.Integer,default=1)

class cart(db.Model):
    __tablename__="cart"
    cart_id=db.Column(db.Integer,primary_key=True)
    book_id=db.Column(db.Integer, ForeignKey("books.book_id",ondelete="CASCADE",onupdate="CASCADE"))
    user_email=db.Column(db.String, ForeignKey("user.email",ondelete="CASCADE",onupdate="CASCADE"))
    cart_state=db.Column(db.Integer)

class book_transactions(db.Model):
    __tablename__="book_transactions"
    serial_no=db.Column(db.Integer,primary_key=True,autoincrement=True)
    transaction_id=db.Column(db.Integer)
    book_id=db.Column(db.Integer, ForeignKey("books.book_id",ondelete="CASCADE",onupdate="CASCADE"))
    book_isbn=db.Column(db.Integer, ForeignKey("books.book_isbn",ondelete="CASCADE",onupdate="CASCADE"))
    book_user=db.Column(db.Integer, ForeignKey("user.user_id",ondelete="CASCADE",onupdate="CASCADE"))
    date_time=db.Column(db.String)
    state=db.Column(db.Integer)
    request_state=db.Column(db.Integer)

class fines(db.Model):
    __tablename__="fines"
    fine_no=db.Column(db.Integer,primary_key=True,autoincrement=True)
    transaction_id=db.Column(db.Integer, ForeignKey("book_transactions.transaction_id",ondelete="CASCADE",onupdate="CASCADE"))
    due=db.Column(db.String)
    fine_amount=db.Column(db.String)


class history(db.Model):
    __tablename__="history"
    serial_no=db.Column(db.Integer,primary_key=True)
    transaction_id=db.Column(db.Integer)
    book_id=db.Column(db.Integer)
    book_isbn=db.Column(db.Integer)
    book_user=db.Column(db.Integer)
    date_time=db.Column(db.String)
    state=db.Column(db.Integer)
