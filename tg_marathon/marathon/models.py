import logging
import os
import random
import string
from datetime import datetime
from pathlib import Path

import requests
from django.db.models import *


# Create your models here.


class MyManager(Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None


class ManagerMarathon(MyManager):

    def get_marathon(self):
        marathon = self.all().first()
        try:
            today = datetime.now().date()
            if today == marathon.date_end:
                marathon.close = True
                marathon.save()
        except Exception as exc:
            return None
        return marathon


class Measurement(Model):
    class Meta:
        verbose_name_plural = 'Замеры пользователей'

    objects = MyManager()
    tg_id = IntegerField(unique=True, verbose_name='TG_ID пользователя', db_index=True)
    waist_before = FloatField(default=0, null=True, verbose_name='Талия(см) до:')
    breast_before = FloatField(default=0, null=True, verbose_name='Грудь(см) до:')
    femur_before = FloatField(default=0, null=True, verbose_name='Бедра(см) до:')
    weight_before = FloatField(default=0, null=True, verbose_name='Вес(кг) до:')
    # --------------------------------------------------------
    waist_after = FloatField(default=0, null=True, verbose_name='Талия(см) после:')
    breast_after = FloatField(default=0, null=True, verbose_name='Грудь(см) после:')
    femur_after = FloatField(default=0, null=True, verbose_name='Бедра(см) после:')
    weight_after = FloatField(default=0, null=True, verbose_name='Вес(кг) после:')

    def __str__(self):
        return f"{self.tg_id}"


class Photo(Model):
    class Meta:
        verbose_name_plural = 'Фотографии пользователей'

    objects = MyManager()
    tg_id = IntegerField(unique=True, null=True, verbose_name='TG_ID пользователя:', db_index=True)
    photo_front_before = ImageField(null=True, verbose_name='Фото спереди до:')
    photo_sideways_before = ImageField(null=True, verbose_name='Фото сбоку до:')
    photo_back_before = ImageField(null=True, verbose_name='Фото сзади до:')
    # --------------------------------------------------------
    photo_front_after = ImageField(null=True, verbose_name='Фото спереди после:')
    photo_sideways_after = ImageField(null=True, verbose_name='Фото сбоку после:')
    photo_back_after = ImageField(null=True, verbose_name='Фото сзади после:')

    def __str__(self):
        return f"{self.tg_id}"


class CategoryTasks(Model):
    class Meta:
        verbose_name_plural = 'Категории заданий'

    objects = MyManager()
    category = CharField(max_length=50, default='', verbose_name='Название категории:', db_index=True)

    def __str__(self):
        return f"{self.category}"


class Tasks(Model):
    class Meta:
        verbose_name_plural = 'Задания'

    objects = MyManager()
    name = CharField(max_length=50, default='', null=False, verbose_name='Название задания:', db_index=True)
    category = ForeignKey(CategoryTasks, default=None, on_delete=DO_NOTHING, null=False,
                          verbose_name='Категория задания:')
    description = TextField(max_length=5000, default='', verbose_name='Описание задания:')
    count_scopes = IntegerField(default=0, null=False,
                                verbose_name='Количество очков, получаемое при выполнении задания:')
    url = URLField(max_length=500, default='', null=True, blank=True, verbose_name='Ссылка на материалы для задания:')
    image = ImageField(upload_to='image_tasks/', blank=True, null=True, verbose_name='Картинка задания:')
    unique_key = CharField(max_length=12, default='', unique=True, blank=True, verbose_name='Уникальный код задания:')

    def save(self, *args, **kwargs):
        if not self.unique_key:
            self.unique_key = ''.join(random.choice(string.ascii_letters) for _ in range(12))
        super(Tasks, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        for user in User.objects.filter(completed_tasks=self):
            user.completed_tasks.remove(self)
        file_path = f"{Path(__file__).resolve().parent.parent}/media/{self.image.name}"
        command = f'rm -r {file_path}'
        os.system(command)
        return super(Tasks, self).delete()

    def __str__(self):
        return f'{self.name}'


class Marathon(Model):
    class Meta:
        verbose_name_plural = 'Марафон'

    objects = ManagerMarathon()
    name = CharField(max_length=50, default='', verbose_name='Название марафона:', db_index=True)
    description = TextField(max_length=5000, default='', verbose_name='Описание марафона:')
    date_start = DateField(default=None, auto_created=True, verbose_name='Дата начала марафона:')
    date_end = DateField(default=None, verbose_name='Дата окончания марафона:')
    send_measurements_before = BooleanField(default=False, verbose_name='Включить отправку замеров ДО марафона:')
    send_measurements_after = BooleanField(default=False, verbose_name='Включить отправку замеров ПОСЛЕ марафона:')
    close = BooleanField(default=False, verbose_name='Закрыть марафон:')

    def save(self, *args, **kwargs):
        marathons = Marathon.objects.all()
        if len(marathons) < 1:
            users = User.objects.all()
            token = getattr(Config.objects.all().first(), 'token_bot')
            text = f"Доброго времени суток!\n\n" \
                   f"Прямо сейчас начался новый марафон - {self.name}.\n\n" \
                   f"Цель текущего марафона:\n{self.description}\n\n" \
                   f"Марафон окончится {self.date_end}\n\n" \
                   f"Введите /start для входа в меню!"
            for user in users:
                url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={user.tg_id}&text={text}'
                requests.get(url)
        super(Marathon, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        for user in User.objects.all():
            user.measurement = None
            user.photos = None
            user.scopes = 0
            user.save()
            try:
                Photo.objects.get(tg_id=user.tg_id).delete()
            except Exception as exc:
                logging.error(exc)
            try:
                Measurement.objects.get(tg_id=user.tg_id).delete()
            except Exception as exc:
                logging.error(exc)
            file_path = f"{Path(__file__).resolve().parent.parent}/media/user_photos"
            command = f'rm -r {file_path}/{user.tg_id}'
            os.system(command)
        return super(Marathon, self).delete()

    def __str__(self):
        return f'{self.name}'


class Product(Model):
    class Meta:
        verbose_name_plural = 'Товары'

    objects = MyManager()
    name = CharField(max_length=20, default='', verbose_name='Название товара:', db_index=True)
    description = TextField(max_length=5000, default='', verbose_name='Описание товара:')
    image = ImageField(upload_to='image_product/', null=True, blank=True, verbose_name="Фотография товара:")
    price = IntegerField(default=0, null=False, verbose_name='Стоимость товара:')
    unique_code = CharField(max_length=20, default='', unique=True, blank=True, verbose_name='Уникальный код товара:')

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = ''.join(random.choice(string.ascii_letters) for _ in range(20))
        super(Product, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        file_path = f"{Path(__file__).resolve().parent.parent}/media/{self.image.name}"
        os.system(f'rm -r {file_path}')
        super(Product, self).delete()

    def __str__(self):
        return f"{self.name}"


class User(Model):
    class Meta:
        verbose_name_plural = 'Пользователи бота'

    objects = MyManager()
    tg_id = IntegerField(unique=True, verbose_name='TG_ID пользователя:', db_index=True)
    tg_nickname = CharField(max_length=50, verbose_name='TG_Nickname пользователя:')
    name = CharField(max_length=50, verbose_name='Имя пользователя:')
    surname = CharField(max_length=50, null=True, verbose_name='Фамилия пользователя:')
    scopes = IntegerField(default=0, verbose_name='Количество баллов пользователя:')
    birthday = DateField(verbose_name='Возраст пользователя:')
    sex = CharField(max_length=1, verbose_name='Пол:')
    invitation_code = CharField(max_length=8, unique=True, default='', blank=True,
                                verbose_name='Уникальный пригласительный код пользователя:')
    is_enter_invite_code = BooleanField(default=False, blank=True, verbose_name='Ввел пригласительный код?')
    marathon = ForeignKey(Marathon, on_delete=DO_NOTHING, null=True, blank=True,
                          verbose_name='Марафон, в котором участвует пользователь:')
    completed_tasks = ManyToManyField(Tasks, blank=True,
                                      verbose_name='Выполненные задания:')
    purchased_goods = ManyToManyField(Product, blank=True,
                                      verbose_name='Выполненные задания:')
    measurement = ForeignKey(Measurement, on_delete=CASCADE, null=True, blank=True,
                             verbose_name='Замеры пользователя:')
    photos = ForeignKey(Photo, on_delete=CASCADE, null=True, blank=True, verbose_name='Фотографии пользователя:')
    menu = CharField(default='main_menu', max_length=100, blank=True)

    def delete(self, using=None, keep_parents=False):
        try:
            Photo.objects.get(tg_id=self.tg_id).delete()
        except Exception as exc:
            logging.error(exc)
        try:
            Measurement.objects.get(tg_id=self.tg_id).delete()
        except Exception as exc:
            logging.error(exc)
        file_path = f"{Path(__file__).resolve().parent.parent}/media/user_photos"
        command = f'rm -r {file_path}/{self.tg_id}'
        os.system(command)
        return super(User, self).delete()

    def __str__(self):
        return f'{self.name} {self.surname} - {self.tg_id}'


class Config(Model):
    class Meta:
        verbose_name_plural = 'Конфигурация бота'

    objects = MyManager()
    name = CharField(default='', max_length=100, verbose_name='Имя бота')
    login = CharField(default='', max_length=500, verbose_name='Логин бота(@...)')
    token_bot = CharField(max_length=100, verbose_name='Токен бота в telegram:')
    count_scopes_invite = IntegerField(
        default=100,
        verbose_name='Количество баллов за приглашение друга(получают оба юзера):',
        db_index=True
    )

    def __str__(self):
        return f'{self.name}'


class Buttons(Model):
    class Meta:
        verbose_name_plural = 'Подписи кнопок'

    objects = MyManager()
    tasks_start = CharField(max_length=50, verbose_name='Текст кнопки для заданий(главное меню):')
    info_start = CharField(max_length=50, verbose_name='Текст кнопки для личной информации человека(главное меню):')
    calculate_kcal_start = CharField(max_length=50, verbose_name='Текст кнопки для подсчета калорий(главное меню):')
    invite_friend_start = CharField(max_length=50, verbose_name='Текст кнопки для приглашения друга(главное меню):')
    enter_code_start = CharField(max_length=50, verbose_name='Текст кнопки для ввода кода приглашения(главное меню):')
    code_task_start = CharField(max_length=50, verbose_name='Текст кнопки для ввода кода задания(главное меню):')
    buy_product_start = CharField(max_length=50,
                                  verbose_name='Текст кнопки для просмотра списка товаров(главное меню):')
    back = CharField(max_length=50, verbose_name='Текст кнопки для возврата назад:')
    main_menu = CharField(max_length=50, verbose_name='Текст кнопки для возврата в главное меню:')
    measurement_marathon_start = CharField(max_length=50, verbose_name='Текст кнопки для просмотра своих замеров:')
    photos_marathon_start = CharField(max_length=50, verbose_name='Текст кнопки для просмотра своих фотографий:')
    stats_all = CharField(max_length=50, verbose_name='Текст кнопки для просмотра статистики:')
    photo_front_before = CharField(max_length=50, verbose_name='Текст кнопки для просмотра фотографии спереди ДО:')
    photo_sideways_before = CharField(max_length=50, verbose_name='Текст кнопки для просмотра фотографии сбоку ДО:')
    photo_back_before = CharField(max_length=50, verbose_name='Текст кнопки для просмотра фотографии сзади ДО:')
    photo_front_after = CharField(max_length=50,
                                  verbose_name='Текст кнопки для просмотра фотографии спереди ПОСЛЕ:')
    photo_sideways_after = CharField(max_length=50,
                                     verbose_name='Текст кнопки для просмотра фотографии сбоку ПОСЛЕ:')
    photo_back_after = CharField(max_length=50, verbose_name='Текст кнопки для просмотра фотографии сзади ПОСЛЕ:')
    add_before = CharField(max_length=50, default='', verbose_name='Текст для кнопки ввода замеров ДО')
    add_after = CharField(max_length=50, default='', verbose_name='Текст для кнопки ввода замеров ПОСЛЕ')

    def __str__(self):
        return 'Подписи кнопок'


class UserState(Model):
    objects = MyManager()
    user_id = IntegerField(unique=True, db_index=True)
    scenario_name = CharField(max_length=20)
    step_name = CharField(max_length=20)
    context = JSONField(null=True)
