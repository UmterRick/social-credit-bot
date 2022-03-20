class BotConf:
    token = '5151266143:AAGq4MZAolc0YLd3YRDlSoMRo4LEoKR5QWo'


class WebHookConf:

    heroku_app = 'social-credit-bot-vu'
    host = f'https://{heroku_app}.herokuapp.com'
    path = '/webhook/' + BotConf.token
    url = host + path
    app_host = '0.0.0.0'
    app_port = 5050
