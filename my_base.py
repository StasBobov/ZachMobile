import requests
import json
from kivy.app import App
import logging

log = logging.getLogger('base_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


class MyBase:
    wak = "AIzaSyB1AH3rKpOY31O8IvhkIIi7rL0oB-o8bsE"

    # При нажатии на кнопку Sign up
    def sign_up(self, email, password):
        print('Sign Up')
        app = App.get_running_app()
        signup_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        # Передаём в базу имейл и пассворд
        sign_up_request = requests.post(signup_url, data=signup_payload)

        sign_up_data = json.loads(sign_up_request.content.decode())
        log.info(f'Try to sing up {sign_up_request} {sign_up_data}')

        if sign_up_request.ok:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken'] # authToken
            with open('refresh_token.txt', 'w') as f:
                f.write(refresh_token)

            app.local_id = localId # uid
            app.id_token = idToken

            my_data = '{"name": "", "lname": "", "email": ""}'
            post_request = requests.patch("https://zach-mobile-default-rtdb.firebaseio.com/" + localId + ".json?auth="
                                          + idToken, data=my_data)

            app.events_filling(sort=None)

            app.change_screen('home_screen')

            # показываем текст ошибки в лэйбле, если данные введены неверно
        if not sign_up_request.ok:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data['error']['message']
            app.root.ids['login_screen'].ids['login_message'].text = error_message

    def exchange_refresh_token(self, refresh_token):
        refresh_url = 'https://securetoken.googleapis.com/v1/token?key=' + self.wak
        refresh_payload = "{'grant_type': 'refresh_token', 'refresh_token': '%s'}" % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)

        local_id = refresh_req.json()['user_id']
        id_token = refresh_req.json()['id_token']
        return id_token, local_id

