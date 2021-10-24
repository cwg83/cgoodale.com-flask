from datetime import datetime
import os

from flask import render_template, url_for, redirect, request, session, g, abort, flash
from sqlalchemy import desc

from calblog import app, db, get_users
from .models import User, Post, Comment


@app.route('/logout')
def logout():
    g.user = None
    session.pop('user_id', None)
    return redirect('login')

@app.before_request
def before_request():
    print(session)
    g.user = None
    if 'user_id' in session:
        user = [x for x in get_users() if x.id == session['user_id']][0]
        g.user = user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']
        try:
            user = [x for x in get_users() if x.username == username][0]
            if user and user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('new_post'))
        except:
            logout()

        return redirect('login')

    return render_template('login.html')

@app.route('/')
def home():
    return render_template('index.html')  # render a template

@app.route('/links')
def links():
    return render_template('links.html')  # render a template

@app.route('/blog', methods=['GET'])
def blog():
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(desc(Post.posted_on)).paginate(page, 5, False)
        comments = Comment.query.all()
        next_url = url_for('blog', page=posts.next_num) if posts.has_next else None
        prev_url = url_for('blog', page=posts.prev_num) if posts.has_prev else None
        return render_template('blog.html', posts=posts.items, comments=comments, next_url=next_url, prev_url=prev_url)  # render a template

@app.route('/admin', methods=['GET', 'POST'])
def new_post():
    if not g.user:
        return redirect('/login')

    elif request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['post']
        post_category = request.form['category']
        new_post = Post(title=post_title, content=post_content, category=post_category)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog')
    else:
        comments = Comment.query.all()
        return render_template('admin.html', comments=comments)

@app.route('/comment', methods=['POST','GET'])
def comments():
    if request.method == 'POST':
            name = request.form['name']
            message = request.form['message']
            post_id = request.form['post-id']
            new_comment = Comment(name=name, message=message, post_id=post_id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Thank you for your comment. It is currently pending approval.')
            return redirect('/blog')

@app.route('/approval', methods=['GET', 'POST'])
def approval():
    if request.method == 'POST':
        to_approve_id = request.form['comment-id']
        to_approve = Comment.query.get_or_404(to_approve_id)
        related_post = Post.query.get_or_404(to_approve.post_id)
        if request.form['submit-button'] == "approve":
            to_approve.approved = True
            related_post.comment_count += 1
        else:
            db.session.delete(to_approve)
        db.session.commit()
        return redirect('/admin')

@app.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    to_edit = Post.query.get_or_404(id)
    if request.method == 'POST':
        to_edit.title = request.form['title']
        to_edit.content = request.form['post']
        db.session.commit()
        return redirect('/blog')
    else:
        return render_template('edit.html', post=to_edit)

@app.route('/blog/delete/<int:id>')
def delete(id):
    to_delete = Post.query.get_or_404(id)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/blog')

@app.route('/comment/delete/<int:id>')
def delete_comment(id):
    to_delete = Comment.query.get_or_404(id)
    related_post = Post.query.get_or_404(to_delete.post_id)
    related_post.comment_count -= 1
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/blog')