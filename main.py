import logging

from kivy.app import App
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

log = logging.getLogger('main_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

# TODO


# Заполнение личных данных в db (возможно через настройки)
# Подтверждение по имейл
# Не забыть про тайм пикер
# потеря имейла
# Размеры диалогового окна
# почему постоянно зависает?
# что делать с журналами логов
# notes / transfer project не прокручивается скролл
# Активна или не активна кнопка Back
# Сохранять контент в файле приложения ???
# Уведомления на электронную почту
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


class MainApp(MDApp):
    lock = 1
    previous_screen = 'home_screen'

    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'BlueGray'
        self.my_base = MyBase()
        Builder.load_file("main.kv")

    def on_start(self):
        log.info('Start App')
        # При старте пытаемся открыть файл с токеном
        try:
            with open('refresh_token.txt', 'r') as f:
                refresh_token = f.read()
            log.info('refresh_token was read')
            # Если получается, то сразу грузим данные
            constants.ID_TOKEN, constants.LOCAL_ID = self.my_base.exchange_refresh_token(refresh_token)
            # и переходим на Home screen
            self.root.ids['screen_manager'].transition = NoTransition()
            self.change_screen('home_screen')
            self.root.ids['screen_manager'].transition = CardTransition()
            self.lock = 0
            # заполняем всю херню
            try:
                result = requests.get(
                        'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
                log.debug(f'Get app projects data from the server {result}')
                data = json.loads(result.content.decode())

                settings.user_settings_fill(data=data)
                event_calendar.events_filling(data=data, sort=None)
                shopping_list.shopping_list_filling(data=data)
                tasks.tasks_filling(sort=tasks.Task.task_sort, data=data)
                notes.fill_notes_screen(data=data)
                projects.fill_projects_screen(data=data)
            except Exception as exc:
                self.error_modal_screen(text_error="Please check your internet connection!)")
                log.error(exc)
            # Если нет, то остаёмся на экране логина
        except Exception:
            log.error('Not all functions not all features enabled on start')
            print('Not Ok')

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

    def unlock_header(self, command):
        if self.lock:
            pass
        else:
            if command == 'home':
                self.change_screen('home_screen')
            elif command == 'settings':
                self.change_screen('settings_screen')


    # ___________________________________Time picker________________________________________________________________________

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        # можно поставить время по дефолту
        default_time = datetime.datetime.strptime("4:20:00", '%H:%M:%S').time()
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
