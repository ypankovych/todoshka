import utils
from fsm import FSM
from telebot import TeleBot
from telebot.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup,
                           ReplyKeyboardMarkup)

bot = TeleBot('<token>')
states = FSM(default='create')
separator = '\n➖➖➖➖➖➖➖➖➖➖\n'


def availability(func):
    def wrapper(call):
        user_id = call.from_user.id
        task = states.get_extra_state(user_id, 'task')
        if task:
            return func(call, task)
        bot.delete_message(user_id, call.message.message_id)
        bot.answer_callback_query(call.id, 'Oops, i can\'t find task, try again')
    return wrapper


@bot.message_handler(commands=['start'])
def start(message):
    utils.create_user(message.chat.id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('My tasks', 'Create task')
    markup.add('Deleted tasks', 'Completed tasks')
    bot.reply_to(message, 'Hello {}'.format(message.from_user.first_name), reply_markup=markup)


@bot.message_handler(commands=['cancel'])
def cancel_creating(message):
    user_id = message.chat.id
    states.remove_state(user_id)
    bot.send_message(user_id, 'Canceled.')


@bot.message_handler(regexp='My tasks')
def get_all_tasks(message):
    user_id = message.chat.id
    all_tasks = utils.get_tasks(user_id)
    if all_tasks:
        return group_tasks(user_id, all_tasks)
    bot.send_message(user_id, 'Task list is empty')


@bot.message_handler(regexp='Completed tasks')
def completed_history(message):
    user_id = message.chat.id
    completed_tasks = utils.complete_history(user_id)
    if completed_tasks:
        bot.send_message(chat_id=user_id, parse_mode='Markdown',
                         text='*You have {} completed tasks:*\n\n{}'.format(len(completed_tasks),
                                                                            separator.join(completed_tasks)))
    else:
        bot.send_message(user_id, 'The list is empty')


@bot.message_handler(regexp='Deleted tasks')
def completed_history(message):
    user_id = message.chat.id
    completed_tasks = utils.delete_history(user_id)
    if completed_tasks:
        bot.send_message(chat_id=user_id, parse_mode='Markdown',
                         text='*You have {} deleted tasks:*\n\n{}'.format(len(completed_tasks),
                                                                          separator.join(completed_tasks)))
    else:
        bot.send_message(user_id, 'The list is empty')


@bot.message_handler(regexp='Create task')
def task_state(message):
    user_id = message.chat.id
    states.init_state(user_id)
    bot.send_message(user_id, 'Send the text of the task, no more than 64 characters. /cancel')


@bot.message_handler(func=lambda m: states.get_state(m.chat.id) == 'create')
def handle_task(message):
    content = message.text
    user_id = message.chat.id
    if len(content) <= 64:
        states.remove_state(user_id)
        utils.create_task(user_id, content)
        bot.send_message(user_id, 'Done.')
    else:
        bot.send_message(user_id, 'Symbol limit exceeded, try again.')


@bot.callback_query_handler(lambda call: call.data == 'done')
@availability
def complete(call, task):
    user_id = call.from_user.id
    utils.move_to_completed(user_id, task)
    bot.answer_callback_query(call.id, 'Done')
    bot.delete_message(user_id, call.message.message_id)


@bot.callback_query_handler(lambda call: call.data == 'delete')
@availability
def delete(call, task):
    user_id = call.from_user.id
    utils.move_to_deleted(user_id, task)
    bot.answer_callback_query(call.id, 'Done')
    bot.delete_message(user_id, call.message.message_id)


@bot.callback_query_handler(lambda call: True)
def task_settings(call):
    user_id = call.from_user.id
    states.add_extra_state(user_id, 'task', call.data)
    markup = InlineKeyboardMarkup()
    delete_btn = InlineKeyboardButton(text='Delete', callback_data='delete')
    done_btn = InlineKeyboardButton(text='Done', callback_data='done')
    markup.add(done_btn, delete_btn)
    bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                          text='*Options*', reply_markup=markup, parse_mode='Markdown')


def group_tasks(user_id, tasks):
    markup = InlineKeyboardMarkup()
    for task in tasks:
        button = InlineKeyboardButton(text=task, callback_data=task)
        markup.add(button)
    bot.send_message(user_id, '*Task list*', reply_markup=markup, parse_mode='Markdown')


if __name__ == '__main__':
    bot.polling()
