from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from flask_login import UserMixin
from app import login, db


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


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    login = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    nft = db.Column(db.Integer, default=0)  # float?
    coins = db.Column(db.Integer, default=0)
    levels = db.relationship('Level', backref='executor', lazy='dynamic')
    tasks = db.relationship('Task', secondary=user_task, backref='users')
    role = db.Column(db.String(120), index=True)  # enum Leader, User, Admin

    def __repr__(self):
        return '<User {}, task1 {}>'.format(self.name, self.tasks[0])

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
            'levels': self.levels,
            'tasks': self.tasks,
            'role': self.role,
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer)  # must be
    total_tasks = db.Column(db.Integer)
    completed_tasks = db.Column(db.Integer, default=0)
    dungeon = db.relationship('Dungeon', uselist=False, backref='level')
    is_done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reward = db.relationship('Reward', uselist=False, backref='level')

    def __repr__(self):
        return '<Level {}, executor {}>'.format(self.level, self.executor)


class Dungeon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(500))
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    bosses = db.relationship('Boss', backref='dungeon', lazy='dynamic')

    def __repr__(self):
        return '<Dungeon {}, level {}>'.format(self.name, self.level)


class Boss(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(500))
    tasks = db.relationship('Task', secondary=boss_task, backref='bosses')
    #  image
    dungeon_id = db.Column(db.Integer, db.ForeignKey('dungeon.id'))
    reward = db.relationship('Reward', uselist=False, backref='boss')

    def __repr__(self):
        return '<Boss {}, dungeon {}>'.format(self.name, self.dungeon)


class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value_coins = db.Column(db.Integer, default=0)
    value_nft = db.Column(db.Integer, default=0)
    #  image
    is_reward_collected = db.Column(db.Boolean, default=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    boss_id = db.Column(db.Integer, db.ForeignKey('boss.id'))  # нормально что тут None?
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    def __repr__(self):
        return '<Reward {}, level {}, boss {}>'.format(self.id, self.level, self.boss)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(500))
    is_completed = db.Column(db.Boolean, default=False)
    reward = db.relationship('Reward', uselist=False, backref='task')
    #  task_type - enum
    is_boss = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    #  teams
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Task {}, reward {}>'.format(self.name, self.reward)




