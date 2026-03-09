
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

app.secret_key = "flames_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200), default="default.png")

class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    person1 = db.Column(db.String(100))
    person2 = db.Column(db.String(100))
    result = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=datetime.utcnow)

def calculate_flames(name1, name2):

    name1 = name1.lower().replace(" ", "")
    name2 = name2.lower().replace(" ", "")

    list1 = list(name1)
    list2 = list(name2)

    for char in name1:
        if char in list2:
            list1.remove(char)
            list2.remove(char)

    count = len(list1) + len(list2)

    flames = ["Friends", "Love", "Affection", "Marriage", "Enemy", "Siblings"]

    while len(flames) > 1:
        split = (count % len(flames)) - 1

        if split >= 0:
            right = flames[split + 1:]
            left = flames[:split]
            flames = right + left
        else:
            flames.pop()

    return flames[0]

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username,password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('game'))

    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        new_user = User(username=username,password=password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/game', methods=['GET','POST'])
def game():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    result = None

    if request.method == 'POST':

        name1 = request.form['person1']
        name2 = request.form['person2']

        result = calculate_flames(name1,name2)

        history = GameHistory(
            user_id=session['user_id'],
            person1=name1,
            person2=name2,
            result=result
        )

        db.session.add(history)
        db.session.commit()

    return render_template('game.html', result=result)

@app.route('/profile', methods=['GET','POST'])
def profile():

    user = User.query.get(session['user_id'])

    if request.method == 'POST':

        file = request.files['photo']

        if file:

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

            file.save(filepath)

            user.profile_pic = file.filename

            db.session.commit()

    return render_template('profile.html', user=user)

@app.route('/history')
def history():

    games = GameHistory.query.filter_by(user_id=session['user_id']).all()

    return render_template('history.html', games=games)

@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
