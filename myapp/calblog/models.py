from datetime import datetime
from calblog import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    category = db.Column(db.String(100), nullable=False)
    comment_count = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return self.title

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    def __repr__(self):
        return f'<User: {self.username}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=False, nullable=False)
    message = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    post = db.relationship('Post', backref=db.backref('posts',lazy=True, passive_deletes=True))
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return self.name

db.create_all()
db.session.commit()