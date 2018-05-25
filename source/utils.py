from models import *

LAST_ITEMS = slice(None, -11, -1)


def create_user(user_id):
    user, created = User.get_or_create(user_id=user_id)


def get_user(user_id):
    user = User().select().where(User.user_id == user_id).get()
    return user


def create_task(user_id, title):
    user = get_user(user_id)
    task = Task(author=user, title=title)
    task.save()


def move_to_deleted(user_id, title):
    user = get_user(user_id)
    delete_task(user, title)
    task = TaskDeleted(title=title, author=user)
    task.save()


def delete_task(user, title):
    task = user.tasks.select().where(Task.title == title).get()
    task.delete_instance()


def move_to_completed(user_id, title):
    user = get_user(user_id)
    delete_task(user, title)
    task = TaskCompleted(title=title, author=user)
    task.save()


def delete_history(user_id):
    user = get_user(user_id)
    tasks = user.deleted.select()
    return [task.title for task in tasks][LAST_ITEMS]


def complete_history(user_id):
    user = get_user(user_id)
    tasks = user.completed.select()
    return [task.title for task in tasks][LAST_ITEMS]


def get_tasks(user_id):
    user = get_user(user_id)
    tasks = user.tasks.select()
    return [task.title for task in tasks]
