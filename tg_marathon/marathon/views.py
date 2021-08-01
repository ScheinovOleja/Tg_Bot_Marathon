import threading
import time
import requests
from django.shortcuts import render
from django.views import View

from .models import Config, User


# https://api.telegram.org/bot<token>/setWebhook?url=<url>/webhooks/tutorial/
class SendMessageToTG(View):

    def mailing(self, request):
        text = f'{request.POST["message"]}\n\n\nНажмите /start, чтобы выйти в главное меню!'
        i = 0
        for user in User.objects.all():
            i += 1
            try:
                url = f'https://api.telegram.org/bot{getattr(Config.objects.all().first(), "token_bot")}' \
                      f'/sendMessage?chat_id={user.tg_id}&text={text}'
                requests.get(url)
                print(i)
            except Exception as exc:
                print(i)
                continue
        print('Дошло всем')

    def post(self, request, *args, **kwargs):
        threading.Thread(target=self.mailing, args=(request,), daemon=True).start()
        return render(request, 'index.html', {'context': {'sent': True}})

    def get(self, request):
        return render(request, 'index.html', {'context': {'sent': False}})
