import csv
import datetime
import logging
import os
from pathlib import Path

from django.contrib import admin
# Register your models here.
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.safestring import mark_safe

from .models import User, Measurement, Marathon, Tasks, CategoryTasks, Product, Photo, Config, Buttons, UserState


@admin.register(CategoryTasks, Buttons)
class MarathonAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['tg_nickname', 'name', 'surname', 'scopes']
    fields = ['tg_nickname', 'name', 'surname', 'scopes', 'birthday', 'sex', 'invitation_code', 'get_photo',
              'get_measurement', 'complete_task', 'purchased_products']
    list_filter = ['sex']
    list_per_page = 10
    actions = ['import_csv']
    search_fields = ['name', 'surname']
    readonly_fields = ['invitation_code', 'tg_id', 'get_photo', 'get_measurement', 'complete_task',
                       'purchased_products']

    def delete_queryset(self, request, queryset):
        for user in queryset:
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
            user.delete()

    def import_csv(self, request, queryset):
        try:
            file_path = f"{Path(__file__).resolve().parent.parent}/media/csv_files"
            if not os.path.isdir(file_path):
                os.mkdir(file_path)
            with open(f'{file_path}/file_csv.csv', 'w', encoding='utf-8') as csv_file:
                data = [['tg_id', 'tg_nickname', 'Имя', 'Фамилия', 'Возраст', 'Пол', 'Кол-во баллов', 'Грудь ДО',
                         'Талия ДО', 'Бедра ДО', 'Вес ДО', 'Грудь ПОСЛЕ', 'Талия ПОСЛЕ', 'Бедра ПОСЛЕ', 'Вес ПОСЛЕ']]
                for user in queryset:
                    writer = csv.writer(csv_file, delimiter=';')
                    measurement = Measurement.objects.get_or_none(tg_id=user.tg_id)
                    if not measurement:
                        continue
                    today = datetime.date.today()
                    age = today.year - user.birthday.year - (
                            (today.month, today.day) < (user.birthday.month, user.birthday.day)
                    )
                    data.append([user.tg_id, user.tg_nickname, user.name, user.surname, age, user.sex, user.scopes,
                                 measurement.waist_before, measurement.breast_before, measurement.femur_before,
                                 measurement.weight_before, measurement.waist_after, measurement.breast_after,
                                 measurement.femur_after, measurement.weight_after])
                for row in data:
                    writer.writerow(row)
                return redirect('/media/csv_files/file_csv.csv')
        except Exception as exc:
            logging.error(exc)

    def complete_task(self, request):
        complete_task = User.objects.filter(tg_id=request.tg_id).values_list('completed_tasks')
        text_url = ''
        for task in Tasks.objects.all():
            if any([task.id in complete for complete in complete_task]):
                text_url += f'<li><b><a href="/admin/marathon/tasks/{task.id}/change/" target="_blank">{task.name}' \
                            f'</a></b></li>\n'
        url = f"""
                <ul>
                    {text_url}
                </ul>
                """
        return mark_safe(url)

    def purchased_products(self, request):
        complete_task = User.objects.filter(tg_id=request.tg_id).values_list('purchased_goods')
        text_url = ''
        for product in Product.objects.all():
            if any([product.id in complete for complete in complete_task]):
                text_url += f'<li><b><a href="/admin/marathon/product/{product.id}/change/" target="_blank">{product.name}' \
                            f'</a></b></li>\n'
        url = f"""
                <ul>
                    {text_url}
                </ul>
                """
        return mark_safe(url)

    def get_photo(self, request):
        url = f'<b><a href="/admin/marathon/photo/{request.photos.id}/change/" target="_blank">Тык сюды</a></b>'
        return mark_safe(url)

    def get_measurement(self, request):
        url = f'<b><a href="/admin/marathon/measurement/{request.measurement.id}/change/" target="_blank">Тык сюды</a>' \
              f'</b>'
        return mark_safe(url)

    get_measurement.short_description = 'Замеры пользователя'
    get_photo.short_description = 'Фотографии пользователя'
    complete_task.short_description = 'Выполненные задания'
    import_csv.short_description = 'Выгрузить в CSV'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'image', 'preview', 'price', 'unique_code']
    list_display = ['name', 'price', 'unique_code']
    search_fields = ['unique_code', 'name']
    readonly_fields = ["preview"]

    def delete_queryset(self, request, queryset):
        for product in queryset:
            for user in User.objects.filter(purchased_goods=product):
                user.completed_tasks.remove(product)
                user.save()
            file_path = f"{Path(__file__).resolve().parent.parent}/media/{product.image.name}"
            command = f'rm -r {file_path}'
            os.system(command)
            product.delete()

    def preview(self, obj):
        return mark_safe(
            f'<a href="{obj.image.url}" target="_blank"><img src="{obj.image.url}" style="max-height: 200px;"></a>')

    preview.short_description = 'Превью товара'


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    fields = ['user', 'front_before', 'sideways_before', 'back_before', 'front_after',
              'sideways_after', 'back_after']
    readonly_fields = ['user', 'front_before', 'sideways_before', 'back_before', 'front_after',
                       'sideways_after', 'back_after']
    list_display = ['tg_id', 'user']

    def user(self, request):
        user = User.objects.get(tg_id=request.tg_id)
        url = f'<b><a href="/admin/marathon/user/{user.id}/change/" target="_blank">{user.name} {user.surname}</a></b>'
        return mark_safe(url)

    user.short_description = 'Пользователь:'

    def front_before(self, obj):
        url = f'<a href="{obj.photo_front_before.url}" target="_blank"><img src="{obj.photo_front_before.url}" ' \
              f'style="max-height:200px;"></a>'
        return mark_safe(url)

    front_before.short_description = 'Фото спереди до:'

    def sideways_before(self, obj):
        url = f'<a href="{obj.photo_sideways_before.url}" target="_blank"><img src="{obj.photo_sideways_before.url}"' \
              f'style="max-height: 200px;"></a> '
        return mark_safe(url)

    sideways_before.short_description = 'Фото сбоку до:'

    def back_before(self, obj):
        url = f'<a href="{obj.photo_back_before.url}" target="_blank"><img src="{obj.photo_back_before.url}"' \
              f'style="max-height:200px;"></a> '
        return mark_safe(url)

    back_before.short_description = 'Фото сзади до:'

    def front_after(self, obj):
        url = f'<a href="{obj.photo_front_after.url}" target="_blank"><img src="{obj.photo_front_after.url}"' \
              f'style="max-height:200px;"></a> '
        return mark_safe(url)

    front_after.short_description = 'Фото спереди после:'

    def sideways_after(self, obj):
        url = f'<a href="{obj.photo_sideways_after.url}" target="_blank"><img src="{obj.photo_sideways_after.url}"' \
              f'style="max-height:200px;"></a> '
        return mark_safe(url)

    sideways_after.short_description = 'Фото сбоку после:'

    def back_after(self, obj):
        url = f'<a href="{obj.photo_back_after.url}" target="_blank"><img src="{obj.photo_back_after.url}"' \
              f' style="max-height:200px;"></a> '
        return mark_safe(url)

    back_after.short_description = 'Фото сзади после:'


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    fields = ['user', 'waist_before', 'breast_before', 'femur_before', 'weight_before',
              'waist_after', 'breast_after', 'femur_after', 'weight_after']
    readonly_fields = ['user']
    list_display = ['tg_id', 'user']

    def user(self, request):
        user = User.objects.get(tg_id=request.tg_id)
        url = f'<b><a href="/admin/marathon/user/{user.id}/change/" target="_blank">{user.name} {user.surname}</a></b>'
        return mark_safe(url)

    user.short_description = mark_safe('<b>Пользователь</b>')


@admin.register(Marathon)
class MarathonAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'date_start', 'date_end', 'send_measurements_before', 'send_measurements_after',
              'close']
    list_display = ['name', 'date_start', 'date_end', 'send_measurements_before', 'send_measurements_after', 'close']

    def delete_queryset(self, request, queryset):
        for user in User.objects.all():
            try:
                Photo.objects.get(tg_id=user.tg_id).delete()
            except Exception as exc:
                logging.error(exc)
            try:
                Measurement.objects.get(tg_id=user.tg_id).delete()
            except Exception as exc:
                logging.error(exc)
            user.measurement = None
            user.photos = None
            user.scopes = 0
            user.save()
            file_path = f"{Path(__file__).resolve().parent.parent}/media/user_photos"
            command = f'rm -r {file_path}/{user.tg_id}'
            os.system(command)
        for marathon in queryset:
            marathon.delete()


@admin.register(Tasks)
class TaskAdmin(admin.ModelAdmin):
    fields = ['name', 'category', 'description', 'count_scopes', 'url', 'image', 'preview', 'unique_key']
    readonly_fields = ['preview']
    list_display = ['name', 'category', 'count_scopes', 'unique_key']
    list_filter = ['category']
    search_fields = ['name', 'unique_key']

    def delete_queryset(self, request, queryset):
        for task in queryset:
            for user in User.objects.filter(completed_tasks=task):
                user.completed_tasks.remove(task)
                user.save()
            file_path = f"{Path(__file__).resolve().parent.parent}/media/{task.image.name}"
            command = f'rm -r {file_path}'
            os.system(command)
        for task in queryset:
            task.delete()

    def preview(self, obj):
        url = f'<a href="{obj.image.url}" target="_blank"><img src="{obj.image.url}" style="max-height: 200px;"></a>'
        return mark_safe(url)

    preview.short_description = 'Превью задания'


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'login', 'start_bot']

    def start_bot(self, request):
        return mark_safe(
            f'<a class="button" href="{reverse("admin:start")}">Запустить</a>'
            f'<a class="button" href="{reverse("admin:stop")}">Остановить</a>'
            f'<a class="button" href="{reverse("admin:restart")}">Перезапустить</a>')

    # Добавляем к существующим ссылкам в админке, ссылки на кнопки для их обработки
    def get_urls(self):
        urls = super().get_urls()
        shard_urls = [path('#', self.admin_site.admin_view(self.start), name="start"),
                      path('#', self.admin_site.admin_view(self.stop), name="stop"),
                      path('#', self.admin_site.admin_view(self.restart), name="restart")
        ]

        # Список отображаемых столбцов
        return shard_urls + urls

    # Обработка событий кнопок
    def start(self, request):
        text = 'systemctl start bot'
        os.system(text)
        return redirect('/admin/marathon/config/')

    def stop(self, request):
        text = 'systemctl stop bot'
        os.system(text)
        return redirect('/admin/marathon/config/')

    def restart(self, request):
        text = 'systemctl restart bot'
        os.system(text)
        return redirect('/admin/marathon/config/')

    start_bot.short_description = 'Запуск'


@admin.register(UserState)
class UserStateAdmin(admin.ModelAdmin):
    pass
