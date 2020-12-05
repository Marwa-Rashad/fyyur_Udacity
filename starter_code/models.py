from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    start_time = db.Column(db.DateTime(), nullable=False)

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', cascade="all,delete")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', cascade="all,delete")   
     # TODO: implement any missing fields, as a database migration using Flask-Migrate
