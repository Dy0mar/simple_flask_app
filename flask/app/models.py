from sqlalchemy.sql.functions import current_timestamp

from . import db


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


user_to_project = db.Table('user_to_project',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)

    def __init__(self, **kwargs):
        for x in kwargs:
            if hasattr(self, x):
                setattr(self, x, kwargs[x])

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'active': self.active,
        }


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    users = db.relationship('User', secondary=user_to_project)
    created_at = db.Column(db.DateTime, default=current_timestamp())

    def __init__(self, *args, **kwargs):
        for x in kwargs:
            if hasattr(self, x):
                setattr(self, x, kwargs[x])
        super(Project, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Project id {}, name {}>'.format(self.id, self.name)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'users': [x.serialize for x in self.users],
            'created_at': dump_datetime(self.created_at),
        }

    @property
    def serialize_many2many(self):
        """
        Return object's relations in easily serializable format.
        NB! Calls many2many's serialize property.
        """
        return [item.serialize for item in self.many2many]





