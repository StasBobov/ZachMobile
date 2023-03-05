import json
import logging

import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

import constants
import my_base
from kivy.app import App

log = logging.getLogger('settings_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


# Изменить свой пароль
def reset_password(email):
    app = App.get_running_app()
    try:
        my_base.auth.send_password_reset_email(email)
        modal_change_password_window(name='Change the password',
                                     label='A link to change your password has been sent to your email')
        app.change_screen('login_screen')
    except Exception as exc:
        error_dict = json.loads(exc.args[1])
        # print(exc)
        app.root.ids['login_recovery_screen'].ids['login_message'].text = error_dict['error']['message']


def modal_change_password_window(name, label):
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


def user_settings_fill(data):
    app = App.get_running_app()

    # Заполняем данные пользователя
    app.root.ids['settings_screen'].ids['user_name'].text = data['user_name']
    app.root.ids['settings_screen'].ids['user_lname'].text = data['user_lname']
    app.root.ids['settings_screen'].ids['user_email'].text = data['user_email']
    app.root.ids['settings_screen'].ids['user_telephone'].text = data['user_telephone']


def user_settings_refill(data):
    pass

def modal_settings_window(command):
    if command == 'user_name':
        hint_text = 'name'
        lavel_text = 'Please enter your name'
        title_text = 'Filling in the name field'
    else:
        hint_text = 'last name'
        lavel_text = 'Please enter your last name'
        title_text = 'Filling in the last name field'

    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text=lavel_text, font_size=12)
    t_i = TextInput(multiline=False, hint_text=hint_text)
    bl.add_widget(l)
    bl.add_widget(t_i)
    bl2 = BoxLayout(orientation='horizontal')
    but_no = Button(text='Cancel!', font_size=12, size_hint=(.3, .5))
    but_yes = Button(text='Save', font_size=12, size_hint=(.3, .5))
    bl2.add_widget(but_no)
    bl2.add_widget(but_yes)
    bl.add_widget(bl2)
    popup = Popup(title=title_text, content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
                  auto_dismiss=False)

    # усли не будешь менять статус
    def no(*args):
        popup.dismiss()

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        popup.dismiss()
        log.info('Patch data on server')
        move_project_request = requests.patch(
            'https://zach-mobile-default-rtdb.firebaseio.com/%s.json?auth=%s'
            % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({command: t_i.text}))
        log.info(move_project_request)


    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()