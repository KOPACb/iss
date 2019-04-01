from app import db, login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, default=0)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
#    chapter = db.relationship('Chapter', backref='author', lazy='dynamic')
    chapter = db.relationship('Chapter', backref=db.backref("author"))
    formula = db.relationship('Formula', backref=db.backref("author"))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

chapter_files = db.Table('chapter_files',
    db.Column('file_id', db.Integer, db.ForeignKey('file.id')),
    db.Column('chapter_id', db.Integer, db.ForeignKey('chapter.id'))
)

class File(db.Model):
#    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    short_description = db.Column(db.String(255))
    filename = db.Column(db.String(150))
    url = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, default=datetime.utcnow)
#    chapters = db.relationship("Chapter", secondary=chapter_files )

    def __repr__(self):
        return '<File {}>'.format(self.filename)


class Chapter(db.Model):
#    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    short_description = db.Column(db.String(255))
    description = db.Column(db.Text)
    created = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#    user_id = db.relationship('User', backref=db.backref("chapters", lazy='dynamic'))
    files = db.relationship("File", secondary=chapter_files, backref=db.backref("chapters", lazy='dynamic'))




class Formula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    formula = db.Column(db.Text)
