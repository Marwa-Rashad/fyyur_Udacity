#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys, datetime
import json
import dateutil.parser
import babel
from flask_sqlalchemy import SQLAlchemy
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    Response,
    abort)
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_moment import Moment
from flask_migrate import Migrate
import forms
import models
from models import app, db, Venue, Artist, Show
from forms import ShowForm, VenueForm, ArtistForm
from flask_wtf.csrf import CsrfProtect

CsrfProtect(app)

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)


# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.





#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  error=False
  try:
    areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
    data = []
    for area in areas:
      rows = db.session.query(Venue).filter(Venue.city == area.city).all()
      venue_data = []
      for venue in rows:
        venue_data.append({
        'id': venue.id,
        'name':venue.name,
      })
      data.append({
        'city':area.city,
        'state':area.state,
        'venues':venue_data
      })
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Error ==> {e}')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  error=False
  try:
    search_term=request.form.get('search_term', '')
    search = "%{}%".format(search_term)
    data = db.session.query(Venue).filter(Venue.name.ilike(search)).all()
    venues = []
    for venue in data:
      venues.append({
            "id": venue.id,
      "name": venue.name,
    })
    response= {
    "count": len(venues),
    "data": venues
  }
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Error ==> {e}')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  error=False
  try:
    venue = Venue.query.get(venue_id)
    if not venue:
      return render_template('errors/404.html'), 404
    else:
      data = db.session.query(Show).join(Venue).filter(Venue.id== venue.id).join(Artist).all()
      upcoming_shows = []
      past_shows = []
      for row in data:
        if row.start_time > datetime.now():
          upcoming_shows.append({
        'artist_id': row.artist.id,
        'artist_name': row.artist.name,
        'artist_image_link': row.artist.image_link,
        'start_time': row.start_time})
        if row.start_time < datetime.now():
          past_shows.append({
        'artist_id': row.artist.id,
        'artist_name': row.artist.name,
        'artist_image_link': row.artist.image_link,
        'start_time': row.start_time})
      venueData = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows" : upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Error ==> {e}')
  finally:
    db.session.close()
    return render_template('pages/show_venue.html', venue=venueData)

    

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error=False
  form = VenueForm()
  form.validate_on_submit()
  if not form.validate_on_submit():
    flash('Error: Venue ' + request.form['name'] + ' was not listed. Please check your inputs and try again :)')
    return render_template('forms/new_venue.html', form=form)
  else: 
      try:
        venue = Venue(name = request.form.get('name'),
        city = request.form.get('city'),
        address= request.form.get('address'),
    state = request.form.get('state'),
    phone = request.form.get('phone'),
    genres = request.form.getlist('genres'),
    image_link = request.form.get('image_link', ""),
    facebook_link = request.form.get('facebook_link', ""),
    website = request.form.get('website', ""),
    seeking_talent = True if request.form.get('seeking_talent') else False,
    seeking_description = request.form.get('seeking_description', ""))
        db.session.add(venue)
        db.session.commit()
      except Exception as e:
        error = True
        db.session.rollback()
        print(f'Error ==> {e}')
      finally:
        db.session.close()
      if error:
    # [x] On unsuccessful db insert, flash an error
        flash('Error: Venue ' + request.form['name'] + ' was not listed. Please check your inputs and try again :)')
        return render_template('forms/new_venue.html', form=form)
      else:
    # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return None
    # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.order_by('id').all())
  # TODO: replace with real data returned from querying the database
 
@app.route('/artists/search', methods=['POST'])
def search_artists():

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  error=False
  try:
    search_term=request.form.get('search_term', '')
    search = "%{}%".format(search_term)
    data = db.session.query(Artist).filter(Artist.name.ilike(search)).all()
    artists = []
    for artist in data:
      artists.append({
            "id": artist.id,
      "name": artist.name,
    })
    response= {
    "count": len(artists),
    "data": artists
  }
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Error ==> {e}')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  error=False
  try:
    artist = Artist.query.get(artist_id)
    if not artist:
      return render_template('errors/404.html'), 404
    else:
      data = db.session.query(Show).join(Artist).filter(Artist.id == artist.id).join(Venue).all()
      upcoming_shows = []
      past_shows = []
      for row in data:
        if row.start_time > datetime.now():
          upcoming_shows.append({
        'venue_id': row.venue.id,
        'venue_name': row.venue.name,
        'venue_image_link': row.venue.image_link,
        'start_time': row.start_time})
        if row.start_time < datetime.now():
          past_shows.append({
        'venue_id': row.venue.id,
        'venue_name': row.venue.name,
        'venue_image_link': row.venue.image_link,
        'start_time': row.start_time})
      artistData = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows" : upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Error ==> {e}')
  finally:
    db.session.close()
    return render_template('pages/show_artist.html', artist=artistData)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)


  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error=False
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form.get('image_link', "")
    artist.facebook_link = request.form.get('facebook_link', "")
    artist.website = request.form.get('website', "")
    artist.seeking_venue = True if request.form.get('seeking_venue') else False
    artist.seeking_description = request.form.get('seeking_description', "")
    print(artist)
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Error ==> {e}')
  finally:
    db.session.close()
  if error:
    # [x] On unsuccessful db insert, flash an error
    flash('Error: Artist ' + request.form['name'] + ' was not updated. Please check your inputs and try again :)')
    abort(400)
  else:
    # on successful db insert, flash success
    flash(request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error=False
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link', "")
    venue.facebook_link = request.form.get('facebook_link', "")
    venue.website = request.form.get('website', "")
    venue.seeking_talent = True if request.form.get('seeking_talent') else False
    venue.seeking_description = request.form.get('seeking_description', "")
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Error ==> {e}')
  finally:
    db.session.close()
  if error:
    # [x] On unsuccessful db insert, flash an error
    flash('Error: Venue ' + request.form['name'] + ' was not updated. Please check your inputs and try again :)')
    abort(400)
  else:
    # on successful db insert, flash success
    flash(request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  # TODO: populate form with values from venue with ID <venue_id>



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error=False
  form = ArtistForm()
  form.validate_on_submit()
  if not form.validate_on_submit():
    flash('Error: Artist ' + request.form['name'] + ' was not listed. Please check your inputs and try again :)')
    return render_template('forms/new_artist.html', form=form)
  else: 
    try:
      artist = Artist(name = request.form.get('name'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    phone = request.form.get('phone'),
    genres = request.form.getlist('genres'),
    image_link = request.form.get('image_link', ""),
    facebook_link = request.form.get('facebook_link', ""),
    website = request.form.get('website', ""),
    seeking_venue = True if request.form.get('seeking_venue') else False,
    seeking_description = request.form.get('seeking_description', ""))
      db.session.add(artist)
      db.session.commit()
    except Exception as e:
      error = True
      db.session.rollback()
      print(f'Error ==> {e}')
    finally:
      db.session.close()
    if error:
  # [x] On unsuccessful db insert, flash an error
      flash('Error: Artist ' + request.form['name'] + ' was not listed. Please check your inputs and try again :)')
      return render_template('forms/new_artist.html', form=form)
    else:
    # on successful db insert, flash success
      flash(request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  error=False
  try:
    shows = Show.query.all()
    data = []
    for show in shows:
      show.venue_name = db.session.query(Venue.name).filter_by(id=show.venue_id).first()[0]
      show.artist_name = db.session.query(Artist.name).filter_by(id=show.artist_id).first()[0]
      show.artist_image_link = db.session.query(Artist.image_link).filter_by(id=show.artist_id).first()[0]
      show.start_time = show.start_time
      data.append(show)
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Error ==> {e}')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return render_template('pages/shows.html', shows=data) 
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #      num_shows should be aggregated based on number of upcoming shows per venue.
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:
      artist = Artist.query.get(request.form.get('artist_id'))
      venue = Venue.query.get(request.form.get('venue_id'))
      if artist.seeking_venue and venue.seeking_talent:
        show = Show(venue_id=request.form.get('venue_id'),
        artist_id=request.form.get('artist_id'),
        start_time=request.form.get('start_time'))
        db.session.add(show)
        db.session.commit()
      else:
        error = True
    except Exception as e:
      error = True
      db.session.rollback()
      print(f'Error ==> {e}')
    finally:
      db.session.close()
    if error:
      print(sys.exc_info())
      flash('Artist or/and Venue is not seeking shows!')
      return render_template('pages/home.html')
    else:
      flash('Show was successfully listed!')
      return redirect(url_for('shows'))
    # on successful db insert, flash success


  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
