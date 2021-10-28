from datetime import datetime
from calblog import db

# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, nullable=False)
    categories = db.relationship('Categories', backref=db.backref('post',lazy=True, passive_deletes=True))
    # Count of related comments
    comment_count = db.Column(db.Integer, nullable=False, default=0)
    comments = db.relationship('Comment', backref=db.backref('post',lazy=True, passive_deletes=True))

    def __repr__(self):
        return self.id

# User model
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    def __repr__(self):
        return f'<User: {self.username}>'

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=False, nullable=False)
    message = db.Column(db.Text, nullable=False)
    # id of related blog post
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return self.name

# Category model
class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # id of related blog post
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.category

db.create_all()
db.session.commit()