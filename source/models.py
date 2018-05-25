import os
from peewee import *
from urllib import parse

url = parse.urlparse(os.environ.get('DATABASE_URL'))
db = PostgresqlDatabase(database=url.path[1:],
                        user=url.username,
                        password=url.password,
                        host=url.hostname,
                        port=url.port)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(unique=True)


class Task(BaseModel):
    author = ForeignKeyField(User, backref='tasks')
    title = CharField(max_length=64)


class TaskCompleted(Task):
    author = ForeignKeyField(User, backref='completed')


class TaskDeleted(Task):
    author = ForeignKeyField(User, backref='deleted')
