import os

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


def logout():
    app = App.get_running_app()
    path = 'refresh_token.txt'
    if os.path.isfile(path):
        os.remove(path)
        constants.LOCAL_ID = None
        constants.ID_TOKEN = None
        app.lock = 1
        app.change_screen('login_screen')
    else:
        print('No')


class MyBase:
    wak = "AIzaSyB1AH3rKpOY31O8IvhkIIi7rL0oB-o8bsE"

    # При нажатии на кнопку Sign up
    def sign_up(self, email, password):
        log.info('Try to sing up')
        app = App.get_running_app()
        signup_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            # Передаём в базу имейл и пассворд
            sign_up_request = requests.post(signup_url, data=signup_payload)
            sign_up_data = json.loads(sign_up_request.content.decode())
            log.info(sign_up_request, sign_up_data)

            if sign_up_request.ok:
                refresh_token = sign_up_data['refreshToken']
                localId = sign_up_data['localId']
                idToken = sign_up_data['idToken'] # authToken
                app.lock = 0
                with open('refresh_token.txt', 'w') as f:
                    f.write(refresh_token)

                constants.LOCAL_ID = localId # uid
                constants.ID_TOKEN = idToken
                data = {"user_telephone": "", "user_name": "", "user_lname": "", "user_email": email}

                my_data = json.dumps(data)
                self.create_user(my_data=my_data, idToken=idToken, localId=localId)

                # показываем текст ошибки в лэйбле, если данные введены неверно
            if not sign_up_request.ok:
                error_data = json.loads(sign_up_request.content.decode())
                log.error(f'{error_data} {sign_up_request}')
                error_message = error_data['error']['message']
                app.root.ids['login_screen'].ids['login_message'].text = error_message
        except Exception as exc:
            app.error_modal_screen(text_error="Please check your internet connection!")
            log.error(exc)

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
            constants.LOCAL_ID = localId  # uid
            constants.ID_TOKEN = idToken
            app.lock = 0
            app.first_fill()
            app.change_screen('home_screen')
        except Exception as ex:
            try:
                error_dict = json.loads(ex.args[1])
                app.root.ids['login_screen'].ids['login_message'].text = error_dict['error']['message']
            except Exception as exc:
                error_dict = ex
                app.root.ids['login_screen'].ids['login_message'].text = 'Please heck your internet connection!'
                log.error(ex)
            log.error(error_dict)

    def exchange_refresh_token(self, refresh_token):
        app = App.get_running_app()
        refresh_url = 'https://securetoken.googleapis.com/v1/token?key=' + self.wak
        refresh_payload = "{'grant_type': 'refresh_token', 'refresh_token': '%s'}" % refresh_token
        try:

            refresh_req = requests.post(refresh_url, data=refresh_payload)

            local_id = refresh_req.json()['user_id']

            id_token = refresh_req.json()['id_token']
            log.debug('Got user_id and id_token')
            return id_token, local_id
        except Exception as exc:
            if type(exc) == requests.exceptions.ConnectionError:
                app.error_modal_screen(text_error="Please check your internet connection!")
            else:
                app.root.ids['login_screen'].ids['login_message'].text = 'There is something wrong with auto-authorization, \n ' \
                                                                         'try logging in with your email and password'
            log.error(exc)

    def create_user(self, idToken, my_data, localId):
        app = App.get_running_app()
        try:
            post_request = requests.patch("https://zach-mobile-default-rtdb.firebaseio.com/" + localId + ".json?auth="
                                          + idToken, data=my_data)

            log.debug(f'Sending data to database {post_request}')
            result = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
            log.debug(f'Get app projects data from the server {result}')
            data = json.loads(result.content.decode())

            event_calendar.events_filling(sort=None, data=data)

            app.change_screen('home_screen')
        except Exception as exc:
            app.error_modal_screen(text_error="Please check your internet connection!")
            log.error(exc)

