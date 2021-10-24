from datetime import datetime
import os

from flask import render_template, url_for, redirect, request, session, g, abort, flash
from sqlalchemy import desc

from calblog import app, db, get_users
from .models import User, Post, Comment


# Logout routing
@app.route('/logout')
def logout():
    g.user = None
    # Clear session data
    session.pop('user_id', None)
    return redirect('login')

# Before each request, check if user is logged in
@app.before_request
def before_request():
    print(session)
    g.user = None
    if 'user_id' in session:
        user = [x for x in get_users() if x.id == session['user_id']][0]
        g.user = user

# cgoodale.com/login routing
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Clear session data
        session.pop('user_id', None)
        # Get username and password from the form
        username = request.form['username']
        password = request.form['password']
        try:
            # Check if username is in the users list
            user = [x for x in get_users() if x.username == username][0]
            # If user exists and the password matches
            if user and user.password == password:
                # Add the user to the session data
                session['user_id'] = user.id
                # Redirect to route that has the new_post function
                return redirect(url_for('new_post'))
        except:
            # If username or password does not match then run logout() function
            logout()
    else:
        # Else if request method equals GET go to login page
        return render_template('login.html')

# cgoodale.com main index routing
@app.route('/')
def home():
    return render_template('index.html')  # render a template

# cgoodale.com/links routing
@app.route('/links')
def links():
    return render_template('links.html')  # render a template

# cgoodale.com/blog routing
@app.route('/blog', methods=['GET'])
def blog():
        page = request.args.get('page', 1, type=int)
        # Display 5 most recent blog posts in descending order by date
        posts = Post.query.order_by(desc(Post.posted_on)).paginate(page, 5, False)
        # Query comments in order to show the related comments under each post
        comments = Comment.query.all()
        # Create the 'next page' and 'previous page' routes
        next_url = url_for('blog', page=posts.next_num) if posts.has_next else None
        prev_url = url_for('blog', page=posts.prev_num) if posts.has_prev else None
        return render_template('blog.html', posts=posts.items, comments=comments, next_url=next_url, prev_url=prev_url)  # render a template

# cgoodale.com/admin routing
@app.route('/admin', methods=['GET', 'POST'])
def new_post():
    # Check if user logged in
    if not g.user:
        return redirect('/login')
    elif request.method == 'POST':
        # Get post data from form fields and commit to database
        post_title = request.form['title']
        post_content = request.form['post']
        post_category = request.form['category']
        new_post = Post(title=post_title, content=post_content, category=post_category)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog')
    else:
        # Query and display all comments to display on admin page for approval
        comments = Comment.query.all()
        posts = Post.query.all()
        return render_template('admin.html', comments=comments, posts=posts)

@app.route('/comment', methods=['POST','GET'])
def comments():
    if request.method == 'POST':
        # Get comment data from form fields and commit to database   
        name = request.form['name']
        message = request.form['message']
        post_id = request.form['post-id']
        new_comment = Comment(name=name, message=message, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        # Flash message informing user of pending approval
        flash('Thank you for your comment. It is currently pending approval.')
        return redirect('/blog')

@app.route('/approval', methods=['GET', 'POST'])
def approval():
    # Check if user logged in
    if not g.user:
        return redirect('/login')
    else:
        if request.method == 'POST':
            # Get id of comment to approve or reject
            to_approve_id = request.form['comment-id']
            to_approve = Comment.query.get_or_404(to_approve_id)
            # Get id of the related post
            related_post = Post.query.get_or_404(to_approve.post_id)
            # If comment is approved
            if request.form['submit-button'] == "approve":
                # Change approved column for comment in database to True
                to_approve.approved = True
                # Add 1 to the comment_count column on the related post
                related_post.comment_count += 1
            else:
                # If comment is rejected delete from database
                db.session.delete(to_approve)
            db.session.commit()
            # Redirect to admin page
            return redirect('/admin')

# Post edit routing
@app.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    # Check if user logged in
    if not g.user:
        return redirect('/login')
    else:
        # Get id of post that is being edited
        to_edit = Post.query.get_or_404(id)
        if request.method == 'POST':
            # Get post data from form fields and commit to database
            to_edit.title = request.form['title']
            to_edit.content = request.form['post']
            db.session.commit()
            return redirect('/blog')
        else:
            return render_template('edit.html', post=to_edit)

# Post delete routing
@app.route('/blog/delete/<int:id>')
def delete(id):
    # Check if user logged in
    if not g.user:
        return redirect('/login')
    else:
        # Get id of post being deleted
        to_delete = Post.query.get_or_404(id)
        # Delete post and commit to database
        db.session.delete(to_delete)
        db.session.commit()
        return redirect('/blog')

# Comment delete routing
@app.route('/comment/delete/<int:id>')
def delete_comment(id):
    # Check if user logged in
    if not g.user:
        return redirect('/login')
    else:
        # Get id of comment
        to_delete = Comment.query.get_or_404(id)
        # Get id of related post
        related_post = Post.query.get_or_404(to_delete.post_id)
        # Subract 1 from comment_count of related post
        related_post.comment_count -= 1
        # Delete comment and commit to database
        db.session.delete(to_delete)
        db.session.commit()
        return redirect('/blog')