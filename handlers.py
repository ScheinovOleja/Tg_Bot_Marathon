import datetime
import os
import re
import sys

import django
from telebot.types import *

sys.path.append(f'{os.getcwd()}/tg_marathon/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tg_marathon.tg_marathon.settings')
django.setup()

from marathon.models import User, Photo, Measurement, Marathon, UserState, CategoryTasks, Tasks, Product, Buttons

start_buttons = [
    InlineKeyboardButton(text='Задания', callback_data='Tasks_start'),
    InlineKeyboardButton(text='Моя информация', callback_data='Info_start'),
    InlineKeyboardButton(text='Подсчитать количество ККАЛ', callback_data='Calculate_kcal_start'),
    InlineKeyboardButton(text='Пригласить друга', callback_data='Invite_friend_start'),
    InlineKeyboardButton(text='Ввести код приглашения', callback_data='Enter_code_start'),
    InlineKeyboardButton(text='Ввести код задания', callback_data='Code_task_start'),
    InlineKeyboardButton(text='Приобрести товар', callback_data='Buy_product_start')
]


def name_handler(text: str, context, markup):
    try:
        context['name'] = text.split(' ')[1]
        context['surname'] = text.split(' ')[0]
    except Exception as exc:
        logging.error(exc)
        return False, None
    markup.add(InlineKeyboardButton(text='Мужчина', callback_data='man_sex'))
    markup.add(InlineKeyboardButton(text='Женщина', callback_data='woman_sex'))
    return True, markup


def sex_handler(text: str, context, markup):
    return True, markup


def birthday_handler(text: str, context, markup):
    for button in start_buttons:
        markup.add(button)
    if re.match(r'\d\d[.]\d\d[.]\d\d\d\d', text):
        date = int(text.split('.')[0])
        month = int(text.split('.')[1])
        if 31 >= date > 0 < month <= 12:
            try:
                context['birthday'] = datetime.datetime.strptime(text, "%d.%m.%Y")
            except ValueError as exc:
                logging.error(exc)
                return False, None
            return True, markup
        else:
            return False, None
    else:
        return False, None


def breast_handler_before(text: str, context, markup):
    try:
        if float(text):
            context['breast_before'] = float(text)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, None


def waist_handler_before(text: str, context, markup):
    try:
        if float(text):
            context['waist_before'] = float(text)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, None


def femur_handler_before(text: str, context, markup):
    try:
        if float(text):
            context['femur_before'] = float(text)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, None


def weight_handler_before(text: str, context, markup):
    for button in start_buttons:
        markup.add(button)
    try:
        if float(text):
            context['weight_before'] = float(text)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, markup


def breast_handler_after(text: str, context, markup):
    try:
        if float(text):
            context['breast_after'] = float(text)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, None


def waist_handler_after(text: str, context, markup):
    try:
        if float(text):
            context['waist_after'] = float(text)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, None


def femur_handler_after(text: str, context, markup):
    try:
        if float(text):
            context['femur_after'] = float(text)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, None


def weight_handler_after(text: str, context, markup):
    for button in start_buttons:
        markup.add(button)
    try:
        if float(text):
            context['weight_after'] = float(text)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, None


def calculate_weight_handler(text: str, context, markup):
    try:
        if float(text):
            context['calculate_weight'] = float(text)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, None


def calculate_height_handler(text: str, context, markup):
    buttons = [
        InlineKeyboardButton(text='Не занимаюсь спортом', callback_data='Level_activity_none'),
        InlineKeyboardButton(text='Легкие тренировки(1-2)', callback_data='Level_activity_one-two'),
        InlineKeyboardButton(text='Умеренная активность(3-5)', callback_data='Level_activity_three-five'),
        InlineKeyboardButton(text='Повышенная активность(6-7)', callback_data='Level_activity_six-seven'),
        InlineKeyboardButton(text='Профессиональный спорт(каждый день)', callback_data='Level_activity_professional'),
    ]
    try:
        if float(text):
            context['calculate_height'] = float(text)
            for btn in buttons:
                markup.add(btn)
            return True, markup
    except Exception as exc:
        logging.error(exc)
        return False, None
