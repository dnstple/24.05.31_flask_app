from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import random
from datetime import datetime


# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     data = db.Column(db.String(10000))
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def generate_unique_id():
    while True:
        id = random.randint(1, 10000000)
        if not User.query.filter_by(id=id).first():
            return id
        

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, default=generate_unique_id)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(150))
    city = db.Column(db.String(150))
    postcode = db.Column(db.String(150))

    # notes = db.relationship('Note')
    listings = db.relationship('Listings', foreign_keys='Listings.user_id', backref='user')
    messages = db.relationship('Messages', foreign_keys='Messages.user_id', backref='user')


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    message = db.Column(db.String(1000), db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))




class Listings(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id = db.Column(db.Integer, primary_key=True)

    image_path = db.Column(db.String(150), unique=True)
    title = db.Column(db.String(150))
    description = db.Column(db.String(1000))
    price = db.Column(db.Float)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(150))
    city = db.Column(db.String(150))
    postcode = db.Column(db.String(150))
