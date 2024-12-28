from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# user - course relationship table
favorites = db.Table('favorites',
                     db.Column('user_id', db.Integer, db.ForeignKey(
                         'user.id'), primary_key=True),
                     db.Column('course_id', db.Integer, db.ForeignKey(
                         'course.id'), primary_key=True),
                     db.Column('favorited_at', db.DateTime,
                               default=datetime.utcnow)
                     )

# course - like relationship table
likes = db.Table('likes',
                 db.Column('user_id', db.Integer, db.ForeignKey(
                     'user.id'), primary_key=True),
                 db.Column('course_id', db.Integer, db.ForeignKey(
                     'course.id'), primary_key=True)
                 )

# course - tag relationship table
course_tags = db.Table('course_tags',
                       db.Column('course_id', db.Integer, db.ForeignKey(
                           'course.id'), primary_key=True),
                       db.Column('tag_id', db.Integer, db.ForeignKey(
                           'tag.id'), primary_key=True)
                       )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    # weather the user is a manager
    role = db.Column(db.String(64), default='student')

    # user favorite courses
    favorited_courses = db.relationship('Course',
                                        secondary=favorites,
                                        lazy='dynamic',
                                        backref=db.backref('favorited_by', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # like count
    likes_count = db.Column(db.Integer, default=0)

    # the video/image url
    video_url = db.Column(db.String(255))
    image_url = db.Column(db.String(255))

    # like by users
    liked_by = db.relationship('User',
                               secondary='likes', lazy='dynamic',
                               backref=db.backref('liked_courses', lazy='dynamic'))

    # the tags
    tags = db.relationship('Tag',
                           secondary=course_tags,
                           lazy='dynamic',
                           backref=db.backref('courses', lazy='dynamic'))

    # the comments
    comments = db.relationship('Comment', backref='course', lazy='dynamic')

    @property
    def comment_count(self):
        return len(self.comments)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)

# comment of the crouse


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(
        db.Integer, db.ForeignKey('course.id'), nullable=True)

    user = db.relationship('User', backref=db.backref('comments', lazy=True))
