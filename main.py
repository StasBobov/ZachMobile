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


class NewEventScreen(Screen):
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


def start_calendar_fill(app):
    # инфо табло/calendar.month_name[month] - текущий месяц  + текущий год
    app.root.ids["event_calendar_screen"].ids["month"].text = calendar.month_name[EventCalendarScreen.month] + \
                                                               ', ' + str(EventCalendarScreen.year)
    for num in range(42):
        EventCalendarScreen.days.append(num)
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
        # days[n + week_day]['fg'] = 'black' #TODO
        if EventCalendarScreen.year == EventCalendarScreen.now.year and EventCalendarScreen.month == \
                EventCalendarScreen.now.month and n == EventCalendarScreen.now.day:
            # красим сегодняшний день в зеленый
            app.root.ids["event_calendar_screen"].ids[str(EventCalendarScreen.now.day + week_day - 1)].background_color = \
                (7/255, 222/255, 67/255, 1)
        #     # остальные дни - серым
            app.root.ids["event_calendar_screen"].ids[str(n + week_day)].background_color = \
            (99/255, 97/255, 97/255, 1)
        else:
            app.root.ids["event_calendar_screen"].ids[str(n + week_day)].background_color = \
            (99/255, 97/255, 97/255, 1)


    # заполняем дни предыдущего месяца
    for n in range(week_day):
        app.root.ids["event_calendar_screen"].ids[str(week_day - n - 1)].text = str(back_month_days - n)
        app.root.ids["event_calendar_screen"].ids[str(week_day - n - 1)].background_color = \
            (193/ 255, 198/ 255, 198/ 255, 1)
        # days[week_day - n - 1]['fg'] = 'gray'
    # заполняем дни следующего месяца
    for n in range(6 * 7 - month_days - week_day):
        app.root.ids["event_calendar_screen"].ids[str(week_day + month_days + n)].text = str(n + 1)
        app.root.ids["event_calendar_screen"].ids[str(week_day + month_days + n)].background_color = \
            (193/ 255, 198/ 255, 198/ 255, 1)
        # days[week_day + month_days + n]['fg'] = 'gray'


class MainApp(MDApp):
    previous_screen = 'home_screen'
    user_id = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date = AKDatePicker(callback=self.callback)

    def callback(self, date):
        pass

    def month_back(self):
        EventCalendarScreen.month -= 1
        if EventCalendarScreen.month == 0:
            EventCalendarScreen.month = 12
            EventCalendarScreen.year -= 1
        start_calendar_fill(self)

    def month_next(self):
        EventCalendarScreen.month += 1
        if EventCalendarScreen.month == 13:
            EventCalendarScreen.month = 1
            EventCalendarScreen.year += 1
        start_calendar_fill(self)

    # после нажатия на дату отправляет на предыдущий экран
    def calendar_button_release(self, day, name):
        current_month = EventCalendarScreen.month
        # дни текущего месяца текущего года
        month_days = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month)[1]
        # первый день месяца (понедельник - 0)
        week_day = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month)[0]
        # если нажал на день предыдущего месяца
        if int(name) < week_day:
            # месяц считается предыдущим
            current_month -= 1
            # если переходили из создания нового эвента
        elif int(name) >= week_day + month_days:
            current_month += 1

        if self.previous_screen == "new_event_screen":
            # проверяем, чтобы дата была не меньше текущей
            if EventCalendarScreen.year > EventCalendarScreen.now.year:
                self.change_screen(self.previous_screen)
                self.root.ids["new_event_screen"].ids["chosen_date"].text = f"{day}/{current_month}/"\
                                                                            f"{EventCalendarScreen.year}"
            elif EventCalendarScreen.year >= EventCalendarScreen.now.year and current_month > \
                    EventCalendarScreen.now.month:
                self.change_screen(self.previous_screen)
                self.root.ids["new_event_screen"].ids["chosen_date"].text = f"{day}/{current_month}/"\
                                                                            f"{EventCalendarScreen.year}"
            elif EventCalendarScreen.year >= EventCalendarScreen.now.year and current_month >= \
                    EventCalendarScreen.now.month and int(day) >= EventCalendarScreen.now.day:
                        self.change_screen(self.previous_screen)
                        self.root.ids["new_event_screen"].ids["chosen_date"].text = f"{day} / {current_month} /" \
                                                                                    f" {EventCalendarScreen.year}"


    def build(self):
        self.theme_cls.theme_style = 'Light'
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
