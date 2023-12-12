from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, default="")
    password_hash = db.Column(db.String(256), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, comment='date of registation')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, comment='last seen user in online')
    role_id = db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))
    role = db.relationship('Role', backref='owners')

    def __repr__(self) -> str:
        return f'User {self.id}, Username: {self.username}, email: {self.email}, date: {self.date},' \
               f' last_seen: {self.last_seen}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))


class Cat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256))
    breed = db.Column(db.String(64))
    link = db.Column(db.String, nullable=False)
    photo_link = db.Column(db.String)
