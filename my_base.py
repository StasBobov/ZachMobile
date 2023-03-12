import os
import requests
import json
from kivy.app import App
import logging
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
    path_rfr = 'refresh_token.txt'
    path_vrf = 'verification.txt'
    app.lock = 1
    if os.path.isfile(path_rfr):
        os.remove(path_rfr)
        constants.LOCAL_ID = None
        constants.ID_TOKEN = None
    if os.path.isfile(path_vrf):
        os.remove(path_vrf)
    app.change_screen('login_screen')


def exchange_refresh_token():
    app = App.get_running_app()
    try:
        with open('refresh_token.txt', 'r') as f:
            refresh_token = f.read()
        log.info('refresh_token was read')
        refresh_url = 'https://securetoken.googleapis.com/v1/token?key=' + constants.WAK
        refresh_payload = "{'grant_type': 'refresh_token', 'refresh_token': '%s'}" % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)

        constants.LOCAL_ID = refresh_req.json()['user_id']

        constants.ID_TOKEN = refresh_req.json()['id_token']
        log.debug('Got user_id and id_token')
    except Exception as exc:
        app.change_screen('login_screen')
        if type(exc) == requests.exceptions.ConnectionError:
            app.error_modal_screen(text_error="Please check your internet connection!")
        else:
            app.root.ids['login_screen'].ids[
                'login_message'].text = 'Please enter your email and password'
        log.error(exc)


def verification_request(id_token):
    payload = json.dumps({
        "requestType": "VERIFY_EMAIL",
        "idToken": id_token
    })
    r = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
                      params={"key": constants.WAK},
                      data=payload)


class MyBase:

    # При нажатии на кнопку Sign up
    def sign_up(self, email, password):
        self.email = email
        log.info('Try to sing up')
        app = App.get_running_app()
        signup_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + constants.WAK

        signup_payload = {"email": email, "password": password, "returnSecureToken": True}

        try:
            # Передаём в базу имейл и пассворд
            sign_up_request = requests.post(signup_url, data=signup_payload)
            sign_up_data = json.loads(sign_up_request.content.decode())
            log.info(sign_up_request, sign_up_data)

            if sign_up_request.ok:
                verification_request(id_token=sign_up_data['idToken'])
                refresh_token = sign_up_data['refreshToken']
                self.localId = sign_up_data['localId']
                self.idToken = sign_up_data['idToken']  # authToken

                with open('refresh_token.txt', 'w') as f:
                    f.write(refresh_token)
                    app.change_screen('verification_screen')
          # показываем текст ошибки в лэйбле, если данные введены неверно
            if not sign_up_request.ok:
                error_data = json.loads(sign_up_request.content.decode())
                log.error(f'{error_data} {sign_up_request}')
                error_message = error_data['error']['message']
                app.root.ids['login_screen'].ids['login_message'].text = error_message
        except Exception as exc:
            app.error_modal_screen(text_error="Please check your internet connection!")
            log.error(exc)

    # Вызывается с панели Login screen
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
            app.on_start()
        except Exception as ex:
            try:
                error_dict = json.loads(ex.args[1])
                app.root.ids['login_screen'].ids['login_message'].text = error_dict['error']['message']
            except Exception as exc:
                error_dict = ex
                app.root.ids['login_screen'].ids['login_message'].text = 'Please heck your internet connection!'
                log.error(ex)
            log.error(error_dict)

    def create_user(self, idToken, my_data, localId):
        app = App.get_running_app()
        try:
            post_request = requests.patch("https://zach-mobile-default-rtdb.firebaseio.com/" + localId + ".json?auth="
                                          + idToken, data=my_data)
            log.debug(f'Sending data to database {post_request}')
            app.change_screen('home_screen')
        except Exception as exc:
            app.error_modal_screen(text_error="Please check your internet connection!")
            log.error(exc)

