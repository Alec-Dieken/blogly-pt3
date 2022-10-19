from flask import Flask, request, render_template, redirect, flash, session
from models import db, connect_db, Users

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://testuser:password@localhost:5432/blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return redirect('/users')

@app.route('/users')
def listusers():
    users = Users.query.all()
    return render_template('/users-list.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        img_url = request.form['imgurl']
        user = Users(first_name=first_name, last_name=last_name, img_url=img_url)
        db.session.add(user)
        db.session.commit()
        return redirect('/users')

    return render_template('new-user-form.html')


@app.route('/users/<int:user_id>')
def userinfo(user_id):
    user = Users.query.get(user_id)
    return render_template('user.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edituser(user_id):

    user = Users.query.get(user_id)
    
    if request.method == 'POST':
        user.first_name = request.form['firstname']
        user.last_name = request.form['lastname']
        user.img_url = request.form['imgurl']
        db.session.commit()
        return redirect('/users')

    return render_template('edit-user-form.html', user=user)


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def deleteuser(user_id):
    user = Users.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')