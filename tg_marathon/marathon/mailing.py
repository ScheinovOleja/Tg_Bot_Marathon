import requests

from .models import Config, User


def mailing(request):
    text = f'{request.POST["message"]}\n\n\nНажмите /start, чтобы выйти в главное меню!'
    users = User.objects.all()
    for user in users:
        try:
            url = f'https://api.telegram.org/bot{getattr(Config.objects.all().first(), "token_bot")}' \
                  f'/sendMessage?chat_id={user.tg_id}&text={text}'
            requests.get(url)
        except Exception as exc:
            continue
    print('Дошло всем')
