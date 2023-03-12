import json
import logging
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import pytz
from kivy.factory import Factory
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
        try:
            error_dict = json.loads(exc.args[1])
            app.root.ids['login_recovery_screen'].ids['login_message'].text = error_dict['error']['message']
        except Exception as ex:
            app.error_modal_screen(text_error="Please check your internet connection!")
            log.error(ex)


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
    app.root.ids['settings_screen'].ids['timezone'].text = data['timezone']
    app.root.ids['settings_screen'].ids['sms_reminder'].active = data['sms_remind']
    app.root.ids['settings_screen'].ids['email_reminder'].active = data['email_remind']


def user_settings_refill():
    app = App.get_running_app()
    try:
        result = requests.get(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
        log.debug(f'Get app projects data from the server {result}')
        data = json.loads(result.content.decode())
        settings_layout = app.root.ids['notes_screen']
        for w in settings_layout.walk():
            if w.__class__  == Label:
                settings_layout.remove_widget(w)
        user_settings_fill(data=data)
    except Exception as exc:
        app.error_modal_screen(text_error="Please check your internet connection!)")
        log.error(exc)


def modal_settings_window(command):
    app = App.get_running_app()
    if command == 'user_name':
        hint_text = 'name'
        lavel_text = 'Please enter your name'
        title_text = 'Filling in the name'
    elif command == 'telephone':
        hint_text = 'Including country code (+000000000000)'
        lavel_text = 'Please enter your correct telephone number'
        title_text = 'Filling in the telephone number'
    else:
        hint_text = 'last name'
        lavel_text = 'Please enter your last name'
        title_text = 'Filling in the last name'


    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text=lavel_text, font_size=12)
    t_i = TextInput(multiline=False, hint_text=hint_text)
    l2 = Label(text='', font_size=12)
    bl.add_widget(l)
    bl.add_widget(t_i)
    bl.add_widget(l2)
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

    def yes(*args):

        if command == 'telephone':
            if len(t_i.text) == 13 and t_i.text[0] == '+' and t_i.text[1:].isdigit():
                popup.dismiss()
                try:
                    log.info('Patch data on server')
                    move_project_request = requests.patch(
                        'https://zach-mobile-default-rtdb.firebaseio.com/%s.json?auth=%s'
                        % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({command: t_i.text}))
                    log.info(move_project_request)
                    user_settings_refill()
                except Exception as exc:
                    app.error_modal_screen(text_error="Please check your internet connection!")
                    log.error(exc)
                    return
            else:
                l2.text = 'You entered an invalid phone number'
        else:
            popup.dismiss()
            try:
                log.info('Patch data on server')
                move_project_request = requests.patch(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s.json?auth=%s'
                    % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({command: t_i.text}))
                log.info(move_project_request)
                user_settings_refill()
            except Exception as exc:
                app.error_modal_screen(text_error="Please check your internet connection!")
                log.error(exc)
                return

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()


def popup_func():
    popup = Factory.SettingsPopup()
    # fill the GridLayout
    grid = popup.ids.container1
    time_zones = pytz.all_timezones
    for zone in time_zones:
        grid.add_widget(Factory.MyButton(text=zone, on_press=add_timezone))

    popup.open()


def add_timezone(butt):
    try:
        log.info('Patch data on server')
        set_timezone_request = requests.patch(
            'https://zach-mobile-default-rtdb.firebaseio.com/%s.json?auth=%s'
            % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'timezone': butt.text}))
        log.info(set_timezone_request)
        user_settings_refill()
    except Exception as exc:
        app = App.get_running_app()
        app.error_modal_screen(text_error="Please check your internet connection!")
        log.error(exc)
        return


def set_email_reminder(value):
    try:
        log.info('Patch data on server')
        value_request = requests.patch(
            'https://zach-mobile-default-rtdb.firebaseio.com/%s.json?auth=%s'
            % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'email_remind': value}))
        log.info(value_request)
        user_settings_refill()
    except Exception as exc:
        app = App.get_running_app()
        app.error_modal_screen(text_error="Please check your internet connection!")
        log.error(exc)
        return


def set_sms_reminder(value):
    try:
        log.info('Patch data on server')
        value_request = requests.patch(
            'https://zach-mobile-default-rtdb.firebaseio.com/%s.json?auth=%s'
            % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'sms_remind': value}))
        log.info(value_request)
        user_settings_refill()
    except Exception as exc:
        app = App.get_running_app()
        app.error_modal_screen(text_error="Please check your internet connection!")
        log.error(exc)
        return


