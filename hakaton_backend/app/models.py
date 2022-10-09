from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from flask_login import UserMixin
from app import login, db
import base64
from datetime import datetime, timedelta
import os
from sqlalchemy import Table, Column, ForeignKey
import enum


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


user_task = db.Table('user_task',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('task_id', db.Integer, db.ForeignKey('task.id'))
                     )

boss_task = db.Table('boss_task',
                     db.Column('boss_id', db.Integer, db.ForeignKey('boss.id')),
                     db.Column('task_id', db.Integer, db.ForeignKey('task.id'))
                     )
'''
team_for_user = db.Table(
    'team_for_user',
    db.Column("id", db.ForeignKey("User.id")),
    db.Column("id", db.ForeignKey("Team.id")),
)
'''

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    login = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(1000))
    nft = db.Column(db.Integer, default=0)  # float?
    coins = db.Column(db.Integer, default=0)
    levels = db.relationship('Level', backref='executor', lazy='dynamic')
    tasks = db.relationship('Task', secondary=user_task, backref='users')
    #teams = db.relationship("Team", secondary=team_for_user)
    role = db.Column(db.String(120), index=True)  # enum Leader, User, Admin
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'login': self.login,
            'nft': self.nft,
            'coins':  self.coins,
            'levels': list(self.levels),
            'tasks': list(self.tasks),
            'role': self.role,
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level = db.Column(db.Integer)  # must be
    total_tasks = db.Column(db.Integer)
    completed_tasks = db.Column(db.Integer, default=0)
    dungeon = db.relationship('Dungeon', uselist=False, backref='level')
    is_done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reward = db.relationship('Reward', uselist=False, backref='level')

    def __repr__(self):
        return '<Level {}, executor {}>'.format(self.level, self.executor)

    def to_dict(self):
        data = {
            'id': self.id,
            'level': self.level,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'dungeon_id': self.dungeon.id,
            'is_done': self.is_done,
            'reward_id': self.reward.id
        }
        return data

'''
leader_for_team = Table(
    "leader_for_team",
    Column("id", ForeignKey("User.id")),
    Column("id", ForeignKey("Team.id")),
)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    leaders = db.relationship("User", secondary=team_for_user)

    def __repr__(self):
        return '<Team {}, executor {}>'.format(self.name, self.executor)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.level,
            'leaders': [leader.to_dict for leader in self.leaders]
        }
        return data
'''


class Dungeon(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(500))
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    bosses = db.relationship('Boss', backref='dungeon', lazy='dynamic')

    def __repr__(self):
        return '<Dungeon {}, level {}>'.format(self.name, self.level)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'bosses': [boss.to_dict() for boss in self.bosses]
        }
        return data


class Boss(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(500))
    tasks = db.relationship('Task', secondary=boss_task, backref='bosses')
    #  image
    dungeon_id = db.Column(db.Integer, db.ForeignKey('dungeon.id'))
    reward = db.relationship('Reward', uselist=False, backref='boss')

    def __repr__(self):
        return '<Boss {}, dungeon {}>'.format(self.name, self.dungeon)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'tasks': [task.to_dict() for task in self.tasks],
            'reward_id': self.reward.id
        }
        return data


class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value_coins = db.Column(db.Integer, default=0)
    value_nft = db.Column(db.Integer, default=0)
    #  image
    is_reward_collected = db.Column(db.Boolean, default=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    boss_id = db.Column(db.Integer, db.ForeignKey('boss.id'))  # нормально что тут None?
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    def __repr__(self):
        return '<Reward {}, level {}, boss {}>'.format(self.id, self.level, self.boss)

    def to_dict(self):
        data = {
            'id': self.id,
            'value_coins': self.value_coins,
            'value_nft': self.value_nft,
            'is_reward_collected': self.is_reward_collected
        }
        return data


class TargetTaskEnum(enum.Enum):
    """
    Enum for task target
    """
    Any = "Any"
    TeamsOnly = "TeamsOnly"
    Individual = "Individual"


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(500))
    is_completed = db.Column(db.Boolean, default=False)
    reward = db.relationship('Reward', uselist=False, backref='task')
    #  task_type - enum
    is_boss = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    target = db.Column(db.Enum(TargetTaskEnum), default=TargetTaskEnum.Any)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Task {}, reward {}>'.format(self.name, self.reward)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_completed': self.is_completed,
            'is_boss': self.is_boss,
            'is_approved': self.is_approved,
            'date': self.date,
            'reward_id': self.reward.id,
            'author_id': self.author_id,
            'target': self.target.value
        }
        return data
