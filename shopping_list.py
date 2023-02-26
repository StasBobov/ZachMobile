import json
import logging
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from own_classes import ImageButton
from functools import partial
import constants

log = logging.getLogger('shopping_list_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


class Purchase:
    operating_purchase = ''
    purchase_sort = None


def save_new_purchase(text):
    app = App.get_running_app()
    if text:
        purchase_text = text
        purchase_data_for_load = {'purchase_text': text, 'status': 'active'}
        if Purchase.operating_purchase == '':
            # requests.post присваивает запросу ключ
            log.info('Sends new purchase data to the server')
            new_purchase_request = requests.post(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list.json?auth=%s'
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(purchase_data_for_load))
            log.info(new_purchase_request)
            # TODO не факт что нужно
        # если purchase уже существует, то меняем
        else:
            log.info('Sends patch purchase data to the server')
            edit_purchase_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
                % (constants.LOCAL_ID, Purchase.operating_purchase, constants.ID_TOKEN),
                data=json.dumps(purchase_data_for_load))
            Purchase.operating_purchase = ''
            log.info(edit_purchase_request)
        # refill_tasks_layouts(sort=Purchase.purchase_sort)
        app.change_screen("shopping_list_screen")


# заполняет экран заданий
def shopping_list_filling(sort):
    app = App.get_running_app()

    # TODO здесь нужно будет добавить подгрузку с файла
    result = requests.get(
        'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
    log.debug(f'Get app task data from the server {result}')
    data = json.loads(result.content.decode())

    shopping_list_layout = app.root.ids['shopping_list_screen'].ids['shopping_layout']
    # Проверка на наличие заданий
    if 'shop_list' in data:
        # словарь словарей
        purchases = data['shop_list']
        # ключи событий
        purchase_keys = purchases.keys()
        # Сортировка заданий
        purchase_list = []
        # добавляем в словарь второго порядка по ключам поля с ключами 'purchase_key' и значениями - ключ
        for purchase_key in purchase_keys:
            purchases[purchase_key]['purchase_key'] = str(purchase_key)
            purchase_list.append(purchases[purchase_key])
        purchase_list = sorted(purchase_list, key=lambda x: (x['status'], ''),
                            reverse=False)
        # Заполнение
        active = 0
        inactive = 0
        for purchase in purchase_list:
            # добавляем в активные или не активные события
            if purchase['status'] == 'active':
                layout_for_purchase = FloatLayout()
                active += 1
                description = Label(text=purchase['purchase_text'], size_hint=(.8, .4),
                                    pos_hint={"top": .7, "left": .5})
                edit_button = ImageButton(source="icons/edit.png", size_hint=(.2, .2),
                                          pos_hint={"top": 1, "right": 1})
                but_edit_callback = partial(edit_purchase, purchase["purchase_key"])
                edit_button.bind(on_release=but_edit_callback)

#
#                 copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
#                                           pos_hint={"top": .75, "right": 1})
#                 but_copy_callback = partial(copy_task, task['task_key'])
#                 copy_button.bind(on_release=but_copy_callback)
#
#                 done_button = ImageButton(source="icons/done.jpg", size_hint=(.2, .2),
#                                           pos_hint={"top": .5, "right": 1})
#                 but_done_callback = partial(done_task, task['task_key'])
#                 done_button.bind(on_release=but_done_callback)
#
#                 delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
#                                             pos_hint={"top": .25, "right": 1})
#                 but_delete_callback = partial(delete_task, task['task_key'])
#                 delete_button.bind(on_release=but_delete_callback)
#
                layout_for_purchase.add_widget(description)
                layout_for_purchase.add_widget(edit_button)
#                 layout_for_task.add_widget(copy_button)
#                 layout_for_task.add_widget(done_button)
#                 layout_for_task.add_widget(delete_button)
                shopping_list_layout.add_widget(layout_for_purchase)
#             elif task['status'] == 'inactive':
#                 if sort is None:
#                     layout_for_task = FloatLayout()
#                     inactive += 1
#                     description = Label(markup=True, text=f"[s]{task['description']}[/s]", size_hint=(.8, .4),
#                                         pos_hint={"top": .7, "left": .5})
#
#                     copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
#                                               pos_hint={"top": .75, "right": 1})
#                     but_copy_callback = partial(copy_task, task['task_key'])
#                     copy_button.bind(on_release=but_copy_callback)
#
#                     delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
#                                                 pos_hint={"top": .25, "right": 1})
#                     but_delete_callback = partial(delete_task, task['task_key'])
#                     delete_button.bind(on_release=but_delete_callback)
#
#                     layout_for_task.add_widget(description)
#                     layout_for_task.add_widget(copy_button)
#                     layout_for_task.add_widget(delete_button)
#                     tasks_box_layout.add_widget(layout_for_task)
#
#         # Если нет активных заданий в списке
#         if active == 0 and sort == 'Actual':
#             l = Label(text='You have no scheduled tasks', font_size='20sp')
#             tasks_box_layout.add_widget(l)
#     # Нет никаких заданий в списке
#     else:
#         l = Label(text='You have no any tasks', font_size='20sp')
#         tasks_box_layout.add_widget(l)


def edit_purchase(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            # по ключу мы достаём запись
            edit_purchase_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for edit purchase')
            Purchase.operating_purchase = arg
            modal_edit_purchase_window(command='edit', purchase_request=edit_purchase_request)

#
#
# def copy_task(*args):
#     for arg in args:
#         if arg.__class__ != ImageButton:
#             copy_task_request = requests.get(
#                 'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
#                 % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
#             log.debug('Get data from server for copy task')
#             fill_new_task_screen(copy_task_request)
#
#
# def done_task(*args):
#     for arg in args:
#         if arg.__class__ != ImageButton:
#             edit_task_request = requests.get(
#                 'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
#                 % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
#             log.debug('Get data from server for make task done')
#
#             Task.operating_task = arg
#             fill_new_task_screen(edit_task_request)
#             modal_task_window(name='Done!', label="It's finished?", command='patch')
#
#
# def delete_task(*args):
#     for arg in args:
#         if arg.__class__ != ImageButton:
#             get_task_request = requests.get(
#                 'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
#                 % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
#             log.debug('Get data from server for delete task')
#             Task.operating_task = arg
#             modal_task_window(name='Delete!', label='Delete task!?', command='delete')
#             fill_new_task_screen(get_task_request)
#
#
# def delete_all_completed_tasks(*args):
#     result = requests.get(
#         'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
#     log.debug(f'Get app task data from the server {result}')
#     data = json.loads(result.content.decode())
#     inactive_tasks = set()
#     if 'tasks' in data:
#         # словарь словарей
#         tasks = data['tasks']
#         # ключи словаря - идентификаторы в базе
#         task_keys = tasks.keys()
#         # проходим по значениям через ключи словаря
#         for task_key in task_keys:
#             if tasks[task_key]['status'] == 'inactive':
#                 inactive_tasks.add(task_key)
#
#     if inactive_tasks:
#         modal_task_window(name='Delete all inactive tasks!!!', label='Delete all inactive task!!!?', command='delete_all',
#                           amount=inactive_tasks)
#     else:
#         pass
#
#
# def fill_new_task_screen(task_request):
#     app = App.get_running_app()
#
#     app.previous_screen = 'todolist_screen'
#     task_data = json.loads(task_request.content.decode())
#     app.root.ids["new_task_screen"].ids["task_info_label"].text = ''
#     app.root.ids["new_task_screen"].ids["task_description"].text = task_data['description']
#     app.change_screen('new_task_screen')
#
#
# # перезаполняет layouts с эвентами
# def refill_tasks_layouts(sort):
#     app = App.get_running_app()
#
#     tasks_box_layout = app.root.ids['todolist_screen'].ids['tasks_layout']
#     for w in tasks_box_layout.walk():
#         # Удаляем только FloatLayout
#         if w.__class__ == FloatLayout or w.__class__ == Label:
#             tasks_box_layout.remove_widget(w)
#     tasks_filling(sort=sort)


def modal_edit_purchase_window(command, purchase_request):
    app = App.get_running_app()
    purchase_data = json.loads(purchase_request.content.decode())

    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    t_i = TextInput(text=purchase_data['purchase_text'], size_hint=  (1, .3),
            pos_hint={'top': .85, 'right': 1})
    bl.add_widget(t_i)
    bl2 = BoxLayout(orientation='horizontal')
    but_no = Button(text='Back without saving', font_size=12, size_hint=(.3, .5))
    but_yes = Button(text='Edit purchase!', font_size=12, size_hint=(.3, .5))
    bl2.add_widget(but_no)
    bl2.add_widget(but_yes)
    bl.add_widget(bl2)
    popup = Popup(title="Edit purchase", content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
                  auto_dismiss=False)

    # если не сохранять
    def no(*args):
        popup.dismiss()
        app.change_screen("shopping_list_screen")

    # чтобы изменить пункт
    def yes(*args):
        popup.dismiss()
        if command == 'edit':
            log.info('Patch data on server')
            done_purchase_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                % (constants.LOCAL_ID, Purchase.operating_purchase, constants.ID_TOKEN), data=json.dumps({'purchase_text': t_i.text}))
            log.info(done_purchase_request)
    #     elif command == 'delete':
    #         log.info('Delete data on server')
    #         delete_task_request = requests.delete(
    #             'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
    #             % (constants.LOCAL_ID, Task.operating_task, constants.ID_TOKEN))
    #         log.info(delete_task_request)
    #     elif command == 'delete_all':
    #         for task_key in amount:
    #             log.info('Delete data on server')
    #             delete_task_request = requests.delete(
    #                 'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
    #                 % (constants.LOCAL_ID, task_key, constants.ID_TOKEN))
    #             log.info(delete_task_request)
    #     refill_tasks_layouts(sort=Task.task_sort)
    #     app.change_screen(app.previous_screen)
    #     clear_new_task_screen()
    #     Task.operating_task = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()
#
# def modal_task_window(name, label, command, amount=None):
#     app = App.get_running_app()
#
#     # Создаём модальное окно
#     bl = BoxLayout(orientation='vertical')
#     l = Label(text=label, font_size=12)
#     bl.add_widget(l)
#     bl2 = BoxLayout(orientation='horizontal')
#     but_no = Button(text='No!', font_size=12, size_hint=(.3, .5))
#     but_yes = Button(text='Yes!', font_size=12, size_hint=(.3, .5))
#     bl2.add_widget(but_no)
#     bl2.add_widget(but_yes)
#     bl.add_widget(bl2)
#     popup = Popup(title=name, content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
#                   auto_dismiss=False)
#
#     # усли не будешь менять статус
#     def no(*args):
#         popup.dismiss()
#         app.change_screen(app.previous_screen)
#         clear_new_task_screen()
#         Task.operating_task = ''
#
#     # чтобы перенести в выполненные/удалить
#     def yes(*args):
#         popup.dismiss()
#         if command == 'patch':
#             log.info('Patch data on server')
#             done_task_request = requests.patch(
#                 'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
#                 % (constants.LOCAL_ID, Task.operating_task, constants.ID_TOKEN), data=json.dumps({'status': 'inactive'}))
#             log.info(done_task_request)
#         elif command == 'delete':
#             log.info('Delete data on server')
#             delete_task_request = requests.delete(
#                 'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
#                 % (constants.LOCAL_ID, Task.operating_task, constants.ID_TOKEN))
#             log.info(delete_task_request)
#         elif command == 'delete_all':
#             for task_key in amount:
#                 log.info('Delete data on server')
#                 delete_task_request = requests.delete(
#                     'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'
#                     % (constants.LOCAL_ID, task_key, constants.ID_TOKEN))
#                 log.info(delete_task_request)
#         refill_tasks_layouts(sort=Task.task_sort)
#         app.change_screen(app.previous_screen)
#         clear_new_task_screen()
#         Task.operating_task = ''
#
#     but_no.bind(on_press=no)
#     but_yes.bind(on_press=yes)
#     popup.open()
