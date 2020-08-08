
from werkzeug.security import generate_password_hash, check_password_hash

from project import db


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String(128))

    tags = db.relationship('Tag', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, user_name):
        self.username = user_name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Tag(db.Model):

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    tagname = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    works = db.relationship('Work', backref='tag', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, tag_name, user):
        self.tagname = tag_name
        self.user = user

    @staticmethod
    def exist(tag_name, user):
        tag = Tag.query.filter_by(tagname=tag_name).filter_by(user_id=user.id).first()
        if tag is not None:
            return True
        else:
            return False

    @staticmethod
    def get_tag_by_name(tag_name, user):
        return Tag.query.filter_by(tagname=tag_name).filter_by(user_id=user.id).first()


class Work(db.Model):

    __tablename__ = 'works'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    tag_id = db.Column( db.Integer, db.ForeignKey('tags.id'))

    def __init__(self, start_time, end_time, tag):
        self.start_time = start_time
        self.end_time = end_time
        self.tag = tag
