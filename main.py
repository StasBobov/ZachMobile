import logging
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from my_base import MyBase
from kivymd.app import MDApp
from kivymd.uix.pickers import MDTimePicker
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
import tasks
import event_calendar
import shopping_list
import projects
import notes
import settings
import constants
import datetime
import requests
import json
import my_base as mb

log = logging.getLogger('main_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


# TODO

#
# поменять название на wait for verification
# в first_fill добавить обработку если рефреш токен не открылся
# про тайм пикер не забыть
# что делать с журналами логов
# notes / transfer project не прокручивается скролл - сделать как в settings
# Активна или не активна кнопка Back
# какие пакеты не используются в приложении?

class EventCalendarScreen(Screen):
    days = []
    now = datetime.datetime.now()
    year = now.year
    month = now.month


class NewEventScreen(Screen):
    pass


class InactiveEventsScreen(Screen):
    pass


class HomeScreen(Screen):
    pass


class CalendarScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class EventsScreen(Screen):
    pass


class TodolistScreen(Screen):
    pass


class ProjectsScreen(Screen):
    pass


class ArchiveProjectsScreen(Screen):
    pass


class OneProjectScreen(Screen):
    pass


class SupplementScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class NewTaskScreen(Screen):
    pass


class ShoppingListScreen(Screen):
    pass


class NotesScreen(Screen):
    pass


class OneNoteScreen(Screen):
    pass


class LoginRecoveryScreen(Screen):
    pass


class VerificationScreen(Screen):
    pass


class MainApp(MDApp):
    lock = 1
    previous_screen = 'home_screen'

    def verification_restart_app(self):
        print('restart')
        self.root.clear_widgets()
        self.stop()
        MainApp().run()

    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'BlueGray'
        self.my_base = MyBase()
        Builder.load_file("main.kv")

    def on_start(self):
        log.info('Start App')
        # Пытаемся найти файл с верификацией (для повторных входов)
        try:
            with open('verification.txt', 'r') as v:
                verification = v.read()
                mb.exchange_refresh_token()
                # Делаем запрос для первого заполнения
                result = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
                self.first_fill(result=result)
        # Если не находим, то возвращаемся на экран верификации
        except Exception as exc:
            log.error(exc)
            # Он исключения сам обрабатывает
            mb.exchange_refresh_token()
            try:
                result = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
                # Если не даёт доступ к БД, пусть активирует имейл
                if result.status_code == 401:
                    self.change_screen('verification_screen')
                # если база пустая, то создаём её и файл, подтверждающий верификацию
                elif json.loads(result.content.decode()) is None:
                    # заполняем базу данных и выгружаем в приложение
                    data = {"user_telephone": "", "user_name": "", "user_lname": "", "user_email": mb.user_email,
                            'sms_remind': False, 'email_remind': False, 'timezone': ''}
                    self.lock = 0
                    self.my_data = json.dumps(data)
                    self.my_base.create_user(my_data=self.my_data, idToken=constants.ID_TOKEN, localId=constants.LOCAL_ID)
                    result = requests.get(
                        'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
                    self.first_fill(result=result)
                    with open('verification.txt', 'w') as f:
                        f.write('Verification : True')
                else:
                    self.first_fill(result=result)
                    with open('verification.txt', 'w') as f:
                        f.write('Verification : True')
            except Exception as exc:
                log.error(exc)

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name

    def error_modal_screen(self, text_error):
        # Создаём модальное окно
        bl = BoxLayout(orientation='vertical')
        l = Label(text=text_error, font_size=12)
        bl.add_widget(l)
        bl2 = BoxLayout(orientation='horizontal')
        but_restart = Button(text='Try again!', font_size=12, size_hint=(.3, .5))
        bl2.add_widget(but_restart)
        bl.add_widget(bl2)
        popup = Popup(title="Something went wrong", content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
                      auto_dismiss=False)

        def try_again(*args):
            popup.dismiss()
            self.root.clear_widgets()
            self.stop()
            MainApp().run()

        but_restart.bind(on_press=try_again)
        popup.open()

    # Разблокирует home and settings, когда залогинился
    def unlock_header(self, command):
        if self.lock:
            pass
        else:
            if command == 'home':
                self.change_screen('home_screen')
            elif command == 'settings':
                self.change_screen('settings_screen')

    def first_fill(self, result):
        # заполняем всю херню
        try:
            # и переходим на Home screen
            self.root.ids['screen_manager'].transition = NoTransition()
            self.change_screen('home_screen')
            self.root.ids['screen_manager'].transition = CardTransition()
            self.lock = 0
            data = json.loads(result.content.decode())
            settings.user_settings_fill(data=data)
            event_calendar.events_filling(data=data, sort=None)
            shopping_list.shopping_list_filling(data=data)
            tasks.tasks_filling(sort=tasks.Task.task_sort, data=data)
            notes.fill_notes_screen(data=data)
            projects.fill_projects_screen(data=data)
        except Exception as exc:
            log.error(exc)

    # ___________________________________Time picker________________________________________________________________________

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        # можно поставить время по дефолту
        default_time = datetime.datetime.now().time()
        time_dialog.set_time(default_time)
        time_dialog.bind(on_cancel=self.time_on_cancel, time=self.get_time)
        time_dialog.open()

    # для time picker
    def time_on_cancel(self, instance, time):
        # self.root.ids["new_event_screen"].ids["chosen_date"].text =
        pass

    # для time picker
    def get_time(self, instance, time):
        self.root.ids["new_event_screen"].ids["chosen_time"].text = str(time)
        chosen_time = time


MainApp().run()
