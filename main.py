from pprint import pprint
from my_base import MyBase

from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
import requests
import json


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


class MainApp(MDApp):
    user_id = 1

    def build(self):

        self.my_base = MyBase()
        Builder.load_file("main.kv")

    def on_start(self):
        result = requests.get('https://zach-mobile-default-rtdb.firebaseio.com/Zach/Users' + str(self.user_id) + '.json')
        data = json.loads(result.content.decode())

        # # for name in data.keys():
        # #     print(name)
        # events = data['Stas']['events']
        # for event in events:
        #     print(events[event]['name'])
        #     print(events[event]['date'])

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name

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