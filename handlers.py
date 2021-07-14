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


def get_buttons(buttons='start', markup=None, chat_id=None):
    btns = Buttons.objects.all().first()
    if buttons == 'start':
        texts = ['Tasks_start', 'Info_start', 'Calculate_kcal_start', 'Invite_friend_start', 'Enter_code_start',
                 'Code_task_start', 'Buy_product_start']
        for text in texts:
            caption = getattr(btns, text.lower())
            markup.add(InlineKeyboardButton(text=caption, callback_data=text))
    elif buttons == 'information':
        texts = ['Measurement_marathon_start',
                 'Photos_marathon_start',
                 'Stats_all']
        for text in texts:
            caption = getattr(btns, text.lower())
            markup.add(InlineKeyboardButton(text=caption, callback_data=text))
    elif 'photo' in buttons:
        callbacks = ['photo_front_before', 'photo_sideways_before', 'photo_back_before',
                     'photo_front_after',
                     'photo_sideways_after', 'photo_back_after']
        if '_get' in buttons:
            photo = Photo.objects.get_or_none(tg_id=chat_id)
            for callback in callbacks:
                image = getattr(photo, callback)
                if not image:
                    continue
                else:
                    btn_text = getattr(btns, callback)
                    markup.add(InlineKeyboardButton(text=btn_text,
                                                    callback_data=f'{callback}_get'))
        if '_add' in buttons:
            marathon = Marathon.objects.get_marathon()
            if marathon.send_measurements_before:
                before_buttons = [btn for btn in callbacks if '_before' in btn]
                for btn in before_buttons:
                    btn_text = getattr(btns, btn)
                    markup.add(InlineKeyboardButton(text=btn_text, callback_data=f'{btn}_add'))
            if marathon.send_measurements_after:
                before_buttons = [btn for btn in callbacks if '_after' in btn]
                for btn in before_buttons:
                    btn_text = getattr(btns, btn)
                    markup.add(InlineKeyboardButton(text=btn_text, callback_data=f'{btn}_add'))
    elif 'add' in buttons:
        marathon = Marathon.objects.get_marathon()
        callbacks = ['Add_before', 'Add_after']
        for callback in callbacks:
            btn_text = getattr(btns, callback)
            markup.add(InlineKeyboardButton(text=btn_text, callback_data=callback))
        if marathon.send_measurements_before:
            markup.add(InlineKeyboardButton(text='Ввести замеры ДО', callback_data='Add_before'))
        if marathon.send_measurements_after:
            markup.add(InlineKeyboardButton(text='Ввести замеры ПОСЛЕ', callback_data='Add_after'))
    back_button = InlineKeyboardButton(text=f'{getattr(btns, "back")}',
                                            callback_data='back')
    main_menu = InlineKeyboardButton(text=f'{getattr(btns, "main_menu")}',
                                          callback_data='main_menu')
    return markup


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
    try:
        if context['sex']:
            return True, markup
    except Exception as exc:
        markup.add(InlineKeyboardButton(text='Мужчина', callback_data='man_sex'))
        markup.add(InlineKeyboardButton(text='Женщина', callback_data='woman_sex'))
        return False, markup


def birthday_handler(text: str, context, markup):
    markup = get_buttons('start', markup)
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
    markup = get_buttons('start', markup)
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
    markup = get_buttons('start', markup)
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
