import requests
import json
from kivy.app import App


class MyBase:
    wak = "AIzaSyB1AH3rKpOY31O8IvhkIIi7rL0oB-o8bsE"

    def sign_up(self, email, password):
        app = App.get_running_app()
        signup_url = "https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        print(sign_up_request.ok)
        print(sign_up_request.content.decode())
        # sign_up_data = json.loads(sign_up_request.content.decode())
        #
        # if sign_up_request.ok:
        #     refresh_token = sign_up_data['refreshToken']
        #     localId = sign_up_data['localId']
        #     idToken = sign_up_data['idToken']
        #     with open('refresh_token.txt', 'w') as f:
        #         f.write(refresh_token)
        #
        #     app.local_id = localId
        #     app.id_token = idToken
        #
        #     my_data = '{"events": ""}'
        #     post_request = requests.patch('https://zach-mobile-default-rtdb.firebaseio.com/Zach/Users' + localId + '.json?auth=' + idToken, data=my_data)
        #     app.change_screen('home_screen')
        # if not sign_up_request.ok:
        #     error_data = json.loads(sign_up_request.content.decode())
        #     error_message = error_data['error']['message']
        #     app.root.ids['login_screen'].ids['login_message'].text = error_message

    def sign_in(self):
        pass
