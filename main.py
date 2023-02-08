from pprint import pprint
from my_base import MyBase
from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivymd_extensions.akivymd.uix.datepicker import AKDatePicker
import requests
import json


class CalendarKivy(Screen):
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


class LoginScreen(Screen):
    pass


class AddTaskScreen(Screen):
    pass


class MainApp(MDApp):
    user_id = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date = AKDatePicker(callback=self.callback)

    def callback(self, date):
        pprint(date.month)

    def build(self):
        self.my_base = MyBase()
        Builder.load_file("main.kv")

    def on_start(self):

        try:
            with open('refresh_token.txt', 'r') as f:
                refresh_token = f.read()

            id_token, local_id = self.my_base.exchange_refresh_token(refresh_token)

            result = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/' + local_id + '.json?auth=' + id_token)
            data = json.loads(result.content.decode())
            self.root.ids['screen_manager'].transition = NoTransition()
            self.change_screen('home_screen')
            self.root.ids['screen_manager'].transition = CardTransition()

        except Exception:
            pass

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name

    def open_calendar(self):
        self.date.open()

    def show_date_picker(self):
        # можно поставить любую конкретную даты в скобках
        date_dialog = MDDatePicker()
        # можно выбрать диапазон, возвращает список с датами
        date_dialog = MDDatePicker(mode='range')
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        print(instance, value, date_range)

    def on_cancel(self, instance, value):
        # не понятно пока как добраться до атрибута text
        pprint(dir(self.root.ids['calendar_screen']))
        # print(self.root.ids.date_label.text)
        # self.root.ids.date_label.text = 'Cancel'


MainApp().run()
