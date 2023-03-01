from pprint import pprint

from kivymd.uix.menu import MDDropdownMenu

from my_base import MyBase
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivymd_extensions.akivymd.uix.datepicker import AKDatePicker
import tasks
import event_calendar
import shopping_list
import projects
import notes
import constants
import datetime
import requests
import json


# TODO

# notes / transfer project не прокручивается скролл
# one_project проверить scrollview
# Залогировать майн
# Ожидание и request ошибки в приложениях
# Заполнение личных данных в db (возможно через настройки)
# Подтверждение по имейл
# восстановление пароля
# Размеры диалогового окна
# Активна или не активна кнопка Back
# Сохранять контент в файле приложения ???

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


class LabelButton(ButtonBehavior, Label):
    pass


class ImageButton(ButtonBehavior, Image):
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



class MainApp(MDApp):
    previous_screen = 'home_screen'
    # dropdown = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # список эвентов
        self.events_list = None
        # Для Date picker
        self.date = AKDatePicker(callback=self.callback)

    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'BlueGray'
        self.my_base = MyBase()
        Builder.load_file("main.kv")

    def on_start(self):

        # При старте пытаемся открыть файл с токеном
        try:
            with open('refresh_token.txt', 'r') as f:
                refresh_token = f.read()
            # Если получается, то сразу грузим данные
            self.id_token, self.local_id = self.my_base.exchange_refresh_token(refresh_token)
            constants.LOCAL_ID = self.local_id
            constants.ID_TOKEN = self.id_token
            self.result = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/' + self.local_id + '.json?auth=' + self.id_token)

            # и переходим на Home screen
            data = json.loads(self.result.content.decode())
            self.root.ids['screen_manager'].transition = NoTransition()
            self.change_screen('home_screen')
            self.root.ids['screen_manager'].transition = CardTransition()

            # заполняем всю херню
            event_calendar.events_filling(sort=None)
            shopping_list.shopping_list_filling()
            tasks.tasks_filling(sort=tasks.Task.task_sort)
            notes.fill_notes_screen()
            projects.fill_projects_screen()

            # self.dropdown = MDDropdownMenu()
            # self.dropdown.items.append(
            #     {"viewclass": "MDMenuItem",
            #      "text": "Create new event",
            #      "callback": print('Create new event')}
            # )

            # Если нет, то остаёмся на экране логина
        except Exception:
            print('Not Ok')

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name


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

    def show_date_picker(self):
        # можно поставить любую конкретную даты в скобках
        date_dialog = MDDatePicker()
        # можно выбрать диапазон, возвращает список с датами
        date_dialog = MDDatePicker(mode='range')
        date_dialog.bind(on_save=self.on_save, on_cancel=self.date_on_cancel)
        date_dialog.open()

    # для date picker
    def on_save(self, instance, value, date_range):
        print(instance, value, date_range)

    # для date picker
    def date_on_cancel(self, instance, value):
        # не понятно пока как добраться до атрибута text
        pprint(dir(self.root.ids['calendar_screen']))
        # print(self.root.ids.date_label.text)
        # self.root.ids.date_label.text = 'Cancel'

    # для date picker
    def callback(self, date):
        pass

    # для date picker
    def open_calendar(self):
        self.date.open()


MainApp().run()
