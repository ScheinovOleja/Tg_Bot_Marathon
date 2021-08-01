import time
import requests
from django.shortcuts import render
from django.views import View

from .models import Config, User


# https://api.telegram.org/bot<token>/setWebhook?url=<url>/webhooks/tutorial/
class SendMessageToTG(View):

    def post(self, request, *args, **kwargs):
        text = f'{request.POST["message"]}\n\n\nНажмите /start, чтобы выйти в главное меню!'
        for user in User.objects.all():
            try:
                url = f'https://api.telegram.org/bot{getattr(Config.objects.all().first(), "token_bot")}' \
                      f'/sendMessage?chat_id={user.tg_id}&text={text}'
                requests.get(url)
                time.sleep(0.5)
            except Exception as exc:
                continue
        return render(request, 'index.html', {'context': {'sent': True}})

    def get(self, request):
        return render(request, 'index.html', {'context': {'sent': False}})

