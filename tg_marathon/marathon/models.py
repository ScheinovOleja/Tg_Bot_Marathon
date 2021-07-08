from django.db.models import *

# Create your models here.


class Measurement(Model):
    tg_id = IntegerField(verbose_name='TG_ID пользователя')
    waist = FloatField(verbose_name='Талия(см)')
    breast = FloatField(verbose_name='Грудь(см)')
    femur = FloatField(verbose_name='Бедра(см)')
    weight = FloatField(verbose_name='Вес(кг)')


class Photo(Model):
    tg_id = IntegerField(verbose_name='TG_ID пользователя')
    photo_front = BinaryField(verbose_name='Фото спереди')
    photo_sideways = BinaryField(verbose_name='Фото сбоку')
    photo_back = BinaryField(verbose_name='Фото сзади')


class User(Model):
    tg_id = IntegerField(verbose_name='TG_ID пользователя')
    tg_nickname = CharField(max_length=50, verbose_name='Никнейм пользователя')
    name = CharField(max_length=50, verbose_name='Имя пользователя')
    surname = CharField(max_length=50, verbose_name='Фамилия пользователя')
    measurement = OneToOneField(Measurement, on_delete=DO_NOTHING, verbose_name='Замеры пользователя')
    photos = OneToOneField(Photo, on_delete=DO_NOTHING, verbose_name='Фотографии пользователя')
