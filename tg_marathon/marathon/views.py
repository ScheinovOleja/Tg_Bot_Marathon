import threading
from django.shortcuts import render
from django.views import View
from .mailing import mailing


# https://api.telegram.org/bot<token>/setWebhook?url=<url>/webhooks/tutorial/
class SendMessageToTG(View):

    def post(self, request, *args, **kwargs):
        threading.Thread(target=mailing, args=(request,), daemon=True).start()
        return render(request, 'index.html', {'context': {'sent': True}})

    def get(self, request):
        return render(request, 'index.html', {'context': {'sent': False}})
