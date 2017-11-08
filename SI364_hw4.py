## SI 364 - Fall 2017
## HW 4

## Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy

###from flask_migrate import Migrate, MigrateCommand

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecure'
## TODO SI364: Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## Your Postgres database should be your uniqname, plus HW4, e.g. "jczettaHW4" or "maupandeHW4"
app.config["SQLALCHEMY_DATABASE_URI"] = "laumurphHW4"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up Flask debug stuff
manager = Manager(app)
db = SQLAlchemy(app) # For database use

## Set up Shell context so it's easy to use the shell to debug
def make_shell_context():
    return dict(app=app, db=db, Tweet=Tweet, User=User, Hashtag=Hashtag) ## TODO SI364: Add your models to this shell context function so you can use them in the shell
    # TODO SI364: Submit a screenshot of yourself using the shell to make a query for all the Tweets in the database.
    # Filling this in will make that easier!

# Add function use to manager
manager.add_command("shell", Shell(make_context=make_shell_context))


#########
######### Everything above this line is important/useful setup, not problem-solving.
#########

##### Set up Models #####

## TODO SI364: Set up the following Model classes, with the respective fields (data types).

## The following relationships should exist between them:
# Tweet:User - Many:One
# Tweet:Hashtag - Many:Many

# - Tweet
class Tweet(db.Model):
    __tablename__ = "tweets"
    id = db.Column(db.Integer, primary_key=True) ## -- id (Primary Key)
    text = db.Column(db.String(285)) ## -- text (String, up to 285 chars)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) ## -- user_id (Integer, ID of user posted)
    hashtags = db.relationship('Hashtag', secondary=tweet_hashtags, backref=db.backref('tweets', lazy='dynamic'),lazy='dynamic')

# - User
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) ## -- id (Primary Key)
    twitter_username = db.Column(db.String(64), unique=True) ## -- twitter_username (String, up to 64 chars) (Unique=True)
    # will I need a tweets thing? possibly
# - Hashtag
class Hashtag(db.Model):
    __tablename__ = 'hashtags'
    id = db.Column(db.Integer, primary_key=True) ## -- id (Primary Key)
    text = db.Column(db.String, unique=True) ## -- text (Unique=True) #represents a single hashtag (like UMSI)

# Association Table: Tweet_Hashtag
# -- tweet_id
# -- hashtag_id
tweet_hashtags = db.Table('Tweet_Hashtags', db.Column('tweet_id', db.Integer, db.ForeignKey('tweets.id')), db.Column('hashtag_id', db.Integer, db.ForeignKey('hashtags.id')))
## NOTE: You'll have to set up database relationship code in either the Tweet table or the Hashtag table so that the association table for that many-many relationship will work properly!


##### Set up Forms #####

# TODO SI364: Fill in the rest of this Form class so that someone running this web app will be able to fill in information about tweets they wish existed to save in the database:

## -- tweet text
## -- the twitter username who should post it
## -- a list of comma-separated hashtags it should have

class TweetForm(FlaskForm):
    text = StringField("What is the text of your tweet? Note that if you include hashtags, to please separate them with commas.", validators=[Required()])
    username = StringField("What your twitter username?",validators=[Required()])
    submit = SubmitField('Submit')


##### Helper functions

### For database additions / get_or_create functions

## TODO SI364: Write get_or_create functions for each model -- Tweets, Hashtags, and Users.
## -- Tweets should be identified by their text and user id,(e.g. if there's already a tweet with that text, by that user, then return it; otherwise, create it)
## -- Users should be identified by their username (e.g. if there's already a user with that username, return it, otherwise; create it)
## -- Hashtags should be identified by their text (e.g. if there's already a hashtag with that text, return it; otherwise, create it)

## HINT: Your get_or_create_tweet function should invoke your get_or_create_user function AND your get_or_create_hashtag function. You'll have seen an example similar to this in class!

## NOTE: If you choose to organize your code differently so it has the same effect of not encounting duplicates / identity errors, that is OK. But writing separate functions that may invoke one another is our primary suggestion.
def get_or_create_user(db_session, username):
    user = db_session.query(User).filter_by(twitter_username=username).first()
    if user:
        return user
    else:
        user = User(twitter_username=username)
        db_session.add(user)
        db_session.commit()
        return user

def get_or_create_hashtag(db_session, hashtag_given):
    hashtag = db_session.query(Hashtag).filter_by(text = hashtag_given).first()
    if hashtag:
        return hashtag
    else:
        hashtag = Hashtag(text=hashtag_given)
        db_session.add(hashtag)
        db_session.commit()
        return hashtag

def get_or_create_tweet(db_session, input_text, username):
    tweet = db_session.query(Tweet).filter_by(text=input_text, user_id=get_or_create_user(db_session, username).id).first()
    if tweet:
        return tweet
    else:
        user = get_or_create_user(db_session, username)
        for text in input_text.split(','):
            if "#" in text.strip():
                pos = text.find('#')
                hashtag = get_or_create_hashtag(db_session, text.strip()[pos:])
        tweet = Tweet(text = input_text, user_id = user.id) # may need to add hashtag here, but probably not?
        db_session.add(tweet)
        db_session.commit()
        return tweet




##### Set up Controllers (view functions) #####

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

## Main route

@app.route('/', methods=['GET', 'POST'])
def index():
    pass
    ## TODO SI364: Fill in the index route as described.
    # A template index.html has been created and provided to render what this route needs to show -- YOU just need to fill in this view function so it will work.
    ## HINT: Check out the index.html template to make sure you're sending it the data it needs.

    # this is gonna need the tweets as well, like number of tweets sent as num_tweets
    # gonna need to render the form.

    # The index route should:
    # - Show the Tweet form.
    # - If you enter a tweet with identical text and username to an existing tweet, it should redirect you to the list of all the tweets and a message that you've already saved a tweet like that.

    ## ^ HINT: Invoke your get_or_create_tweet function
    ## ^ HINT: Check out the get_flashed_messages setup in the songs app you saw in class

    # This  main page should ALSO show links to pages in the app (see routes below) that:
    # -- allow you to see all of the tweets posted
    # -- see all of the twitter users you've saved tweets for, along with how many tweets they have in your database

    tweets = Tweet.query.all()
    num_tweets = len(tweets)
    form = TweetForm()
    if form.validate on submit():
        if db.session.query(Tweet).filter_by(text=form.text.data, user_id= (get_or_create_user(db.session, form.username.data).id)).first():
            flash("You've already saved a tweet by this user!")
        get_or_create_tweet(db.session, form.text.data, form.username.data)
        return redirect(url_for('see_all_tweets'))
    return render_template('index.html', form=form,num_tweets=num_tweets)

@app.route('/all_tweets')
def see_all_tweets():

    # TODO SI364: Fill in this view function so that it can successfully render the template all_tweets.html, which is provided.
    ## HINT: Check out the all_songs and all_artists routes in the songs app you saw in class.

    # looks like I'll want to send two things, first, is a list of tweets called all_tweets, and in the first position should be
    # the actual text
    # also need to send something called sg, which will contain the username. not sure how to call it sg though, since that suggests
    # that the username is the same for each one since it doesn't iterate? Should ask about that.
    all_tweets = []
    tweets = Tweet.query.all()
    for t in tweets:
        user = User.query.filter_by(id=t.user_id).first()
        all_tweets.append(t.text, user.twitter_username)
    return render_template('all_tweets.html', all_tweets=all_tweets)

@app.route('/all_users')
def see_all_users():

    # TODO SI364: Fill in this view function so it can successfully render the template all_users.html, which is provided. (See instructions for more detail.)
    ## HINT: Check out the all_songs and all_artists routes in the songs app you saw in class.

    # looks like I'll want to send a list of lists (or tuples) called usernames where the 
    # first item for each element is the username and the second is the number of tweets they have sent
    all_users = []
    users = User.query.all()
    for u in users:
        all_users.append(u.text, user.twitter_username)
    return render_template('all_tweets.html', all_tweets=all_tweets)

if __name__ == '__main__':
    db.create_all()
    manager.run() # Run with this: python main_app.py runserver
    # Also provides more tools for debugging
