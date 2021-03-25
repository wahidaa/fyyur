#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate,MigrateCommand
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate= Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String()))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    #shows_ven = db.relationship('Show', backref='venue',cascade="all, delete-orphan")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue =db.Column(db.Boolean, nullable=False, default=False)
    seeking_description=db.Column(db.String(120))
    shows_art = db.relationship('Show', backref='artist',cascade="all, delete-orphan")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__='show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id=Column(db.Integer,ForeignKey('venue.id'),primary_key=True)
    artist_id=Column(db.Integer,ForeignKey('artist.id'),primary_key=True)
    start_time=db.Column(db.DateTime)
   
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
  
  data=[] 
  cities=db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  
  for city in cities :
    
    venues_city=db.session.query(Venue).filter(Venue.city==city[0], Venue.state==city[1]).all()
    nb_show_venue=[]
    for venue_ in venues_city:
        nb_show_venue.append({
             "id": venue_.id,
            "name": venue_.name,
            "num_upcoming_shows":db.session.query(Show).filter(Show.venue_id==venue_.id).filter(Show.start_time>datetime.now()).count(),
             },)
    data.append({"city": city[0],"state":city[1],"venues":nb_show_venue},)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues_result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []

  for venue in venues_result:
    data.append({
    "id": venue.id,
    "name": venue.name,
    "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()),
    })
  
  response={
    "count":len(venues_result),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data={}
  
  venue=Venue.query.get(venue_id) 
  info_past_shows=[]   
  info_upcoming_shows=[]

  past_shows=db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time<datetime.now()).all()
  
  for show in past_shows:
    
    info_past_shows.append({
    "artist_id":show.artist_id,
    "artist_name":(db.session.query(Artist.name).filter(Artist.id==show.artist_id).first())[0],
    "artist_image_link":(db.session.query(Artist.image_link).filter(Artist.id==show.artist_id).first())[0],
    "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M:%S")})
 
  upcoming_shows=db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
  for show in upcoming_shows:
    info_upcoming_shows.append({
    "artist_id":show.artist_id,
    "artist_name":(db.session.query(Artist.name).filter(Artist.id==show.artist_id).first())[0],
    "artist_image_link":(db.session.query(Artist.image_link).filter(Artist.id==show.artist_id).first())[0],
    "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M:%S")})

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres":venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link":venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": info_past_shows,
    "upcoming_shows": info_upcoming_shows,
    "past_shows_count": len(info_past_shows),
    "upcoming_shows_count": len(info_upcoming_shows)}
  
  #data = list(filter(lambda d: d['id'] == venue_id,data1))[0]
  return render_template('pages/show_venue.html', venue=data)

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
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  website = request.form.get('website')
  seeking_talent = True if 'seeking_talent' in request.form else False 
  seeking_description = request.form.get('seeking_description')

  venue = Venue(name=name,
  city=city, state=state, 
  address=address,
  phone=phone, 
  genres=genres, 
  facebook_link=facebook_link, 
  image_link=image_link, 
  website=website, 
  seeking_talent=seeking_talent,
  seeking_description=seeking_description)
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  venue = Venue.query.get(venue_id)
  
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error: 
    flash( venue.name +' was successfully  deleted.')
  if error: 
    flash('An error occurred '+ request.form['name'] +'would not be deleted.')

  return jsonify({'success': True})

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists=db.session.query(Artist).all()
  for artist in artists :
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists_result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []

  for artist in artists_result:
    data.append({
    "id": artist.id,
    "name": artist.name,
    "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()),
    })
  
  response={
    "count":len(artists_result),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data={}
  
  artist=Artist.query.get(artist_id) 
  info_past_shows=[]   
  info_upcoming_shows=[]
  past_shows=db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time<datetime.now()).all()
  
  for show in past_shows:

    info_past_shows.append({
    "venue_id":show.venue_id,
    "venue_name":(db.session.query(Venue.name).filter(Venue.id==show.venue_id).first())[0],
    "venue_image_link":(db.session.query(Venue.image_link).filter(Venue.id==show.venue_id).first())[0],
    "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M:%S")})

  upcoming_shows=db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all()
  for show in upcoming_shows:
    info_upcoming_shows.append({
    "venue_id":show.venue_id,
    "venue_name":(db.session.query(Venue.name).filter(Venue.id==show.venue_id).first())[0],
    "venue_image_link":(db.session.query(Venue.image_link).filter(Venue.id==show.venue_id).first())[0],
    "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M:%S")})

  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres":artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link":artist.facebook_link,
    "seeking_talent": True if 'seeking_talent' in request.form else False,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": info_past_shows,
    "upcoming_shows": info_upcoming_shows,
    "past_shows_count": len(info_past_shows),
    "upcoming_shows_count": len(info_upcoming_shows)}
  

  
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  
  form = ArtistForm()
  artist=db.session.query(Artist).get(artist_id)

  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data= artist.state
    form.phone.data= artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data= artist.image_link
    form.website.data= artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  update_artist=db.session.query(Artist).get(artist_id)
  try:
    update_artist.name=request.form.get('name')
    update_artist.city=request.form['city']
    update_artist.state=request.form['state']
    update_artist.phone=request.form['phone']
    update_artist.genres=request.form.getlist('genres')
    update_artist.facebook_link = request.form['facebook_link']
    update_artist.website = request.form['website']
    update_artist.seeking_venue = True if 'seeking_venue' in request.form else False
    update_artist.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    flash('An error occurred Artist is not updated .')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
 
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=db.session.query(Artist).get(venue_id)

  if venue:
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data= venue.state
    form.phone.data= venue.phone
    form.genres.data =venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data= venue.image_link
    form.website.data= venue.website
    form.seeking_artist.data = venue.seeking_artist
    form.seeking_description.data = venue.seeking_description

 
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  update_venue=db.session.query(Venue).get(venue_id)
  try:
    update_venue.name=request.form.get('name')
    update_venue.city=request.form['city']
    update_venue.state=request.form['state']
    update_venue.phone=request.form['phone']
    update_venue.genres=request.form.getlist('genres')
    update_venue.facebook_link = request.form['facebook_link']
    update_venue.website = request.form['website']
    update_venue.seeking_artist= True if 'seeking_artist' in request.form else False
    update_venue.seeking_description = request.form['seeking_description']
    db.session.commit()
    flash('venue was successfully updated!')
  except:
    flash('An error occurred venue is not updated .')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  website = request.form.get('website')
  seeking_artist = True if 'seeking_talent' in request.form else False 
  seeking_description = request.form.get('seeking_description')

  artist = Artist(name=name,
  city=city, state=state, 
  phone=phone, 
  genres=genres, 
  facebook_link=facebook_link, 
  image_link=image_link, 
  website=website, 
  seeking_venue=seeking_artist,
  seeking_description=seeking_description)

  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.') 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #num_shows should be aggregated based on number of upcoming shows per venue.
 
  num_upcoming_show_venue=db.session.query(Venue.name,db.func.count(Show.start_time)).join(Show,Show.venue_id==Venue.id).group_by(Venue.name).filter(Show.start_time>datetime.now() ).all()
  num_upcoming_show_venue_=dict(num_upcoming_show_venue)

  data=[]
  shows=db.session.query(Show).all()
  for show in shows: 
    venue=db.session.query(Venue).get(show.venue_id)
    artist=db.session.query(Artist).get(show.artist_id)
    if venue.name in num_upcoming_show_venue_.keys():
      y=num_upcoming_show_venue_[venue.name]
    else:
      y=0
    data.append({
    "venue_id":venue.id,
    "venue_name":"{} upcoming_show in {}".format(y,venue.name),
    "artist_id":artist.id,
    "artist_name": artist.name,
    "artist_image_link":artist.image_link,
    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  venue_id = request.form.get('venue_id')
  artist_id = request.form.get('artist_id')
  start_time = request.form.get('start_time')
  
  show=Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
  
  try:
    db.session.add(show)
    db.session.commit()
    flash('An error occurred. Show could not be listed.')
  except:
    flash('Show was successfully listed!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
