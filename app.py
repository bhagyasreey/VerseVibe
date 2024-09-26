from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import re
import os
import lyricsgenius

import lyricsgenius
token = "M6OOR7mmplrIptKID6t0wiwsBFzhezmhY9XZPc6c2VjicebBw-GLf82ijy5MqkZm"
genius = lyricsgenius.Genius(token)


current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "2lK3&Uj@q8#p$E5*9aXrGz1!bF7sT0w"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.db")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

@app.route('/')
def index():
    chart=genius.charts(time_period='day')
    return render_template('index.html', chart=chart)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = Account.query.filter_by(username=username, password=password).first()
        if account:
            session['loggedin'] = True
            session['id'] = account.id
            session['username'] = account.username
            login_msg = 'Logged in successfully!'
            return render_template('index.html', msg=login_msg)
        else:
            login_msg = 'Incorrect username / password!'
    return render_template('login.html', login_msg=login_msg, register_msg='')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    register_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_account = Account.query.filter_by(username=username).first()
        if not username or not password or not email:
            register_msg = 'Please fill out the form!'
        elif existing_account:
            register_msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            register_msg = 'Invalid email address!'
        else:
            new_account = Account(username=username, password=password, email=email)
            db.session.add(new_account)
            db.session.commit()
            register_msg = 'You have successfully registered!'
    return render_template('login.html', login_msg='', register_msg=register_msg)


@app.route('/search_results', methods=['GET'])
def search_results():
    search_term = request.args.get('search_term')
    search_value= request.args.get('search_value')
    search_artist = request.args.get('search_artist')
    if search_value=="song" and search_artist!='':
        results = genius.search_songs(search_term, artist=search_artist)
    elif search_value=="album" and search_artist!='':
        results = genius.search_albums(search_term, artist=search_artist)
    elif search_value=="artist":
        results = genius.search_artists(search_term)
    elif search_value=="lyric":
        results = genius.search_lyrics(search_term)
    else:
        results = genius.search(search_term, type_=search_value)
    return render_template('search_results.html', results=results)

if __name__ == "__main__":
    app.run()
