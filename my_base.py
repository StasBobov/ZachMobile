from pprint import pprint

import requests
import json
from kivy.app import App


class MyBase:
    wak = "AIzaSyB1AH3rKpOY31O8IvhkIIi7rL0oB-o8bsE"

    def sign_up(self, email, password):
        app = App.get_running_app()
        signup_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        # print(sign_up_request.ok)
        # print(sign_up_request.content.decode())
        sign_up_data = json.loads(sign_up_request.content.decode())

        if sign_up_request.ok:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken'] # authToken
            with open('refresh_token.txt', 'w') as f:
                f.write(refresh_token)

            app.local_id = localId # uid
            app.id_token = idToken

            my_data = '{"name": "", "lname": "", "email": "", "events": ""}'
            post_request = requests.patch("https://zach-mobile-default-rtdb.firebaseio.com/" + localId + ".json?auth="
                                          + idToken, data=my_data)
            # print(post_request.ok)
            # print(json.loads((post_request.content.decode())))

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
        # print('Refresh ok', refresh_req.ok)
        # pprint(refresh_req.json())

        local_id = refresh_req.json()['user_id']
        id_token = refresh_req.json()['id_token']
        return id_token, local_id

