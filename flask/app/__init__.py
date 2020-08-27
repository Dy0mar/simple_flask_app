# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime
from random import randint

from flask import Flask, g, request
from flask import jsonify
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import func, desc

from .config import ProductionConfig, DevelopmentConfig
from .utils import random_date

from dotenv import load_dotenv, find_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))


def get_config():
    if os.environ.get('FLASK_ENV') == 'production':
        return ProductionConfig
    if os.environ.get('FLASK_ENV') == 'development':
        return DevelopmentConfig


env = os.path.join(basedir, '.env')
load_dotenv(find_dotenv(filename=env, raise_error_if_not_found=True))

app = Flask(__name__)
app.config.from_object(get_config())
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from .models import User, Project


def init_db():
    try:
        rows = int(os.environ.get('GENERATE_TEST_ROWS', 0))
    except (ValueError, TypeError):
        return False

    if rows == 0:
        print('GENERATE_TEST_ROWS == 0')
        return False

    db.drop_all()
    db.create_all()

    users = [f'user_{x}' for x in range(1, 11)]
    users.append('admin')

    user_list = []
    for i, name in enumerate(users, start=1):
        user = User(
            id=i, username=name, email=f'{name}@example.com',
            password='password', active=True
        )
        user_list.append(user)
    db.session.add_all(user_list)
    db.session.commit()

    d1 = datetime.strptime('2020-01-01 0:30:00', '%Y-%m-%d %H:%M:%S')
    d2 = datetime.strptime('2021-01-01 0:30:00', '%Y-%m-%d %H:%M:%S')

    for row_id in range(1, rows+1):

        # add some users to project 0 - len(user_list)
        tmp_user_list = user_list.copy()
        count_users_in_project = randint(0, 5)
        users_in_project = []

        for x in range(0, count_users_in_project):
            index = randint(0, len(tmp_user_list)-1)
            user_in_project = tmp_user_list.pop(index)
            users_in_project.append(user_in_project)

        project = Project(
            id=row_id,
            name=f'Project_{row_id}',
            created_at=random_date(d1, d2)
        )
        if users_in_project:
            project.users.extend(users_in_project)

        db.session.add(project)
    db.session.commit()


if app.config.get('GENERATE'):
    print('Initialized the database.')
    init_db()
else:
    db.create_all()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/v1.0/top/users', methods=['GET'])
def get_top():
    items = db.session.query(
        User.id,
        func.count(Project.id).label('total')
    ).join(Project.users).group_by(User).order_by(desc('total')).limit(10).all()

    return jsonify(top10=items)


@app.route('/api/v1.0/projects', methods=['GET'])
@app.route('/api/v1.0/projects/<int:page>', methods=['GET'])
def get_projects(page=1):
    qs = Project.query

    sorted_date = request.args.get("sorted_date", None)

    if sorted_date in ('ask', 'desc'):
        if sorted_date == 'ask':
            qs = qs.order_by(Project.created_at.asc())
        else:
            qs = qs.order_by(Project.created_at.desc())

    per_page = app.config.get('DEFAULT_PER_PAGE')

    projects = qs.paginate(page, per_page, False)

    return jsonify(
        page=page,
        total=projects.total,
        list=[i.serialize for i in projects.items]
    )



