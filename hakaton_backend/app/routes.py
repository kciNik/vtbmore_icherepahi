from flask import url_for, request, jsonify, session
from flask_login import current_user, login_user
from app.errors import bad_request, error_response
from flask_cors import cross_origin
from app.auth import token_auth
import random
from flask import request, jsonify
from app import app
from app import db
from app.models import User, Reward, Level, Dungeon, Boss, Task


@app.route('/')
@cross_origin()
def root():
    return 'Hello'

#  http POST http://localhost:5000/api/authorization login=ilya password=dog


@app.route('/api/authorization', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json() or {}
    if 'login' not in data or 'password' not in data:
        return bad_request('must include login and password fields')
    user = User.query.filter_by(login=data['login']).first()
    if user is None:
        return bad_request('please use a different login')
    if not user.check_password(data['password']):
        return bad_request('wrong password')
    login_user(user, remember=True)
    session['user_id'] = user.id
    response = jsonify(user.to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('root')
    return response


@app.route('/api/admin', methods=['GET'])
@cross_origin()
@token_auth.login_required
def get_admin():
    if token_auth.current_user().role == 'Admin':
        return jsonify(token_auth.current_user().to_dict())
    else:
        return error_response(403, 'user is not admin')


'''
@app.route('/api/create_task', methods=['GET'])
@cross_origin()
@token_auth.login_required
def create_task():
    if current_user.role != 'Admin':
        return error_response(403, 'user is not admin')
'''


# TODO

def get_current_user_id():
    return token_auth.current_user().id


"""
    ********************
        Reward block 
    ********************

[user, admin]

/create_reward
/reward/all
/reward/ID
/reward/edit
/reward/delete
"""


@app.route('/user/create_reward', methods=['POST'])
@cross_origin()
@token_auth.login_required
def create_reward():
    data = request.get_json() or {}

    reward = Reward(
        value_coins=data["value_coins"],
        value_nft=data["value_nft"],
        is_reward_collected=data["is_reward_collected"]
    )
    db.session.add(reward)
    db.session.commit()

    response = jsonify(reward.to_dict())
    response.status_code = 201
    return response


@app.route('/user/reward/<int:id_reward>', methods=['GET'])
@cross_origin()
@token_auth.login_required
def reward_get(id_reward):
    reward: Reward = Reward.query.filter_by(id=id_reward).first()

    response = jsonify(reward.to_dict())
    response.status_code = 200
    return response


@app.route('/user/reward/<int:id_reward>', methods=['PUT'])
@cross_origin()
@token_auth.login_required
def reward_edit(id_reward):
    data = request.get_json() or {}

    value_coins = data.get("value_coins", None)
    value_nft = data.get("value_nft", None)
    is_reward_collected = data.get("is_reward_collected", None)

    reward: Reward = Reward.query.filter_by(id=id_reward).first()

    if value_coins is not None:
        reward.value_coins = value_coins

    if value_nft is not None:
        reward.value_coins = value_nft

    if is_reward_collected is not None:
        reward.value_coins = is_reward_collected

    db.session.commit()

    response = jsonify(reward.to_dict())
    response.status_code = 201
    return response


@app.route('/user/reward/<int:id_reward>', methods=['DELETE'])
@cross_origin()
@token_auth.login_required
def reward_remove(id_reward):
    Reward.query.filter_by(id=id_reward).delete()
    db.session.commit()

    response = jsonify()
    response.status_code = 201
    return response


@app.route('/user/reward/all', methods=['GET'])
@cross_origin()
@token_auth.login_required
def reward_all():
    rewards = Reward.query.all()

    response = jsonify(
        {
            "rewards": [reward.to_dict for reward in rewards]
        }
    )
    response.status_code = 200
    return response


"""
    *************
        LEVEL 
    *************

[user]

/level
/level/ID/collect_reward
/level/all
/level_up
"""


@app.route('/level', methods=['GET'])
@cross_origin()
@token_auth.login_required
def get_current_level():
    user_id = get_current_user_id()

    user: User = User.query.filter_by(id=user_id).first()
    level: Level = [level for level in user.levels if level.is_done is False][0]

    response = jsonify(level.to_dict())
    response.status_code = 200
    return response


@app.route('/level/all', methods=['GET'])
@cross_origin()
@token_auth.login_required
def get_all_user_levels():
    user_id = get_current_user_id()

    user = User.query.filter_by(id=user_id).first()

    response = jsonify(
        {
            "levels": [level.to_dict for level in user.levels]
        }
    )
    response.status_code = 200
    return response


@app.route('/level/<int:id_level>/collect_reward', methods=['PUT'])
@cross_origin()
@token_auth.login_required
def collect_reward_for_level(id_level):
    user_id = get_current_user_id()

    user: User = User.query.filter_by(id=user_id).first()
    level: Level = Level.query.filter_by(id=id_level).first()

    status_code = 409

    if not level.reward.is_reward_collected:
        level.reward.is_reward_collected = True

        # TODO API NFT
        user.coins += level.reward.value_coins
        user.nft += level.reward.value_nft

        status_code = 200

    db.session.commit()

    response = jsonify()
    response.status_code = status_code
    return response


@app.route('/level/level_up', methods=['POST'])
@cross_origin()
@token_auth.login_required
def level_up():
    user_id = get_current_user_id()

    user: User = User.query.filter_by(id=user_id).first()
    current_level: Level = [level for level in user.levels if level.is_done is False][0]

    current_level.is_done = True

    """
        Once upon a time there was a...

        Нам нужно как-то автогенерить уровень
        Мы тупенькие, поэтому значения будут браться рандомно из раннее сгенерированных админом
        Мы берём реварды, данжи с id {level}0000
        Число уровней: 4 + 1 каждые 5 левелов

    """

    new_level = current_level.level + 1

    dungeons_for_new_level = Dungeon.query.filter(
        Dungeon.id >= new_level * 1000,
        Dungeon.id < (new_level + 1) * 1000
    ).all()

    rewards_for_new_level = Reward.query.filter(
        Reward.id >= new_level * 1000,
        Reward.id < (new_level + 1) * 1000
    ).all()

    level = Level(
        level=current_level.level + 1,
        total_tasks=4 + int(current_level.level / 5),
        completed_tasks=0,
        dungeon=Dungeon(random.choice(dungeons_for_new_level)),
        reward=Reward(random.choice(rewards_for_new_level)),
        is_done=False
    )

    db.session.add(level)
    db.session.commit()

    response = jsonify(level.to_dict())
    response.status_code = 200
    return response


"""
    ************
        BOSS 
    ************

[user]

/boss/ID
/boss/ID/collect_reward
"""


@app.route('/user/boss/<int:id_boss>', methods=['GET'])
@cross_origin()
@token_auth.login_required
def boss_get(id_boss):
    boss: Boss = Boss.query.filter_by(id=id_boss).first()

    response = jsonify(boss.to_dict())
    response.status_code = 200
    return response


@app.route('/user/boss/<int:id_boss>/collect_reward', methods=['PUT'])
@cross_origin()
@token_auth.login_required
def collect_reward_for_boss(id_boss):
    user_id = get_current_user_id()

    user: User = User.query.filter_by(id=user_id).first()
    boss: Boss = Boss.query.filter_by(id=id_boss).first()

    status_code = 409

    if not boss.reward.is_reward_collected:
        boss.reward.is_reward_collected = True

        # TODO API NFT
        user.coins += boss.reward.value_coins
        user.nft += boss.reward.value_nft

        status_code = 200

    db.session.commit()

    response = jsonify()
    response.status_code = status_code
    return response


"""
    ***************
        Dungeon 
    ***************

[user]

/dungeon/ID
/dungeon/ID/collect_reward
"""


@app.route('/user/dungeon/<int:id_dungeon>', methods=['GET'])
@cross_origin()
@token_auth.login_required
def dungeon_get(id_dungeon):
    dungeon: Dungeon = Dungeon.query.filter_by(id=id_dungeon).first()

    response = jsonify(dungeon.to_dict())
    response.status_code = 200
    return response


@app.route('/user/dungeon/<int:id_dungeon>/collect_reward', methods=['PUT'])
@cross_origin()
@token_auth.login_required
def collect_reward_for_dungeon(id_dungeon):
    user_id = get_current_user_id()

    user = User.query.filter_by(id=user_id).first()
    dungeon: Dungeon = Dungeon.query.filter_by(id=id_dungeon).first()

    status_code = 409

    if not dungeon.reward.is_reward_collected:
        dungeon.reward.is_reward_collected = True

        # TODO API NFT
        user.coins += dungeon.reward.value_coins
        user.nft += dungeon.reward.value_nft

        status_code = 200

    db.session.commit()

    response = jsonify()
    response.status_code = status_code
    return response


'''
    ************
        TEAM 
    ************

[user]

/create_team
/team/ID
/team/ID/edit
/team/ID/delete
/team/ID/add_participants
/team/ID/participants



@app.route('/user/create_team', methods=['POST'])
@cross_origin()
@token_auth.login_required
def create_team():
    data = request.get_json() or {}

    leaders = [
        User.query.filter_by(id=_id).first() for _id in data["leaders_id"]
    ]

    team = Team(
        name=data["name"],
        leaders=leaders,
    )
    db.session.add(team)
    db.session.commit()

    response = jsonify(team.to_dict())
    response.status_code = 201
    return response


@app.route('/user/team/<int:id_team>', methods=['GET'])
@cross_origin()
@token_auth.login_required
def team_get(id_team):
    team: Team = Team.query.filter_by(id=id_team).first()

    response = jsonify(team.to_dict())
    response.status_code = 200
    return response


@app.route('/user/team/<int:id_team>', methods=['PUT'])
@cross_origin()
@token_auth.login_required
def team_edit(id_team):
    data = request.get_json() or {}

    name = data.get("name", None)
    leaders_id = data.get("leaders_id", None)

    team: Team = Team.query.filter_by(id=id_team).first()

    if name is not None:
        team.value_coins = name

    if leaders_id is not None:
        team.value_coins = [
            User.query.filter_by(id=_id).first() for _id in data["leaders_id"]
        ]

    db.session.commit()

    response = jsonify(team.to_dict())
    response.status_code = 201
    return response


@app.route('/user/team/<int:id_team>', methods=['DELETE'])
@cross_origin()
@token_auth.login_required
def team_remove(id_team):
    Team.query.filter_by(id=id_team).delete()
    db.session.commit()

    response = jsonify()
    response.status_code = 201
    return response


@app.route('/user/team/<int:id_team>/participants', methods=['GET'])
@cross_origin()
@token_auth.login_required
def get_team_participants(id_team):
    participants = User.query.filter(User.teams.has(id=id_team))

    response = jsonify(
        {
            "participants": [participant.to_dict() for participant in participants]
        }
    )

    response.status_code = 201
    return response


@app.route('/user/team/<int:id_team>/add_participants', methods=['PUT'])
@cross_origin()
@token_auth.login_required
def team_add_participants(id_team):
    data = request.get_json() or {}

    team: Team = Team.query.filter_by(id=id_team).first()

    users_ids = data.get("users_ids", None)

    for user_id in users_ids:
        user = User.query.filter_by(id=user_id).first()
        user.teams.append(team)

    db.session.commit()

    response = jsonify(team.to_dict())
    response.status_code = 201
    return response
'''

"""
    ************
        TASK 
    ************

[user, admin]

/create_task
/task/ID
/task/ID/edit
/task/ID/delete
/task/all
/task/collect_reward
//!task/user_id

"""


@app.route('/user/create_task', methods=['POST'])
@cross_origin()
@token_auth.login_required
def create_task():
    data = request.get_json() or {}

    user_id = get_current_user_id()
    user = User.query.filter_by(id=user_id).first()

    task = Task(
        name=data["name"],
        description=data["description"],
        is_completed=False,
        is_boss=data["is_boss"],
        is_approved=user.role == "Admin",
        date=data["date"],  # or datetime
        reward_id=data["reward_id"],
        target=data["target"],  # TODO Please, не забудьте в апи фронту сказать, что тут oneOf enum, а то накроет всех
        author_id=user_id,
    )

    db.session.add(task)
    db.session.commit()

    response = jsonify(task.to_dict())
    response.status_code = 201
    return response


@app.route('/user/task/<int:id_task>', methods=['GET'])
@cross_origin()
@token_auth.login_required
def task_get(id_task):
    task: Task = Task.query.filter_by(id=id_task).first()

    response = jsonify(task.to_dict())
    response.status_code = 200
    return response


@app.route('/user/task/<int:id_task>', methods=['PUT'])
@cross_origin()
@token_auth.login_required
def task_edit(id_task):
    data = request.get_json() or {}

    name = data.get("name", None)
    description = data.get("description", None)
    is_completed = data.get("is_completed", None)
    is_boss = data.get("is_boss", None)
    is_approved = data.get("is_approved", None)
    reward_id = data.get("reward_id", None)
    author_id = data.get("author_id", None)
    target = data.get("target", None)

    task: Task = Task.query.filter_by(id=id_task).first()

    if name is not None:
        task.name = name

    if description is not None:
        task.description = description

    if is_completed is not None:
        task.is_completed = is_completed

    if is_boss is not None:
        task.is_boss = is_boss

    if is_approved is not None:
        task.is_approved = is_approved

    if reward_id is not None:
        task.reward_id = reward_id

    if author_id is not None:
        task.author_id = author_id

    if target is not None:
        task.target = target

    db.session.commit()

    response = jsonify(task.to_dict())
    response.status_code = 201
    return response


@app.route('/user/task/<int:id_task>', methods=['DELETE'])
@cross_origin()
@token_auth.login_required
def task_remove(id_task):
    Task.query.filter_by(id=id_task).delete()
    db.session.commit()

    response = jsonify()
    response.status_code = 201
    return response


@app.route('/user/task/all', methods=['GET'])
@cross_origin()
@token_auth.login_required
def get_task_all():
    tasks = Task.query.all()

    response = jsonify(
        {
            "tasks": [task.to_dict() for task in tasks]
        }
    )

    response.status_code = 201
    return response


@app.route('/user/task/<int:id_task>/collect_reward', methods=['PUT'])
@cross_origin()
@token_auth.login_required
def collect_reward_for_task(id_task):
    user_id = get_current_user_id()

    user = User.query.filter_by(id=user_id).first()
    task: Task = Task.query.filter_by(id=id_task).first()

    status_code = 409

    if not task.reward.is_reward_collected:
        task.reward.is_reward_collected = True

        # TODO API NFT task.author_id !!
        user.coins += task.reward.value_coins
        user.nft += task.reward.value_nft

        status_code = 200

    db.session.commit()

    response = jsonify()
    response.status_code = status_code
    return response


"""
    ************
        BOSS 
    ************

[admin]

/create_boss
/boss/ID @see user
/boss/ID/edit
/boss/ID/delete
/boss/all

"""


@app.route('/user/create_boss', methods=['POST'])
@cross_origin()
@token_auth.login_required
def create_boss():
    data = request.get_json() or {}

    tasks = [
        Task.query.filter_by(id == task_id).first() for task_id in data['tasks_ids']
    ]

    boss = Boss(
        name=data["name"],
        description=data["description"],
        tasks=tasks,
        reward=Reward.query.filter_by(id == data["reward_id"]).first
    )

    db.session.add(boss)
    db.session.commit()

    response = jsonify(boss.to_dict())
    response.status_code = 201
    return response

'''
@app.route('/user/boss/<int:id_boss>', methods=['GET'])
@cross_origin()
@token_auth.login_required
def boss_get(id_boss):
    boss: Boss = Boss.query.filter_by(id=id_boss).first()

    response = jsonify(boss.to_dict())
    response.status_code = 200
    return response
'''

@app.route('/user/boss/<int:id_boss>', methods=['PUT'])
@cross_origin()
@token_auth.login_required
def boss_edit(id_boss):
    data = request.get_json() or {}

    name = data.get("name", None)
    description = data.get("description", None)
    tasks_ids = data.get("tasks_ids", None)
    reward_id = data.get("reward_id", None)

    boss: Boss = Task.query.filter_by(id=id_boss).first()

    if name is not None:
        boss.name = name

    if description is not None:
        boss.description = description

    if tasks_ids is not None:
        tasks = [
            Task.query.filter_by(id == task_id).first() for task_id in data['tasks_ids']
        ]
        boss.tasks = tasks

    if reward_id is not None:
        boss.reward = Reward.query.filter_by(id == data["reward_id"]).first

    db.session.commit()

    response = jsonify(boss.to_dict())
    response.status_code = 201
    return response


@app.route('/user/boss/<int:id_boss>', methods=['DELETE'])
@cross_origin()
@token_auth.login_required
def boss_remove(id_boss):
    Boss.query.filter_by(id=id_boss).delete()
    db.session.commit()

    response = jsonify()
    response.status_code = 201
    return response


@app.route('/user/boss/all', methods=['GET'])
@cross_origin()
@token_auth.login_required
def get_boss_all():
    bosses = Boss.query.all()

    response = jsonify(
        {
            "bosses": [boss.to_dict() for boss in bosses]
        }
    )

    response.status_code = 201
    return response



