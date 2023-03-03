import json

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

import my_base
from kivy.app import App


# def email_verification():
#     my_base.auth.send_email_verification(id_token)

# Изменить свой пароль
def reset_password(email):
    app = App.get_running_app()
    try:
        my_base.auth.send_password_reset_email(email)
        modal_settings_window(name='Change the password',
                              label='A link to change your password has been sent to your email')
        app.change_screen('login_screen')
    except Exception as exc:
        error_dict = json.loads(exc.args[1])
        # print(exc)
        app.root.ids['login_recovery_screen'].ids['login_message'].text = error_dict['error']['message']


def modal_settings_window(name, label):
    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text=label, font_size=12)
    bl.add_widget(l)
    but_ok = Button(text='Ok!', font_size=12, size_hint=(.3, .5))
    bl.add_widget(but_ok)
    popup = Popup(title=name, content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.5, "top": 0.5}, )

    # просто закрываем модальное окно
    def ok(*args):
        popup.dismiss()

    but_ok.bind(on_press=ok)
    popup.open()