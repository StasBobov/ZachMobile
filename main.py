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
from requests_futures import sessions

log = logging.getLogger('main_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

# TODO

# что такое self.date_on_cancel?
# Зарефакторить все модули с запросами, перенести запросы в рефилл
# Ожидание и request ошибки в приложениях
# Заполнение личных данных в db (возможно через настройки)
# Подтверждение по имейл
# потеря имейла
# Размеры диалогового окна
# в настройках logout
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
            # заполняем всю херню

            self.session = sessions.FuturesSession(max_workers=5)

            try:
                future_one = self.session.get(
                        'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
                result = future_one.result()
                data = json.loads(result.content.decode())

                settings.user_settings_fill(data=data)
                event_calendar.events_filling(sort=None)
                # shopping_list.shopping_list_filling()
                # tasks.tasks_filling(sort=tasks.Task.task_sort)
                # notes.fill_notes_screen()
                # projects.fill_projects_screen()
            except Exception as exc:
                print(json.loads(exc.args[1]), 'Please heck your internet connection!')
                self.error_modal_screen(text_error=json.loads(exc.args[1])
                # log.error(json.loads(exc.args[1]))


            # result = requests.get(
            #     'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
            # data = json.loads(result.content.decode())
            # log.debug(f'Get app projects data from the server {result}')



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
        but_cancel = Button(text='Cancel!', font_size=12, size_hint=(.3, .5))
        bl2.add_widget(but_cancel)
        bl.add_widget(bl2)
        popup = Popup(title="Something went wrong", content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
                      auto_dismiss=False)

        # усли не будешь менять статус
        def cancel(*args):
            popup.dismiss()

        but_cancel.bind(on_press=cancel)
        popup.open()


    # ___________________________________Time picker________________________________________________________________________

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        # можно поставить время по дефолту
        default_time = datetime.datetime.strptime("4:20:00", '%H:%M:%S').time()
        time_dialog.set_time(default_time)
        time_dialog.bind(on_cancel=self.date_on_cancel, time=self.get_time)
        time_dialog.open()

    # для time picker
    def time_on_cancel(self, instance, time):
        # self.root.ids["new_event_screen"].ids["chosen_date"].text =
        pass

    # для time picker
    def get_time(self, instance, time):
        self.root.ids["new_event_screen"].ids["chosen_time"].text = str(time)
        chosen_time = time

    # ___________________________________Date picker________________________________________________________________________

    # def show_date_picker(self):
    #     # можно поставить любую конкретную даты в скобках
    #     date_dialog = MDDatePicker()
    #     # можно выбрать диапазон, возвращает список с датами
    #     date_dialog = MDDatePicker(mode='range')
    #     date_dialog.bind(on_save=self.on_save, on_cancel=self.date_on_cancel)
    #     date_dialog.open()
    #
    # # для date picker
    # def on_save(self, instance, value, date_range):
    #     print(instance, value, date_range)
    #
    # # для date picker
    # def date_on_cancel(self, instance, value):
    #     # не понятно пока как добраться до атрибута text
    #     pprint(dir(self.root.ids['calendar_screen']))
    #     # print(self.root.ids.date_label.text)
    #     # self.root.ids.date_label.text = 'Cancel'
    #
    # # для date picker
    # def callback(self, date):
    #     pass
    #
    # # для date picker
    # def open_calendar(self):
    #     self.date.open()


MainApp().run()
