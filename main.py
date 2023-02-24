from pprint import pprint
from kivy.uix.popup import Popup
from my_base import MyBase
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd_extensions.akivymd.uix.datepicker import AKDatePicker
from functools import partial
import projects
import calendar
import constants
import datetime
import requests
import json


# TODO

# иконки майка: активная/неактивная
# Размеры диалогового окна
# Активна или не активна кнопка Back


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


def start_calendar_fill(app):
    # инфо табло/calendar.month_name[month] - текущий месяц  + текущий год
    app.root.ids["event_calendar_screen"].ids["month"].text = calendar.month_name[EventCalendarScreen.month] + \
                                                              ', ' + str(EventCalendarScreen.year)

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
        formatting_label(app=app, day=n + 1, label_day_id=str(n + week_day), direction='ok')

        if EventCalendarScreen.year == EventCalendarScreen.now.year and EventCalendarScreen.month == \
                EventCalendarScreen.now.month and n == EventCalendarScreen.now.day:
            # красим сегодняшний день в зеленый
            app.root.ids["event_calendar_screen"].ids[
                str(EventCalendarScreen.now.day + week_day - 1)].background_color = \
                (7 / 255, 222 / 255, 67 / 255, 1)
            #     # остальные дни - серым
            app.root.ids["event_calendar_screen"].ids[str(n + week_day)].background_color = \
                (99 / 255, 97 / 255, 97 / 255, 1)
        else:
            app.root.ids["event_calendar_screen"].ids[str(n + week_day)].background_color = \
                (99 / 255, 97 / 255, 97 / 255, 1)

    # заполняем дни предыдущего месяца
    for n in range(week_day):
        formatting_label(app=app, day=back_month_days - n, label_day_id=str(week_day - n - 1), direction='back')
        app.root.ids["event_calendar_screen"].ids[str(week_day - n - 1)].text = str(back_month_days - n)
        app.root.ids["event_calendar_screen"].ids[str(week_day - n - 1)].background_color = \
            (193 / 255, 198 / 255, 198 / 255, 1)

    # заполняем дни следующего месяца
    for n in range(6 * 7 - month_days - week_day):
        formatting_label(app=app, day=n + 1, label_day_id=str(week_day + month_days + n), direction='next')
        app.root.ids["event_calendar_screen"].ids[str(week_day + month_days + n)].text = str(n + 1)
        app.root.ids["event_calendar_screen"].ids[str(week_day + month_days + n)].background_color = \
            (193 / 255, 198 / 255, 198 / 255, 1)
        # days[week_day + month_days + n]['fg'] = 'gray'


# Заполняем лэйбы с эвентами
def formatting_label(app, day, label_day_id, direction):
    day_events = 0
    current_month = EventCalendarScreen.month
    label_id = app.root.ids["event_calendar_screen"].ids[label_day_id + 'l']
    if direction == 'next':
        if EventCalendarScreen.month == 12:
            current_month = 1
        else:
            current_month = EventCalendarScreen.month + 1
    elif direction == 'back':
        if EventCalendarScreen.month == 0:
            current_month = 12
        else:
            current_month = EventCalendarScreen.month - 1
    form_day = app.formatted_date(current_month, day)
    # Проверка на наличие события
    if app.events_list:
        for event in app.events_list:
            if event['date'] == form_day:
                day_events += 1
            # отмечаем на календаре события
            label_id.text = f'{day_events} ev'
            if day_events > 0:
                label_id.background_color = (222 / 255, 121 / 255, 65 / 255, 1)
            else:
                label_id.background_color = (24 / 255, 171 / 255, 21 / 255, 1)
    else:
        label_id.text = f'{day_events} ev'
        label_id.background_color = (24 / 255, 171 / 255, 21 / 255, 1)


class MainApp(MDApp):
    previous_screen = 'home_screen'
    user_id = 1
    # эвент, с которым сейчас работаем
    operating_event = ''
    operating_task = ''
    # отбор по дате
    date_sort = None
    task_sort = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # список эвентов
        self.events_list = None
        # сортировать невыполненные задания
        self.task_sort = None
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
            self.events_filling(sort=None)
            self.tasks_filling(sort=self.task_sort)
            projects.fill_projects_screen()

        # Если нет, то остаёмся на экране логина
        except Exception:
            print('Not Ok')

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name

# ___________________________________Todo list________________________________________________________________________

    def save_new_task(self):
        description = self.root.ids["new_task_screen"].ids["task_description"].text
        # проверяем заполнение полей
        if description == '':
            self.root.ids["new_task_screen"].ids["task_info_label"].text = "Please fill in the description field"
        else:
            # Отправляем данные в firebase
            task_data_for_load = {'description': description, 'status': 'active'}
            if self.operating_task == '':
                # requests.post присваивает запросу ключ
                new_task_request = requests.post(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks.json?auth=%s'
                    % (self.local_id, self.id_token), data=json.dumps(task_data_for_load))
            # если task уже существует, то меняем
            else:
                edit_task_request = requests.patch(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                    % (self.local_id, self.operating_task, self.id_token), data=json.dumps(task_data_for_load))
                self.operating_task = ''

            self.clear_new_task_screen()
            self.refill_tasks_layouts(sort=self.task_sort)
            self.change_screen("todolist_screen")

    def clear_new_task_screen(self):
        self.root.ids["new_task_screen"].ids["task_info_label"].text = ''
        self.root.ids["new_task_screen"].ids["task_description"].text = ''

    # заполняет экран заданий
    def tasks_filling(self, sort):
        result = requests.get(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + self.local_id + '.json?auth=' + self.id_token)
        data = json.loads(result.content.decode())
        # BoxLayout в events_screen
        tasks_box_layout = self.root.ids['todolist_screen'].ids['tasks_layout']
        # Проверка на наличие заданий
        if 'tasks' in data:
            # словарь словарей
            tasks = data['tasks']
            # ключи событий
            tasks_keys = tasks.keys()
            # Сортировка заданий
            tasks_list = []
            # добавляем в словарь второго порядка поле с ключами
            for task_key in tasks_keys:
                tasks[task_key]['task_key'] = str(task_key)
                tasks_list.append(tasks[task_key])
            tasks_list = sorted(tasks_list, key=lambda x: (x['status'], ''),
                                reverse=False)
            # self.events_list = events_list
            # Заполнение
            active = 0
            inactive = 0
            for task in tasks_list:
                # добавляем в активные или не активные события
                if task['status'] == 'active':
                    layout_for_task = FloatLayout()
                    active += 1
                    description = Label(text=task['description'], size_hint=(.8, .4),
                                        pos_hint={"top": .7, "left": .5})

                    edit_button = ImageButton(source="icons/edit.png", size_hint=(.2, .2),
                                              pos_hint={"top": 1, "right": 1})
                    but_edit_callback = partial(self.edit_task, task['task_key'])
                    edit_button.bind(on_release=but_edit_callback)

                    copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
                                              pos_hint={"top": .75, "right": 1})
                    but_copy_callback = partial(self.copy_task, task['task_key'])
                    copy_button.bind(on_release=but_copy_callback)

                    done_button = ImageButton(source="icons/done.jpg", size_hint=(.2, .2),
                                              pos_hint={"top": .5, "right": 1})
                    but_done_callback = partial(self.done_task, task['task_key'])
                    done_button.bind(on_release=but_done_callback)

                    delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                                pos_hint={"top": .25, "right": 1})
                    but_delete_callback = partial(self.delete_task, task['task_key'])
                    delete_button.bind(on_release=but_delete_callback)

                    layout_for_task.add_widget(description)
                    layout_for_task.add_widget(edit_button)
                    layout_for_task.add_widget(copy_button)
                    layout_for_task.add_widget(done_button)
                    layout_for_task.add_widget(delete_button)
                    tasks_box_layout.add_widget(layout_for_task)
                elif task['status'] == 'inactive':
                    if sort is None:
                        layout_for_task = FloatLayout()
                        inactive += 1
                        description = Label(markup=True, text=f"[s]{task['description']}[/s]", size_hint=(.8, .4),
                                            pos_hint={"top": .7, "left": .5})

                        copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
                                                  pos_hint={"top": .75, "right": 1})
                        but_copy_callback = partial(self.copy_task, task['task_key'])
                        copy_button.bind(on_release=but_copy_callback)

                        delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                                    pos_hint={"top": .25, "right": 1})
                        but_delete_callback = partial(self.delete_task, task['task_key'])
                        delete_button.bind(on_release=but_delete_callback)

                        layout_for_task.add_widget(description)
                        layout_for_task.add_widget(copy_button)
                        layout_for_task.add_widget(delete_button)
                        tasks_box_layout.add_widget(layout_for_task)

            # Если нет активных заданий в списке
            if active == 0 and sort == 'Actual':
                l = Label(text='You have no scheduled tasks', font_size='20sp')
                tasks_box_layout.add_widget(l)
        # Нет никаких заданий в списке
        else:
            l = Label(text='You have no any tasks', font_size='20sp')
            tasks_box_layout.add_widget(l)

    def edit_task(self, *args):
        for arg in args:
            if arg.__class__ != ImageButton:
                edit_task_request = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                    % (self.local_id, arg, self.id_token))
                self.operating_task = arg
                self.fill_new_task_screen(edit_task_request)

    def copy_task(self, *args):
        for arg in args:
            if arg.__class__ != ImageButton:
                copy_task_request = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                    % (self.local_id, arg, self.id_token))
                self.fill_new_task_screen(copy_task_request)

    def done_task(self, *args):
        for arg in args:
            if arg.__class__ != ImageButton:
                edit_task_request = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                    % (self.local_id, arg, self.id_token))
                self.operating_task = arg
                self.fill_new_task_screen(edit_task_request)
                self.modal_task_window(name='Done!', label="It's finished?", command='patch')

    def delete_task(self, *args):
        for arg in args:
            if arg.__class__ != ImageButton:
                get_task_request = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                    % (self.local_id, arg, self.id_token))
                self.operating_task = arg
                self.modal_task_window(name='Delete!', label='Delete task!?', command='delete')
                self.fill_new_task_screen(get_task_request)

    def fill_new_task_screen(self, task_request):
        self.previous_screen = 'todolist_screen'
        task_data = json.loads(task_request.content.decode())
        self.root.ids["new_task_screen"].ids["task_info_label"].text = ''
        self.root.ids["new_task_screen"].ids["task_description"].text = task_data['description']
        self.change_screen('new_task_screen')

    # перезаполняет layouts с эвентами
    def refill_tasks_layouts(self, sort):
        tasks_box_layout = self.root.ids['todolist_screen'].ids['tasks_layout']
        for w in tasks_box_layout.walk():
            # Удаляем только FloatLayout
            if w.__class__ == FloatLayout or w.__class__ == Label:
                tasks_box_layout.remove_widget(w)
        self.tasks_filling(sort=sort)

    def modal_task_window(self, name, label, command):
        # Создаём модальное окно
        bl = BoxLayout(orientation='vertical')
        l = Label(text=label, font_size=12)
        bl.add_widget(l)
        bl2 = BoxLayout(orientation='horizontal')
        but_no = Button(text='No!', font_size=12, size_hint=(.3, .5))
        but_yes = Button(text='Yes!', font_size=12, size_hint=(.3, .5))
        bl2.add_widget(but_no)
        bl2.add_widget(but_yes)
        bl.add_widget(bl2)
        popup = Popup(title=name, content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
                      auto_dismiss=False)

        # усли не будешь менять статус
        def no(*args):
            popup.dismiss()
            self.change_screen(self.previous_screen)
            self.clear_new_task_screen()
            self.operating_task = ''

        # чтобы перенести в выполненные/удалить
        def yes(*args):
            popup.dismiss()
            if command == 'patch':
                done_task_request = requests.patch(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                    % (self.local_id, self.operating_task, self.id_token), data=json.dumps({'status': 'inactive'}))
            elif command == 'delete':
                delete_task_request = requests.delete(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                    % (self.local_id, self.operating_task, self.id_token))
            self.refill_tasks_layouts(sort=self.task_sort)
            self.change_screen(self.previous_screen)
            self.clear_new_task_screen()
            self.operating_task = ''

        but_no.bind(on_press=no)
        but_yes.bind(on_press=yes)
        popup.open()

    # ___________________________________Event calendar________________________________________________________________________

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

    def formatted_date(self, current_month, day):
        # форматируем дату и время
        if len(str(current_month)) < 2:
            formatted_month = '0' + str(current_month)
        else:
            formatted_month = current_month
        if len(str(day)) < 2:
            formatted_day = '0' + str(day)
        else:
            formatted_day = day
        return f"{EventCalendarScreen.year}-{formatted_month}-{formatted_day}"

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
        elif int(name) >= week_day + month_days:
            current_month += 1

        formatted_date = self.formatted_date(current_month, day)

        if self.previous_screen == "new_event_screen":
            # проверяем, чтобы дата была не меньше текущей
            if EventCalendarScreen.year > EventCalendarScreen.now.year:
                # переносит на экран создания нового эвента
                self.change_screen(self.previous_screen)
                # заполняет поле с датой
                self.root.ids["new_event_screen"].ids["chosen_date"].text = formatted_date
            elif EventCalendarScreen.year >= EventCalendarScreen.now.year and current_month > \
                    EventCalendarScreen.now.month:
                self.change_screen(self.previous_screen)
                self.root.ids["new_event_screen"].ids["chosen_date"].text = formatted_date
            elif EventCalendarScreen.year >= EventCalendarScreen.now.year and current_month >= \
                    EventCalendarScreen.now.month and int(day) >= EventCalendarScreen.now.day:
                self.change_screen(self.previous_screen)
                self.root.ids["new_event_screen"].ids["chosen_date"].text = formatted_date
        # Отбираем события по дате
        else:
            self.date_sort = formatted_date
            # лепит автоматом в новый эвент дату из сортировки
            self.root.ids["new_event_screen"].ids["chosen_date"].text = formatted_date
            self.root.ids["events_screen"].ids["sort_by_date"].text = self.date_sort
            self.root.ids["inactive_events_screen"].ids["inactive_sort_by_date"].text = self.date_sort
            self.refill_events_layouts(sort=self.date_sort)
            self.change_screen('events_screen')

    # заполняет экран эвентов
    def events_filling(self, sort):
        result = requests.get(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + self.local_id + '.json?auth=' + self.id_token)
        data = json.loads(result.content.decode())
        # BoxLayout в events_screen
        events_box_layout = self.root.ids['events_screen'].ids['events_layout']
        inactive_events_box_layout = self.root.ids['inactive_events_screen'].ids['inactive_events_layout']
        # Проверка на наличие события
        if 'events' in data:
            events = data['events']
            # ключи событий
            events_keys = events.keys()

            # Сортировка событий
            events_list = []
            # добавляем в словарь второго порядка поле с ключами
            for event_key in events_keys:
                events[event_key]['event_key'] = str(event_key)
                events_list.append(events[event_key])
            events_list = sorted(events_list,
                                 key=lambda x: datetime.datetime.strptime(x['date_time'], '%Y-%m-%d %H:%M:%S'),
                                 reverse=False)
            self.events_list = events_list
            # Заполнение
            active = 0
            inactive = 0
            for event in events_list:
                if sort is None or sort == event['date']:
                    layout_for_event = FloatLayout()
                    # добавляем в активные или не активные события
                    if event['status'] == 'active':
                        active += 1
                        title = Label(text=event['title'], size_hint=(.8, .3),
                                      pos_hint={"top": 1, "left": .5})
                        description = Label(text=event['description'], size_hint=(.8, .4),
                                            pos_hint={"top": .7, "left": .5})
                        date = Label(text=event['date'], size_hint=(.4, .3),
                                     pos_hint={"top": .3, "left": .5})
                        time = Label(text=event['time'], size_hint=(.4, .3),
                                     pos_hint={"top": .3, "right": .8})

                        edit_button = ImageButton(source="icons/edit.png", size_hint=(.2, .2),
                                                  pos_hint={"top": 1, "right": 1})
                        but_edit_callback = partial(self.edit_event, event['event_key'])
                        edit_button.bind(on_release=but_edit_callback)

                        copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
                                                  pos_hint={"top": .75, "right": 1})
                        but_copy_callback = partial(self.copy_event, event['event_key'])
                        copy_button.bind(on_release=but_copy_callback)

                        done_button = ImageButton(source="icons/done.jpg", size_hint=(.2, .2),
                                                  pos_hint={"top": .5, "right": 1})
                        but_done_callback = partial(self.done_event, event['event_key'])
                        done_button.bind(on_release=but_done_callback)

                        delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                                    pos_hint={"top": .25, "right": 1})
                        but_delete_callback = partial(self.delete_event, event['event_key'])
                        delete_button.bind(on_release=but_delete_callback)

                        layout_for_event.add_widget(title)
                        layout_for_event.add_widget(description)
                        layout_for_event.add_widget(date)
                        layout_for_event.add_widget(time)
                        layout_for_event.add_widget(edit_button)
                        layout_for_event.add_widget(copy_button)
                        layout_for_event.add_widget(done_button)
                        layout_for_event.add_widget(delete_button)
                        events_box_layout.add_widget(layout_for_event)
                    elif event['status'] == 'inactive':
                        inactive += 1
                        title = Label(text=event['title'], size_hint=(.8, .3),
                                      pos_hint={"top": 1, "left": .5})
                        description = Label(text=event['description'], size_hint=(.8, .4),
                                            pos_hint={"top": .7, "left": .5})
                        date = Label(text=event['date'], size_hint=(.4, .3),
                                     pos_hint={"top": .3, "left": .5})
                        time = Label(text=event['time'], size_hint=(.4, .3),
                                     pos_hint={"top": .3, "right": .8})

                        copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
                                                  pos_hint={"top": .9, "right": 1})
                        but_copy_callback = partial(self.copy_event, event['event_key'])
                        copy_button.bind(on_release=but_copy_callback)

                        delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                                    pos_hint={"top": .3, "right": 1})
                        but_delete_callback = partial(self.delete_event, event['event_key'])
                        delete_button.bind(on_release=but_delete_callback)
                        layout_for_event.add_widget(title)
                        layout_for_event.add_widget(description)
                        layout_for_event.add_widget(date)
                        layout_for_event.add_widget(time)
                        layout_for_event.add_widget(copy_button)
                        layout_for_event.add_widget(delete_button)
                        inactive_events_box_layout.add_widget(layout_for_event)

            # Если нет эвентов в списке
            if active == 0:
                l = Label(text='You have no scheduled events', font_size='20sp')
                events_box_layout.add_widget(l)
            if inactive == 0:
                l = Label(text='You have no completed events', font_size='20sp')
                inactive_events_box_layout.add_widget(l)
        else:
            l = Label(text='You have no scheduled events', font_size='20sp')
            events_box_layout.add_widget(l)
            l = Label(text='You have no completed events', font_size='20sp')
            inactive_events_box_layout.add_widget(l)
        # заполняем календарь
        start_calendar_fill(self)

    # перезаполняет layouts с эвентами
    def refill_events_layouts(self, sort):
        events_box_layout = self.root.ids['events_screen'].ids['events_layout']
        inactive_events_box_layout = self.root.ids['inactive_events_screen'].ids['inactive_events_layout']
        for w in events_box_layout.walk():
            # Удаляем только FloatLayout
            if w.__class__ == FloatLayout or w.__class__ == Label:
                events_box_layout.remove_widget(w)
        for w in inactive_events_box_layout.walk():
            if w.__class__ == FloatLayout or w.__class__ == Label:
                inactive_events_box_layout.remove_widget(w)
        self.events_filling(sort=sort)

    def save_new_event(self):
        title = self.root.ids["new_event_screen"].ids["title"].text
        description = self.root.ids["new_event_screen"].ids["description"].text
        time = self.root.ids["new_event_screen"].ids["chosen_time"].text
        date = self.root.ids["new_event_screen"].ids["chosen_date"].text
        date_time = f"{date} {time}"
        # проверяем заполнение полей
        if title == '':
            self.root.ids["new_event_screen"].ids["info_label"].text = "Please fill in the title field"
        elif description == '':
            self.root.ids["new_event_screen"].ids["info_label"].text = "Please fill in the description field"
        elif date == 'date':
            self.root.ids["new_event_screen"].ids["info_label"].text = "Please chose the date"
        elif time == 'time':
            self.root.ids["new_event_screen"].ids["info_label"].text = "Please chose the time"
        else:
            # Отправляем данные в firebase

            event_data_for_load = {'title': title, 'description': description, 'time': time, 'date': date,
                                   'status': 'active', 'date_time': date_time}
            if self.operating_event == '':
                # requests.post присваивает запросу ключ
                new_event_request = requests.post(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/events.json?auth=%s'
                    % (self.local_id, self.id_token), data=json.dumps(event_data_for_load))
            # если эвент уже существует, то меняем
            else:
                edit_event_request = requests.patch(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'
                    % (self.local_id, self.operating_event, self.id_token), data=json.dumps(event_data_for_load))
                self.operating_event = ''

            self.clear_new_event_screen()
            self.change_screen("events_screen")
            self.refill_events_layouts(sort=self.date_sort)

    def clear_new_event_screen(self):
        self.root.ids["new_event_screen"].ids["info_label"].text = ''
        self.root.ids["new_event_screen"].ids["title"].text = ''
        self.root.ids["new_event_screen"].ids["description"].text = ''
        self.root.ids["new_event_screen"].ids["chosen_time"].text = 'time'
        self.root.ids["new_event_screen"].ids["chosen_date"].text = 'date'

    def edit_event(self, *args):
        for arg in args:
            if arg.__class__ != ImageButton:
                edit_event_request = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'
                    % (self.local_id, arg, self.id_token))
                self.operating_event = arg
                self.fill_new_event_screen(edit_event_request)

    def done_event(self, *args):
        for arg in args:
            if arg.__class__ != ImageButton:
                edit_event_request = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'
                    % (self.local_id, arg, self.id_token))
                self.operating_event = arg
                self.fill_new_event_screen(edit_event_request)
                self.modal_event_window(name='Done!', label="It's finished?", command='patch')

    def delete_event(self, *args):
        for arg in args:
            if arg.__class__ != ImageButton:
                get_event_request = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'
                    % (self.local_id, arg, self.id_token))
                self.operating_event = arg
                self.modal_event_window(name='Delete!', label='Delete event!?', command='delete')
                self.fill_new_event_screen(get_event_request)

    def copy_event(self, *args):
        for arg in args:
            if arg.__class__ != ImageButton:
                copy_event_request = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'
                    % (self.local_id, arg, self.id_token))
                self.fill_new_event_screen(copy_event_request)

    def fill_new_event_screen(self, event_request):
        event_data = json.loads(event_request.content.decode())
        if event_data['status'] == 'inactive':
            self.previous_screen = 'inactive_events_screen'
        else:
            self.previous_screen = 'events_screen'
        self.root.ids["new_event_screen"].ids["info_label"].text = ''
        self.root.ids["new_event_screen"].ids["title"].text = event_data['title']
        self.root.ids["new_event_screen"].ids["description"].text = event_data['description']
        self.root.ids["new_event_screen"].ids["chosen_time"].text = event_data['time']
        self.root.ids["new_event_screen"].ids["chosen_date"].text = event_data['date']
        self.change_screen('new_event_screen')

    def modal_event_window(self, name, label, command):
        # Создаём модальное окно
        bl = BoxLayout(orientation='vertical')
        l = Label(text=label, font_size=12)
        bl.add_widget(l)
        bl2 = BoxLayout(orientation='horizontal')
        but_no = Button(text='No!', font_size=12, size_hint=(.3, .5))
        but_yes = Button(text='Yes!', font_size=12, size_hint=(.3, .5))
        bl2.add_widget(but_no)
        bl2.add_widget(but_yes)
        bl.add_widget(bl2)
        popup = Popup(title=name, content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
                      auto_dismiss=False)

        # усли не будешь менять статус
        def no(*args):
            popup.dismiss()
            self.change_screen(self.previous_screen)
            self.clear_new_event_screen()
            self.operating_event = ''

        # чтобы перенести в выполненные/удалить
        def yes(*args):
            popup.dismiss()
            if command == 'patch':
                done_event_request = requests.patch(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'
                    % (self.local_id, self.operating_event, self.id_token), data=json.dumps({'status': 'inactive'}))
            elif command == 'delete':
                delete_event_request = requests.delete(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'
                    % (self.local_id, self.operating_event, self.id_token), data=json.dumps({'status': 'inactive'}))
            self.refill_events_layouts(sort=self.date_sort)
            self.change_screen(self.previous_screen)
            self.clear_new_event_screen()
            self.operating_event = ''

        but_no.bind(on_press=no)
        but_yes.bind(on_press=yes)
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
