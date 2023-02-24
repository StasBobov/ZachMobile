import json
import logging
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from own_classes import ImageButton
from functools import partial
import constants


log = logging.getLogger('tasks_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

class Task:
    operating_task = ''
    task_sort = None


def save_new_task():
    app = App.get_running_app()

    description = app.root.ids["new_task_screen"].ids["task_description"].text
    # проверяем заполнение полей
    if description == '':
        app.root.ids["new_task_screen"].ids["task_info_label"].text = "Please fill in the description field"
    else:
        # Отправляем данные в firebase
        task_data_for_load = {'description': description, 'status': 'active'}
        if Task.operating_task == '':
            # requests.post присваивает запросу ключ
            log.info('Sends new task data to the server')
            new_task_request = requests.post(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks.json?auth=%s'
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(task_data_for_load))
            log.info(new_task_request)
        # если task уже существует, то меняем
        else:
            log.info('Sends patch task data to the server')
            edit_task_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                % (constants.LOCAL_ID, Task.operating_task, constants.ID_TOKEN), data=json.dumps(task_data_for_load))
            Task.operating_task = ''
            log.info(edit_task_request)
        clear_new_task_screen()
        refill_tasks_layouts(sort=Task.task_sort)
        app.change_screen("todolist_screen")


def clear_new_task_screen():
    app = App.get_running_app()
    app.root.ids["new_task_screen"].ids["task_info_label"].text = ''
    app.root.ids["new_task_screen"].ids["task_description"].text = ''


# заполняет экран заданий
def tasks_filling(sort):
    app = App.get_running_app()

    result = requests.get(
        'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
    log.debug(f'Get app task data from the server {result}')
    data = json.loads(result.content.decode())
    # BoxLayout в events_screen
    tasks_box_layout = app.root.ids['todolist_screen'].ids['tasks_layout']
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
                but_edit_callback = partial(edit_task, task['task_key'])
                edit_button.bind(on_release=but_edit_callback)

                copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
                                          pos_hint={"top": .75, "right": 1})
                but_copy_callback = partial(copy_task, task['task_key'])
                copy_button.bind(on_release=but_copy_callback)

                done_button = ImageButton(source="icons/done.jpg", size_hint=(.2, .2),
                                          pos_hint={"top": .5, "right": 1})
                but_done_callback = partial(done_task, task['task_key'])
                done_button.bind(on_release=but_done_callback)

                delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                            pos_hint={"top": .25, "right": 1})
                but_delete_callback = partial(delete_task, task['task_key'])
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
                    but_copy_callback = partial(copy_task, task['task_key'])
                    copy_button.bind(on_release=but_copy_callback)

                    delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                                pos_hint={"top": .25, "right": 1})
                    but_delete_callback = partial(delete_task, task['task_key'])
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


def edit_task(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            edit_task_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for edit task')
            Task.operating_task = arg
            fill_new_task_screen(edit_task_request)


def copy_task(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            copy_task_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for copy task')
            fill_new_task_screen(copy_task_request)


def done_task(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            edit_task_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for make task done')

            Task.operating_task = arg
            fill_new_task_screen(edit_task_request)
            modal_task_window(name='Done!', label="It's finished?", command='patch')


def delete_task(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            get_task_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for delete task')
            Task.operating_task = arg
            modal_task_window(name='Delete!', label='Delete task!?', command='delete')
            fill_new_task_screen(get_task_request)


def fill_new_task_screen(task_request):
    app = App.get_running_app()

    app.previous_screen = 'todolist_screen'
    task_data = json.loads(task_request.content.decode())
    app.root.ids["new_task_screen"].ids["task_info_label"].text = ''
    app.root.ids["new_task_screen"].ids["task_description"].text = task_data['description']
    app.change_screen('new_task_screen')


# перезаполняет layouts с эвентами
def refill_tasks_layouts(sort):
    app = App.get_running_app()

    tasks_box_layout = app.root.ids['todolist_screen'].ids['tasks_layout']
    for w in tasks_box_layout.walk():
        # Удаляем только FloatLayout
        if w.__class__ == FloatLayout or w.__class__ == Label:
            tasks_box_layout.remove_widget(w)
    tasks_filling(sort=sort)


def modal_task_window(name, label, command):
    app = App.get_running_app()

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
        app.change_screen(app.previous_screen)
        clear_new_task_screen()
        Task.operating_task = ''

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        popup.dismiss()
        if command == 'patch':
            log.info('Patch data on server')
            done_task_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                % (constants.LOCAL_ID, Task.operating_task, constants.ID_TOKEN), data=json.dumps({'status': 'inactive'}))
            log.info(done_task_request)
        elif command == 'delete':
            log.info('Delete data on server')
            delete_task_request = requests.delete(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                % (constants.LOCAL_ID, Task.operating_task, constants.ID_TOKEN))
            log.info(delete_task_request)
        refill_tasks_layouts(sort=Task.task_sort)
        app.change_screen(app.previous_screen)
        clear_new_task_screen()
        Task.operating_task = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()