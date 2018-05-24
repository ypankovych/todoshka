from peewee import *

db = SqliteDatabase('tasks.db')


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


# Run before the first start
# db.create_tables([User, Task, TaskCompleted, TaskDeleted])
