import datetime
import os
import sys
import time
from copy import copy
import requests
import handlers
from config import *
import django
import telebot as tb
from telebot.types import *

sys.path.append(f'{os.getcwd()}/tg_marathon/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tg_marathon.tg_marathon.settings')
django.setup()

from marathon.models import User, Photo, Measurement, Marathon, UserState, CategoryTasks, Tasks, Product, Buttons, \
    Config


def log_error(f):
    """
    Обработчик ошибок
    :param f:
    :return:
    """

    if not os.path.isdir(f'{os.getcwd()}/Logs'):
        os.mkdir(f'{os.getcwd()}/Logs')
    logging.basicConfig(level=logging.ERROR, filename=f'{os.getcwd()}/Logs/logs_error.log',
                        format='%(asctime)s %(levelname)s:%(message)s')

    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as exc:
            logging.error(f'Error - {exc}')

    return inner


class BotMarathon:

    def __init__(self):
        self.bot = tb.TeleBot(token=getattr(Config.objects.all().first(), 'token_bot'), num_threads=2)
        self.back_button = InlineKeyboardButton(text=f'{getattr(Buttons.objects.all().first(), "back")}',
                                                callback_data='back')
        self.main_menu = InlineKeyboardButton(text=f'{getattr(Buttons.objects.all().first(), "main_menu")}',
                                              callback_data='main_menu')
        self.def_bots()
        self.image = None
        self.back_button = None
        self.main_menu = None

    @log_error
    def run(self):
        while True:
            try:
                self.bot.polling(none_stop=True)
            except Exception as exc:
                self.bot.stop_polling()
                logging.error(exc)
                continue

    def def_bots(self):
        """
        Хранит в себе весь хаос бота
        :return:
        """

        @log_error
        @self.bot.message_handler(commands=['register'])
        def register(message):
            register_user(message, 'register')

        @log_error
        @self.bot.message_handler(commands=['clear'])
        def clear(message):
            """
            Очистка истории сообщений
            """
            count_time = int(message.text.split()[1])
            message_id = int(message.message_id)
            deadline = time.monotonic() + count_time
            while time.monotonic() < deadline:
                try:
                    message_id -= 1
                    self.bot.delete_message(message.chat.id, message_id)
                except:
                    continue

        @self.bot.message_handler(commands=['start'])
        @log_error
        def start(message):
            chat_id = message.chat.id
            user = User.objects.get_or_none(tg_id=message.chat.id)
            if user:
                markup = InlineKeyboardMarkup(row_width=2)
                markup = get_buttons('start', markup)
                self.bot.send_message(
                    text=f"Привет {user.name}!\nВыберите пункт меню:",
                    chat_id=chat_id,
                    reply_markup=markup
                )
                return
            else:
                register_user(message, 'start')

        @log_error
        def edit_menu_user(call):
            user = User.objects.get(tg_id=call.message.chat.id)
            if 'Tasks_start' == call.data:
                user.menu = 'category_task_menu'
            elif 'Category_' in call.data:
                user.menu = 'tasks_menu'
            elif 'Task_' in call.data:
                user.menu = 'info_task_menu'
            elif 'Info_start' == call.data:
                user.menu = 'info_user_menu'
            elif 'Measurement_marathon_start' == call.data:
                user.menu = 'measurement_user_menu'
            elif 'Photos_marathon_start' == call.data:
                user.menu = 'photos_user_menu'
            elif '_get' in call.data:
                user.menu = 'photos_category_menu'
            elif 'Stats_all' == call.data:
                user.menu = 'stats_menu'
            elif 'Buy_product_start' == call.data:
                user.menu = 'products_menu'
            elif 'Product_' in call.data:
                user.menu = 'product_info_menu'
            else:
                user.menu = 'main_menu'
            user.save()

        @log_error
        @self.bot.callback_query_handler(func=lambda call: "back" == call.data)
        def back(call):
            markup = InlineKeyboardMarkup(row_width=2)
            markup, text = choice_menu(markup, call)
            if call.message.content_type == 'text':
                self.bot.edit_message_text(
                    text=text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.id,
                    reply_markup=markup
                )
            elif call.message.content_type == 'photo':
                self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
                self.bot.send_message(
                    text=text,
                    chat_id=call.message.chat.id,
                    reply_markup=markup
                )
            return

        @log_error
        @self.bot.callback_query_handler(func=lambda call: 'main_menu' == call.data)
        def main_menu(call):
            markup = InlineKeyboardMarkup(row_width=2)
            markup = get_buttons('start', markup)
            user = User.objects.get(tg_id=call.message.chat.id)
            if call.message.content_type == 'text':
                self.bot.edit_message_text(
                    text=f'Привет, {user.name}!\nВыбери пункт меню:',
                    chat_id=call.message.chat.id,
                    message_id=call.message.id,
                    reply_markup=markup
                )
            elif call.message.content_type == 'photo':
                self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
                self.bot.send_message(
                    text=f'Привет, {user.name}!\nВыбери пункт меню:',
                    chat_id=call.message.chat.id,
                    reply_markup=markup
                )
            return

        @log_error
        @self.bot.callback_query_handler(func=lambda call: "_start" in call.data)
        def marathon_buttons(call):
            message_id = call.message.id
            chat_id = call.message.chat.id
            if "Tasks" in call.data:
                tasks(call, message_id, chat_id)
            elif "Measurement" in call.data:
                measurement(call, message_id, chat_id)
            elif "Photos" in call.data:
                photos(call, message_id, chat_id)
            elif "Invite" in call.data:
                invite(message_id, chat_id)
            elif "Enter" in call.data:
                enter_code(message_id, chat_id)
            elif "Info" in call.data:
                info_user(call, message_id, chat_id)
            elif 'Calculate' in call.data:
                calculate_kcal(call)
            elif 'Code' in call.data:
                task_code(message_id, chat_id)
            elif 'Buy' in call.data:
                buy_product_list(call, message_id, chat_id)
            else:
                return

        @log_error
        def buy_product_list(call, message_id, chat_id):
            edit_menu_user(call)
            markup = InlineKeyboardMarkup(row_width=2)
            markup = get_all_products(markup)
            self.bot.edit_message_text(text='Выберите товар:', chat_id=chat_id, message_id=message_id,
                                       reply_markup=markup)

        @log_error
        @self.bot.callback_query_handler(func=lambda call: "Product_" in call.data)
        def buy_product(call):
            edit_menu_user(call)
            product = Product.objects.get(unique_code=call.data.split('_')[1])
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton(text='Купить', callback_data=f'{product.unique_code}_buy'))
            markup.add(self.back_button)
            markup.add(self.main_menu)
            text = f'{product.name}\n{"-" * 50}\n' \
                   f'{product.description}\n\n' \
                   f'Стоимость - {product.price} баллов.'
            self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            if product.image:
                self.bot.send_photo(call.message.chat.id, open(f'{product.image.file.name}', 'rb'),
                                    caption=text, reply_markup=markup)
            else:
                self.bot.send_message(call.message.chat.id, text=text, reply_markup=markup)

        @log_error
        @self.bot.callback_query_handler(func=lambda call: "_buy" in call.data)
        def get_product_code(call):
            code = call.data.split("_buy")[0]
            product = Product.objects.get(unique_code=code)
            user = User.objects.get(tg_id=call.message.chat.id)
            if product:
                if user.scopes >= product.price:
                    if call.message.content_type == 'photo':
                        self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
                        self.bot.send_message(
                            text=f'Сообщите следующий код администратору - {product.unique_code}',
                            chat_id=call.message.chat.id,
                            reply_markup=InlineKeyboardMarkup().add(self.back_button).add(self.main_menu)
                        )
                    else:
                        self.bot.edit_message_text(
                            text=f'Сообщите следующий код администратору - {product.unique_code}',
                            chat_id=call.message.chat.id, message_id=call.message.id,
                            reply_markup=InlineKeyboardMarkup().add(self.back_button).add(self.main_menu)
                        )
                    user.purchased_goods.add(product)
                    user.scopes -= product.price
                    user.save()
                else:
                    if call.message.content_type == 'photo':
                        self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
                        self.bot.send_message(
                            text=f'У вас недостаточно баллов для приобретения данного товара!',
                            chat_id=call.message.chat.id,
                            reply_markup=InlineKeyboardMarkup().add(self.back_button).add(self.main_menu)
                        )
                    else:
                        self.bot.edit_message_text(
                            text=f'У вас недостаточно баллов для приобретения данного товара!',
                            chat_id=call.message.chat.id, message_id=call.message.id,
                            reply_markup=InlineKeyboardMarkup().add(self.back_button).add(self.main_menu)
                        )

        @log_error
        def calculate_kcal(call):
            register_user(call.message, 'calculate_kcal')

        @log_error
        @self.bot.callback_query_handler(func=lambda call: "Level_activity_" in call.data)
        def calculate_activity(call):
            state, step, next_step = get_object_scenario(call.message)
            level_activity = {
                'none': 1.2,
                'one-two': 1.375,
                'three-five': 1.55,
                'six-seven': 1.725,
                'professional': 1.9
            }
            state.context['level_activity'] = level_activity[f'{call.data.split("Level_activity_")[1]}']
            today = datetime.date.today()
            user = User.objects.get(tg_id=call.message.chat.id)
            age = today.year - user.birthday.year - (
                    (today.month, today.day) < (user.birthday.month, user.birthday.day)
            )
            kcal = ((655 + 9.56 * state.context['calculate_weight'] + 1.85 * state.context[
                'calculate_height'] - 4.68 * age) * state.context['level_activity']) - 571 if user.sex == 'Ж' \
                else ((66.5 + 13.75 * state.context['calculate_weight'] + 5 * state.context['calculate_height'] - 6.78
                       * age) * state.context['level_activity']) - 571
            UserState.objects.get(user_id=state.user_id).delete()
            text = f'Вам требуется - {round(kcal, 2)} ККАЛ.'
            markup = InlineKeyboardMarkup(row_width=2).add(self.main_menu)
            self.bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.id,
                                       reply_markup=markup)

        @log_error
        def info_user(call, message_id, chat_id):
            user = User.objects.get(tg_id=chat_id)
            markup = InlineKeyboardMarkup()
            edit_menu_user(call)
            user, markup, text = to_main_menu_from_info(user, markup)
            self.bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id,
                                       reply_markup=markup)

        @log_error
        @self.bot.callback_query_handler(func=lambda call: "Stats_all" in call.data)
        def stats(call):
            edit_menu_user(call)
            users = User.objects.order_by('-scopes')[:10]
            markup = InlineKeyboardMarkup().add(self.back_button).add(self.main_menu)
            text = f'ТОП-10 участников марафона:\n{"-" * 50}\n'
            if any([user.tg_id == call.message.chat.id for user in users]):
                pass
            for user in users:
                text += f'{user.name} {user.surname} - {user.scopes} баллов\n'
            self.bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.id,
                                       reply_markup=markup)

        @log_error
        def tasks(call, message_id, chat_id):
            categories = CategoryTasks.objects.all()
            markup = InlineKeyboardMarkup(row_width=1)
            edit_menu_user(call)
            text = 'Выберите категорию:'
            for category in categories:
                markup.add(InlineKeyboardButton(text=f'{category.category}', callback_data=f'Category_{category.id}'))
            else:
                text = 'К сожалению, на данный момент еще нет ни одного задания!'
            markup = get_buttons('', markup)
            markup.add(self.back_button).add(self.main_menu)
            self.bot.edit_message_text(
                text=text, chat_id=chat_id, message_id=message_id,
                reply_markup=markup
            )

        @log_error
        @self.bot.callback_query_handler(func=lambda call: 'Category_' in call.data)
        def choice_task(call):
            category = CategoryTasks.objects.get(id=call.data.split('_')[1])
            markup = InlineKeyboardMarkup(row_width=1)
            all_task = Tasks.objects.filter(category=category)
            complete_task = User.objects.filter(tg_id=call.message.chat.id).values_list('completed_tasks')
            edit_menu_user(call)
            markup = choice_tasks_algorithm(all_task, markup, complete_task)
            self.bot.edit_message_text(
                text='Выберите задание:', chat_id=call.message.chat.id, message_id=call.message.id,
                reply_markup=markup
            )

        @log_error
        @self.bot.callback_query_handler(func=lambda call: 'Task_' in call.data)
        def info_task(call):
            task = Tasks.objects.get(id=call.data.split('_')[1])
            markup = InlineKeyboardMarkup(row_width=1)
            edit_menu_user(call)
            markup.add(self.back_button)
            markup.add(self.main_menu)
            text = f'{task.name}\n\n' \
                   f'{task.description}\n\n' \
                   f'{task.url if task.url else ""}\n\n'
            if task.image:
                self.bot.delete_message(call.message.chat.id, call.message.id)
                self.bot.send_photo(call.message.chat.id, photo=open(f'{task.image.file.name}', 'rb'), caption=text,
                                    reply_markup=markup)
                return
            self.bot.edit_message_text(
                text=text, chat_id=call.message.chat.id, message_id=call.message.id,
                reply_markup=markup
            )

        @log_error
        def measurement(call, message_id, chat_id):
            edit_menu_user(call)
            markup = InlineKeyboardMarkup(row_width=2)
            marathon = Marathon.objects.get_marathon()
            if not marathon:
                markup.add(self.back_button).add(self.main_menu)
                self.bot.edit_message_text(text='Марафон еще не начался!',
                                           chat_id=chat_id, message_id=message_id, reply_markup=markup)
                return
            if not marathon.close:
                froze = Measurement.objects.get_or_none(tg_id=chat_id)
                if froze:
                    text = f'ДО:                     ----->                     ПОСЛЕ:\n' \
                           f'Грудь: {froze.breast_before if froze.breast_before else ""}       ----->       ' \
                           f'Грудь: {froze.breast_after if froze.breast_after else ""},\n' \
                           f'Талия: {froze.waist_before if froze.waist_before else ""}        ----->        ' \
                           f'Талия: {froze.waist_after if froze.waist_after else ""},\n' \
                           f'Бедра: {froze.femur_before if froze.femur_before else ""}        ----->        ' \
                           f'Бедра: {froze.femur_after if froze.femur_after else ""},\n' \
                           f'Вес: {froze.weight_before if froze.weight_before else ""}       ----->       ' \
                           f'Вес: {froze.weight_after if froze.weight_after else ""}'
                    markup = get_buttons('add', markup)
                    if len(markup.keyboard) == 0:
                        markup.add(self.back_button).add(self.main_menu)
                        self.bot.edit_message_text(text='Нужно немного подождать!\nЗагрузка еще не началась.',
                                                   chat_id=chat_id, message_id=message_id, reply_markup=markup)
                    else:
                        markup.add(self.back_button).add(self.main_menu)
                        self.bot.edit_message_text(text=text,
                                                   chat_id=chat_id, message_id=message_id, reply_markup=markup)
                else:
                    markup = get_buttons(buttons='add', markup=markup)
                    markup.add(self.back_button).add(self.main_menu)
                    self.bot.edit_message_text(text='Выберите, какие данные нужно ввести:',
                                               chat_id=chat_id,
                                               message_id=message_id,
                                               reply_markup=markup)
            else:
                markup.add(self.back_button).add(self.main_menu)
                self.bot.edit_message_text(text='Извините, марафон пока что закрыт!',
                                           chat_id=chat_id, message_id=message_id, reply_markup=markup)

        @log_error
        def photos(call, message_id, chat_id, menu=None):
            if not menu:
                edit_menu_user(call)
            markup = InlineKeyboardMarkup(row_width=2)
            marathon = Marathon.objects.get_marathon()
            if not marathon:
                if menu:
                    return User.objects.get(tg_id=chat_id), markup, 'Извините, марафон пока что закрыт!'
                else:
                    markup.add(self.back_button).add(self.main_menu)
                    self.bot.edit_message_text(text='Марафон еще не начался!',
                                               chat_id=chat_id, message_id=message_id, reply_markup=markup)
                    return
            if not marathon.close:
                photo = Photo.objects.get_or_none(tg_id=chat_id)
                if photo:
                    markup = get_buttons(buttons='photo_get', markup=markup, chat_id=chat_id)
                    markup.add(self.back_button).add(self.main_menu)
                    if menu:
                        return User.objects.get(tg_id=chat_id), markup, \
                               'Какую фотографию вы хотите увидеть?\n' \
                               'Чтобы добавить фото, просто пришлите его мне!\n' \
                               'Убедитесь, что отправляете сжатое изображение!'
                    self.bot.edit_message_text('Какую фотографию вы хотите увидеть?\n'
                                               'Чтобы добавить фото, просто пришлите его мне!\n'
                                               'Убедитесь, что отправляете сжатое изображение!',
                                               chat_id, message_id,
                                               reply_markup=markup)
                else:
                    markup.add(self.back_button)
                    markup.add(self.main_menu)
                    if menu:
                        return User.objects.get(tg_id=chat_id), markup, \
                               'Пришлите мне фотографию и следуйте дальнейшим инструкциям!'
                    self.bot.edit_message_text(text='Пришлите мне фотографию и следуйте дальнейшим инструкциям!',
                                               chat_id=chat_id, message_id=message_id, reply_markup=markup)
            else:
                markup.add(self.back_button)
                markup.add(self.main_menu)
                if menu:
                    return User.objects.get(tg_id=chat_id), markup, 'Извините, марафон пока что закрыт!'
                self.bot.edit_message_text(text='Извините, марафон пока что закрыт!',
                                           chat_id=chat_id, message_id=message_id, reply_markup=markup)

        @log_error
        def invite(message_id, chat_id):
            markup = InlineKeyboardMarkup(row_width=1).add(self.main_menu)
            user = User.objects.get(tg_id=chat_id)
            text = 'Сообщите вашему другу следующий код - {}\n' \
                   'Он должен будет ввести его и вы оба получите дополнительные баллы)'
            if not user.invitation_code:
                import random
                import string
                rand_string = ''.join(random.choice(string.ascii_letters) for _ in range(8))
                user.invitation_code = rand_string
                user.save()
            self.bot.edit_message_text(text=text.format(user.invitation_code), chat_id=chat_id,
                                       message_id=message_id, reply_markup=markup)

        @log_error
        def enter_code(message_id, chat_id):
            user = User.objects.get(tg_id=chat_id)
            if user.is_enter_invite_code:
                self.bot.edit_message_text(chat_id=chat_id,
                                           text=f'Вы уже ввели пригласительный код!',
                                           message_id=message_id,
                                           reply_markup=InlineKeyboardMarkup(row_width=1).add(self.main_menu)
                                           )
            else:
                markup = InlineKeyboardMarkup(row_width=1).add(self.main_menu)
                text = 'Пожалуйста, введите пригласительный код!'
                msg = self.bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
                self.bot.register_next_step_handler(msg, enter_invite_code, msg)

        @log_error
        def enter_invite_code(message_user, message_bot):
            user_from_db = User.objects.get_or_none(invitation_code=str(message_user.text))
            markup = InlineKeyboardMarkup(row_width=1).add(self.main_menu)
            if user_from_db:
                user = User.objects.get(tg_id=message_user.chat.id)
                if user == user_from_db:
                    if not message_bot.text == 'Ай-ай-ай. Нельзя так делать!\n' \
                                               'Нельзя вводить свой же код приглашения!!!':
                        msg = self.bot.edit_message_text(
                            text='Ай-ай-ай. Нельзя так делать!\nНельзя вводить свой же код приглашения!!!',
                            chat_id=message_bot.chat.id,
                            message_id=message_bot.id,
                            reply_markup=markup
                        )
                    else:
                        msg = copy(message_bot)
                    self.bot.delete_message(message_user.chat.id, message_user.id)
                    self.bot.clear_step_handler(msg)
                    self.bot.register_next_step_handler(msg, enter_invite_code, msg)
                elif not user.is_enter_invite_code:
                    count_scopes = getattr(Config.objects.all().first(), 'count_scopes_invite')
                    user_from_db.scopes += count_scopes
                    user_from_db.save()
                    user.scopes += count_scopes
                    user.is_enter_invite_code = True
                    user.save()
                    self.bot.delete_message(message_user.chat.id, message_user.id)
                    self.bot.edit_message_text(chat_id=message_bot.chat.id,
                                               text=f'Вас пригласил {user_from_db.name} {user_from_db.surname}',
                                               message_id=message_bot.id,
                                               reply_markup=markup
                                               )
                    self.bot.clear_step_handler(message_bot)
            else:
                if not message_bot.text == 'Вы ввели неверный код!\nПожалуйста, повторите попытку снова!':
                    msg = self.bot.edit_message_text(
                        text='Вы ввели неверный код!\nПожалуйста, повторите попытку снова!',
                        chat_id=message_bot.chat.id,
                        message_id=message_bot.id,
                        reply_markup=markup
                    )
                else:
                    msg = copy(message_bot)
                self.bot.delete_message(message_user.chat.id, message_user.id)
                self.bot.clear_step_handler(msg)
                self.bot.register_next_step_handler(msg, enter_invite_code, msg)

        @log_error
        def task_code(message_id, chat_id):
            markup = InlineKeyboardMarkup(row_width=1).add(self.main_menu)
            text = 'Пожалуйста, введите код задания!'
            msg = self.bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
            self.bot.register_next_step_handler(msg, enter_task_code, msg)

        @log_error
        def enter_task_code(message_user, message_bot):
            markup = InlineKeyboardMarkup(row_width=1).add(self.main_menu)
            complete_task = User.objects.filter(tg_id=message_user.chat.id).values_list('completed_tasks')
            task = Tasks.objects.get_or_none(unique_key=message_user.text)
            if task:
                if any([task.id in complete for complete in complete_task]):
                    text = 'Вы уже выполнили это задание!'
                else:
                    user = User.objects.get(tg_id=message_user.chat.id)
                    user.completed_tasks.add(task)
                    user.scopes += task.count_scopes
                    user.save()
                    text = f'Спасибо за введенный код!\nЗа это задание вы получили {task.count_scopes} баллов!'
                self.bot.delete_message(message_user.chat.id, message_user.id)
                self.bot.edit_message_text(text=text, chat_id=message_bot.chat.id, message_id=message_bot.id,
                                           reply_markup=markup)
                self.bot.clear_step_handler(message_bot)
            else:
                self.bot.delete_message(message_user.chat.id, message_user.id)
                if not message_bot.text == 'Вы ввели неверный код!\nПожалуйста, повторите попытку снова!':
                    msg = self.bot.edit_message_text(
                        text='Вы ввели неверный код!\nПожалуйста, повторите попытку снова!',
                        chat_id=message_bot.chat.id,
                        message_id=message_bot.id,
                        reply_markup=markup
                    )
                else:
                    msg = copy(message_bot)
                self.bot.clear_step_handler(msg)
                self.bot.register_next_step_handler(msg, enter_task_code, msg)

        @log_error
        def send_step(step, chat_id, context, message_id, local_markup=None):
            """
            Отправка сообщений из сценария
            :param message_id:
            :param step: шаг сценария
            :param chat_id: id чата, куда нужно отправлять
            :param context: контекст отправки
            :param local_markup: разметка сообщения
            :return: возврат объекта сообщения
            """
            try:
                if message_id != context['message_id']:
                    self.bot.delete_message(message_id=message_id, chat_id=chat_id)
                if context['message_id']:
                    if step['next_step'] is None:
                        return self.bot.send_message(chat_id=chat_id,
                                                     text=step['text'].format(**context),
                                                     reply_markup=local_markup, parse_mode="HTML")
                    return self.bot.edit_message_text(chat_id=chat_id,
                                                      message_id=context['message_id'],
                                                      text=step['text'].format(**context),
                                                      reply_markup=local_markup, parse_mode="HTML")
            except Exception as exc:
                self.bot.delete_message(message_id=message_id, chat_id=chat_id)
                return self.bot.send_message(chat_id=chat_id,
                                             text=step['text'].format(**context),
                                             reply_markup=local_markup, parse_mode="HTML")

        @log_error
        def get_object_scenario(message):
            """
            Метод получения объектов сценария.
            :param message: входное сообщение
            :return: Состояние сценария, шаг сценария, следующий шаг сценария
            """
            state = UserState.objects.get(user_id=message.chat.id)
            steps = SCENARIOS[state.scenario_name]['steps']
            step = steps[state.step_name]
            next_step = steps[step['next_step']]
            return state, step, next_step

        @log_error
        def start_scenario(scenario_name, chat_id, message):
            """
            Начало сценария. Только для модераторов.
            :param message:
            :param scenario_name: имя сценария
            :param chat_id: id чата, куда нужно отправлять сообщения
            """
            scenario = SCENARIOS[scenario_name]
            first_step = scenario['first_step']
            step = scenario['steps'][first_step]
            msg = send_step(step, chat_id, message_id=message.id, context={})
            UserState.objects.create(user_id=chat_id, scenario_name=scenario_name, step_name=first_step,
                                     context={"message_id": msg.id})

        @log_error
        def distribution_create(username, state):
            if state.scenario_name == 'register':
                import random
                import string
                user = User.objects.update_or_create(
                    defaults={
                        'tg_nickname': username,
                        'name': state.context['name'],
                        'surname': state.context['surname'],
                        'birthday': state.context['birthday'],
                        'sex': state.context['sex'],
                    },
                    tg_id=state.user_id,
                )
                if not user[1]:
                    invitation_code = ''.join(random.choice(string.ascii_letters) for _ in range(8))
                    user[0].invitation_code = invitation_code
                    user[0].save()
            elif state.scenario_name == 'photo':
                pass
            elif 'measurement_' in state.scenario_name:
                measurement_db = Measurement.objects.get_or_none(tg_id=state.user_id)
                if measurement_db is None:
                    measurement_db = Measurement.objects.create(tg_id=state.user_id)
                user = User.objects.get(tg_id=state.user_id)
                for key in state.context.keys():
                    setattr(measurement_db, key, state.context[key])
                measurement_db.save()
                user.measurement = measurement_db
                user.save()

        @log_error
        def continue_scenario(text, state, chat_id, message, username=None):
            """
            Продолжения сценария. Вызывается на каждом новом шаге, не считая шагов с кнопками.
            :param message:
            :param username:
            :param text: текст модератора
            :param state: состояние модератора
            :param chat_id: id чата, куда нужно отправлять сообщения
            """
            markup = InlineKeyboardMarkup(row_width=2)
            steps = SCENARIOS[state.scenario_name]['steps']
            step = steps[state.step_name]
            handler = getattr(handlers, step['handler'])
            check, markup = handler(text=text, context=state.context, markup=markup)
            if check:
                next_step = steps[step['next_step']]
                send_step(next_step, chat_id, state.context, local_markup=markup, message_id=message.id)
                if next_step['next_step']:
                    UserState.objects.filter(user_id=state.user_id).update(step_name=step['next_step'],
                                                                           context=state.context)
                else:
                    self.bot.delete_message(chat_id=chat_id, message_id=state.context['message_id'])
                    distribution_create(username, state)
                    UserState.objects.get(user_id=state.user_id).delete()
            else:
                text_to_send = step['failure_text'].format(**state.context)
                self.bot.send_message(chat_id=chat_id, text=text_to_send)

        @log_error
        @self.bot.message_handler(content_types=['text'], func=lambda message: not message.from_user.is_bot)
        def register_user(message, token_scenario=None):
            # clear(message)
            state = None
            text = message.text
            chat_id = message.chat.id
            try:
                state = UserState.objects.get(user_id=chat_id)
            except Exception as exc:
                logging.error(exc)
            if token_scenario is None and not state:
                user = User.objects.get_or_none(tg_id=message.chat.id)
                if user:
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup = get_buttons('start', markup)
                    self.bot.delete_message(message.chat.id, message.id)
                    self.bot.send_message(
                        text=f"Привет {user.name}!\nВыберите пункт меню:",
                        chat_id=message.chat.id,
                        reply_markup=markup
                    )
                    return
                else:
                    token_scenario = 'start'
            if state:
                if message.chat.username is None:
                    pass
                continue_scenario(text=text, state=state, chat_id=chat_id,
                                  username=message.chat.username if message.chat.username else message.chat.first_name,
                                  message=message)
            else:
                for intent in INTENTS:
                    if any(token == token_scenario for token in intent['tokens']):
                        if intent['answer']:
                            self.bot.send_message(chat_id, intent['answer'])
                        else:
                            start_scenario(intent['scenario'], chat_id, message)
                        break

        @log_error
        @self.bot.callback_query_handler(func=lambda call: "_sex" in call.data)
        def set_sex(call):
            state, step, next_step = get_object_scenario(call.message)
            sex = call.data.split('_')[0]
            if sex[0] == 'm':
                state.context["sex"] = 'М'
            elif sex[0] == 'w':
                state.context["sex"] = 'Ж'
            else:
                state.context["sex"] = None
            continue_scenario(call.message.text, state, call.message.chat.id, message=call.message)

        @log_error
        @self.bot.message_handler(content_types=['photo'])
        def photos_add(message):
            file_url = self.bot.get_file_url(file_id=message.photo[-1].file_id)
            self.image = requests.get(file_url).content
            if not os.path.isdir(f"{os.getcwd()}/tg_marathon/media/user_photos/{message.chat.id}"):
                os.mkdir(f"{os.getcwd()}/tg_marathon/media/user_photos/{message.chat.id}")
            with open(f"{os.getcwd()}/tg_marathon/media/user_photos/{message.chat.id}/"
                      f"{message.photo[-1].file_unique_id}.jpg", 'wb') as new_file:
                new_file.write(self.image)
                self.image = new_file.name.split('media/')[1]
            markup = InlineKeyboardMarkup(row_width=2)
            marathon = Marathon.objects.get_marathon()
            text = 'Выберите, куда относится эта фотография:'
            if not marathon:
                self.bot.edit_message_text(text='Марафон еще не начался!',
                                           chat_id=message.chat.id, message_id=message.id, reply_markup=markup)
                return
            if not marathon.close:
                markup = get_buttons(buttons='photo_add', markup=markup)
                if len(markup.keyboard) == 0:
                    text = 'К сожалению сейчас невозможно загрузить фотография. Я оповещу вас, когда можно будет!'
            else:
                text = 'Марафон временно закрыт! Приношу свои извинения!'
            markup.add(self.back_button)
            markup.add(self.main_menu)
            self.bot.send_message(message.chat.id, text, reply_markup=markup)

        @log_error
        @self.bot.callback_query_handler(func=lambda call: '_add' in call.data)
        def choice_category_photo(call):
            photo = Photo.objects.get_or_create(tg_id=call.message.chat.id)[0]
            user = User.objects.get(tg_id=call.message.chat.id)
            setattr(photo, call.data.split('_add')[0], self.image)
            user.photos_id = photo.id
            user.save()
            photo.save()
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(self.back_button)
            markup.add(self.main_menu)
            text = 'Спасибо!\nВаша фотография сохранена!\nЕсли хотите внести еще, просто пришлите мне фотографию!'
            self.image = None
            self.bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)

        @log_error
        @self.bot.callback_query_handler(func=lambda call: '_get' in call.data)
        def get_photo_from_db(call):
            edit_menu_user(call)
            photo = Photo.objects.get_or_none(tg_id=call.message.chat.id)
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(self.back_button)
            markup.add(self.main_menu)
            text = 'Вашей фотографии нет в базе. Пришлите мне фотографию и следуйте инструкциям!'
            image = getattr(photo, call.data.split('_get')[0])
            if not image:
                self.bot.edit_message_text(
                    text, call.message.chat.id, call.message.id, reply_markup=markup)
                return
            self.bot.delete_message(call.message.chat.id, call.message.id)
            self.bot.send_photo(call.message.chat.id, open(f'{image.file.name}', 'rb'), reply_markup=markup)

        @log_error
        @self.bot.callback_query_handler(func=lambda call: 'Add_' in call.data)
        def add_measurement(call):
            if 'before' in call.data:
                register_user(call.message, 'measurement_before')
            elif 'after' in call.data:
                register_user(call.message, 'measurement_after')
            else:
                return

        @log_error
        def choice_menu(markup, call):
            user = User.objects.get(tg_id=call.message.chat.id)
            text = f'Привет, {user.name}!\nВыбери пункт меню:'
            if user.menu == 'main_menu':
                markup = get_buttons(buttons='start', markup=markup)
                user.menu = 'main_menu'
            elif user.menu == 'category_task_menu':
                markup = get_buttons('start', markup)
                user.menu = 'main_menu'
            elif user.menu == 'tasks_menu':
                markup = get_task_markup(markup, call)
                user.menu = 'category_task_menu'
            elif user.menu == 'info_task_menu':
                if call.message.content_type == 'photo':
                    task_name = call.message.caption.split('\n\n')[0]
                else:
                    task_name = call.message.text.split('\n\n')[0]
                task = Tasks.objects.get(name=task_name)
                category = CategoryTasks.objects.get(id=task.category_id)
                all_task = Tasks.objects.filter(category=category)
                complete_task = User.objects.filter(tg_id=call.message.chat.id).values_list('completed_tasks')
                markup = choice_tasks_algorithm(all_task, markup, complete_task)
                user.menu = 'tasks_menu'
                text = f'Привет, {user.name}!\nВыбери задание:'
            elif user.menu == 'info_user_menu':
                markup = get_buttons('start', markup)
                user.menu = 'main_menu'
            elif user.menu == 'measurement_user_menu':
                user, markup, text = to_main_menu_from_info(user, markup)
            elif user.menu == 'photos_user_menu':
                user, markup, text = to_main_menu_from_info(user, markup)
            elif user.menu == 'photos_category_menu':
                user, markup, text = photos(call, call.message.id, call.message.chat.id, menu=True)
                user.menu = 'photos_user_menu'
            elif user.menu == 'stats_menu':
                user, markup, text = to_main_menu_from_info(user, markup)
            elif user.menu == 'products_menu':
                markup = get_buttons('start', markup)
                user.menu = 'main_menu'
            elif user.menu == 'product_info_menu':
                markup = get_all_products(markup)
                user.menu = 'products_menu'
            user.save()
            return markup, text

        @log_error
        def to_main_menu_from_info(user, markup):
            markup = get_buttons(buttons='information', markup=markup)
            markup.add(self.back_button)
            markup.add(self.main_menu)
            today = datetime.date.today()
            age = today.year - user.birthday.year - (
                    (today.month, today.day) < (user.birthday.month, user.birthday.day)
            )
            text = f"Привет, {user.name}!\n" \
                   f"Ваш возраст - {age} лет.\n" \
                   f"Ваш пол - {user.sex}.\n" \
                   f"Количество баллов - {user.scopes}."
            user.menu = 'info_user_menu'
            return user, markup, text

        @log_error
        def choice_tasks_algorithm(all_task, markup, complete_task):
            for task in all_task:
                if any([task.id in complete for complete in complete_task]):
                    continue
                else:
                    markup.add(InlineKeyboardButton(text=f'{task.name}', callback_data=f'Task_{task.id}'))
            markup.add(self.back_button)
            markup.add(self.main_menu)
            return markup

        @log_error
        def get_task_markup(markup, call):
            categories = CategoryTasks.objects.all()
            edit_menu_user(call)
            for category in categories:
                markup.add(InlineKeyboardButton(text=f'{category.category}', callback_data=f'Category_{category.id}'))
            markup.add(self.back_button)
            markup.add(self.main_menu)
            return markup

        @log_error
        def get_all_products(markup):
            products = Product.objects.all()
            for product in products:
                markup.add(InlineKeyboardButton(text=product.name, callback_data=f'Product_{product.unique_code}'))
            markup.add(self.back_button)
            markup.add(self.main_menu)
            return markup

        @log_error
        def get_buttons(buttons='start', markup=None, chat_id=None):
            self.buttons = Buttons.objects.all().first()
            if buttons == 'start':
                texts = ['Tasks_start', 'Info_start', 'Calculate_kcal_start', 'Invite_friend_start', 'Enter_code_start',
                         'Code_task_start', 'Buy_product_start']
                for text in texts:
                    caption = getattr(self.buttons, text.lower())
                    markup.add(InlineKeyboardButton(text=caption, callback_data=text))
            elif buttons == 'information':
                texts = ['Measurement_marathon_start',
                         'Photos_marathon_start',
                         'Stats_all']
                for text in texts:
                    caption = getattr(self.buttons, text.lower())
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
                            btn_text = getattr(self.buttons, callback)
                            markup.add(InlineKeyboardButton(text=btn_text,
                                                            callback_data=f'{callback}_get'))
                if '_add' in buttons:
                    marathon = Marathon.objects.get_marathon()
                    if marathon.send_measurements_before:
                        before_buttons = [btn for btn in callbacks if '_before' in btn]
                        for btn in before_buttons:
                            btn_text = getattr(self.buttons, btn)
                            markup.add(InlineKeyboardButton(text=btn_text, callback_data=f'{btn}_add'))
                    if marathon.send_measurements_after:
                        before_buttons = [btn for btn in callbacks if '_after' in btn]
                        for btn in before_buttons:
                            btn_text = getattr(self.buttons, btn)
                            markup.add(InlineKeyboardButton(text=btn_text, callback_data=f'{btn}_add'))
            elif 'add' in buttons:
                marathon = Marathon.objects.get_marathon()
                callbacks = ['Add_before', 'Add_after']
                for callback in callbacks:
                    if marathon.send_measurements_before and callback == 'Add_before':
                        btn_text = getattr(self.buttons, callback)
                        markup.add(InlineKeyboardButton(text=btn_text, callback_data=callback))
                    if marathon.send_measurements_after and callback == 'Add_after':
                        btn_text = getattr(self.buttons, callback)
                        markup.add(InlineKeyboardButton(text=btn_text, callback_data=callback))
            self.back_button = InlineKeyboardButton(text=f'{getattr(self.buttons, "back")}',
                                                    callback_data='back')
            self.main_menu = InlineKeyboardButton(text=f'{getattr(self.buttons, "main_menu")}',
                                                  callback_data='main_menu')
            return markup


if __name__ == "__main__":
    bot = BotMarathon()
    bot.run()
