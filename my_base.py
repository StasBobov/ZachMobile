import requests
import json
from kivy.app import App
import logging
import event_calendar
import constants
import pyrebase

log = logging.getLogger('base_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)





firebaseConfig = {
  "apiKey": "AIzaSyB1AH3rKpOY31O8IvhkIIi7rL0oB-o8bsE",
  "authDomain": "zach-mobile.firebaseapp.com",
  "databaseURL": "https://zach-mobile-default-rtdb.firebaseio.com",
  "projectId": "zach-mobile",
  "storageBucket": "zach-mobile.appspot.com",
  "messagingSenderId": "1044564107596",
  "appId": "1:1044564107596:web:42695e4d6711eb5d7b2fe9",
  "measurementId": "G-2VEJTJQ2E0"
}

firebase = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()


class MyBase:
    wak = "AIzaSyB1AH3rKpOY31O8IvhkIIi7rL0oB-o8bsE"

    # При нажатии на кнопку Sign up
    def sign_up(self, email, password):
        log.info('Try to sing up')
        app = App.get_running_app()
        signup_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        # Передаём в базу имейл и пассворд
        sign_up_request = requests.post(signup_url, data=signup_payload)
        sign_up_data = json.loads(sign_up_request.content.decode())
        log.info(sign_up_request, sign_up_data)

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
            log.debug(f'Sending data to database {post_request}')

            event_calendar.events_filling(sort=None)

            app.change_screen('home_screen')

            # показываем текст ошибки в лэйбле, если данные введены неверно
        if not sign_up_request.ok:
            error_data = json.loads(sign_up_request.content.decode())
            log.error(f'{error_data} {sign_up_request}')
            error_message = error_data['error']['message']
            app.root.ids['login_screen'].ids['login_message'].text = error_message

    def login(self, email, password):
        app = App.get_running_app()
        try:
            login = auth.sign_in_with_email_and_password(email, password)
            log.info('Successful login')
            refresh_token = login['refreshToken']
            localId = login['localId']
            idToken = login['idToken']  # authToken
            with open('refresh_token.txt', 'w') as f:
                f.write(refresh_token)
            app.local_id = constants.LOCAL_ID = localId  # uid
            app.id_token = constants.ID_TOKEN = idToken
            event_calendar.events_filling(sort=None)

            app.change_screen('home_screen')
        except Exception as ex:
            error_dict = json.loads(ex.args[1])
            app.root.ids['login_screen'].ids['login_message'].text = error_dict['error']['message']
            log.error(error_dict)

    def exchange_refresh_token(self, refresh_token):
        refresh_url = 'https://securetoken.googleapis.com/v1/token?key=' + self.wak
        refresh_payload = "{'grant_type': 'refresh_token', 'refresh_token': '%s'}" % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)

        local_id = refresh_req.json()['user_id']
        id_token = refresh_req.json()['id_token']
        log.debug('Got user_id and id_token')
        return id_token, local_id

