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
import calendar
import datetime
import requests
import json


class EventCalendarScreen(Screen):
    days = []
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # for row in range(6):
        #     for col in range(7):
        #         _date = '0'
        #         # заполнили словарь объектами с текстом 0
        #         self.days.append(_date)


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


def start_calendar_fill(app):
    # инфо табло/calendar.month_name[month] - текущий месяц  + текущий год
    app.root.ids["event_calendar_screen"].ids["month"].text = calendar.month_name[EventCalendarScreen.month] + \
                                                               ', ' + str(EventCalendarScreen.year)
    for num in range(42):
        EventCalendarScreen.days.append(num)
    # for row in range(6):
    #     for col in range(7):
    #         _date = '0'
    #         # заполнили список объектами с текстом 0
    #         EventCalendarScreen.days.append(_date)
    # calendar.monthrange(year, month)[1] - дней в текущем месяце текущего года
    month_days = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month)[1]
    # если январь
    if EventCalendarScreen.month == 1:
        # дней в декабре прошлого года
        back_month_days = calendar.monthrange(EventCalendarScreen.year - 1, 12)[1]
    else:
        # дней в прошлом месяце текущего года
        back_month_days = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month - 1)[1]
    # первый день месяца (понедельник - 0)
    week_day = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month)[0]

    # n - дни текущего месяца текущего года с 0
    for n in range(month_days):
        # в списке объекту Button по индексам дням присваиваются числа в поле text
        app.root.ids["event_calendar_screen"].ids[str(n + week_day)].text = str(n + 1)
        # days[n + week_day]['text'] = n + 1
        # days[n + week_day]['fg'] = 'black'
        # if EventCalendarScreen.year == EventCalendarScreen.now.year and EventCalendarScreen.month == \
        #         EventCalendarScreen.now.month and n == EventCalendarScreen.now.day:
        #     # красим сегодняшний день в зеленый
        #     days[now.day + week_day - 1]['bg'] = 'green'
        #     # остальные дни - серым
        #     days[n + week_day]['bg'] = 'grey'
        # else:
        #     days[n + week_day]['bg'] = 'grey'


class MainApp(MDApp):
    user_id = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date = AKDatePicker(callback=self.callback)

    def callback(self, date):
        pass

    def build(self):
        self.my_base = MyBase()
        Builder.load_file("main.kv")

    def on_start(self):
        print(self.root.ids["event_calendar_screen"].ids["month"].text)

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

            start_calendar_fill(self)

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
