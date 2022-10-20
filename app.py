from flask import Flask, request, render_template, redirect, flash, session
from models import db, connect_db, Users, Posts, Tags, PostTags

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://testuser:password@localhost:5432/blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)

with app.app_context():
    db.drop_all()
    db.create_all()

# HANDLE ROUTES
# Home Route - Redirect to /users
@app.route('/')
def home():
    return render_template('home.html')

# /users route - lists links for all the users in db
@app.route('/users')
def listusers():
    users = Users.query.all()
    return render_template('/users-list.html', users=users)

# /users/new route - handles both displaying the form to add a new user
# and sending post data to server
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

# this page displays info and posts about selected user
@app.route('/users/<int:user_id>')
def userinfo(user_id):
    user = Users.query.get(user_id)
    posts = Posts.query.filter(Posts.user_id == user_id)
    return render_template('user.html', user=user, posts=posts)

# handles form for editing user and sending post data to server
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

# handles post data for deleting user from db
@app.route('/users/<int:user_id>/delete', methods=['POST'])
def deleteuser(user_id):
    user = Users.query.get(user_id)
    for post in user.posts:
        for pt in post.p_tags:
            db.session.delete(pt)
        db.session.delete(post)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')

# handles form for creating a blog-post, and post data for adding blog-post data to db
@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def newpost(user_id):
    user = Users.query.get(user_id)
    tags = Tags.query.all()
    # ####
    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']
        sel_tags = request.form.getlist('tag')

        post = Posts(title=title, content=content, user_id=user_id)

        db.session.add(post)
        db.session.flush()

        for tag in sel_tags:
            tag_name = Tags.query.filter_by(name=tag).first()
            post_tag = PostTags(post_id=post.id, tag_id=tag_name.id)
            db.session.add(post_tag)
        
        db.session.commit()
        # return redirect(f'/users/{user_id}')
        return redirect(f'/users/{user_id}')
    # #####
    return render_template('new-post-form.html', user=user, tags=tags)
# 
# shows contents of selected post
@app.route('/posts/<int:post_id>')
def showpost(post_id):
    post = Posts.query.get(post_id)
    user = Users.query.get(post.user_id)
    tags = [p.name for p in post.tags]
    return render_template('post.html', post=post, user=user, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def editpost(post_id):
    post = Posts.query.get(post_id)
    tags = Tags.query.all()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        sel_tags = request.form.getlist('tag')

        post.title = title
        post.content = content

        delete_me = PostTags.query.filter_by(post_id=post_id)
        for d in delete_me:
            db.session.delete(d)

        for tag in sel_tags:
            tag_name = Tags.query.filter_by(name=tag).first()
            post_tag = PostTags(post_id=post_id, tag_id=tag_name.id)
            db.session.add(post_tag)

        db.session.commit()
        return redirect(f'/posts/{post.id}')

    return render_template('edit-post-form.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def deletepost(post_id):
    post = Posts.query.get(post_id)
    id = post.user_id
    for pt in post.p_tags:
        db.session.delete(pt)
    db.session.delete(post)
    db.session.commit()
    return redirect (f'/users/{id}')


@app.route('/tags')
def listtags():
    tags = Tags.query.all()
    return render_template('tags-list.html', tags=tags)


@app.route('/tags/<int:tag_id>')
def tagdetails(tag_id):
    tag = Tags.query.get(tag_id)
    posts = [p for p in tag.posts]
    return render_template('tag.html', tag=tag, posts=posts)


@app.route('/tags/new', methods=['GET', 'POST'])
def newtag():
    if request.method == 'POST':
        tag_name = request.form['tagname'].title()
        tag = Tags(name=tag_name)
        db.session.add(tag)
        db.session.commit()
        return redirect('/tags')

    return render_template('new-tag-form.html')


@app.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
def edittag(tag_id):
    tag = Tags.query.get(tag_id)
    if request.method == 'POST':
        tag.name = request.form['name']
        db.session.commit()
        return redirect('/tags')
    return render_template('/edit-tag-form.html', tag=tag)


@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def deletetag(tag_id):
    tag = Tags.query.get(tag_id)

    for pt in tag.p_tags:
        db.session.delete(pt)

    db.session.delete(tag)
    db.session.commit()
    
    return redirect('/tags')