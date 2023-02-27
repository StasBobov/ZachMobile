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
        refill_shopping_list_layout()
        app.change_screen("shopping_list_screen")


def shopping_list_filling():
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

                copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
                                          pos_hint={"top": .75, "right": 1})
                but_copy_callback = partial(copy_purchase, purchase["purchase_key"])
                copy_button.bind(on_release=but_copy_callback)

                done_button = ImageButton(source="icons/done.jpg", size_hint=(.2, .2),
                                          pos_hint={"top": .5, "right": 1})
                but_done_callback = partial(done_purchase, purchase["purchase_key"])
                done_button.bind(on_release=but_done_callback)

                delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                            pos_hint={"top": .25, "right": 1})
                but_delete_callback = partial(delete_purchase, purchase["purchase_key"])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_purchase.add_widget(description)
                layout_for_purchase.add_widget(edit_button)
                layout_for_purchase.add_widget(copy_button)
                layout_for_purchase.add_widget(done_button)
                layout_for_purchase.add_widget(delete_button)
                shopping_list_layout.add_widget(layout_for_purchase)
            elif purchase['status'] == 'inactive':
                layout_for_purchase = FloatLayout()
                inactive += 1
                description = Label(markup=True, text=f"[s]{purchase['purchase_text']}[/s]", size_hint=(.8, .4),
                                    pos_hint={"top": .7, "left": .5})

                copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
                                          pos_hint={"top": .75, "right": 1})
                but_copy_callback = partial(copy_purchase, purchase["purchase_key"])
                copy_button.bind(on_release=but_copy_callback)

                delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                            pos_hint={"top": .25, "right": 1})
                but_delete_callback = partial(delete_purchase, purchase["purchase_key"])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_purchase.add_widget(description)
                layout_for_purchase.add_widget(copy_button)
                layout_for_purchase.add_widget(delete_button)
                shopping_list_layout.add_widget(layout_for_purchase)

    # Нет никаких заданий в списке
    else:
        l = Label(text='Your shopping list is empty', font_size='20sp')
        shopping_list_layout.add_widget(l)


def edit_purchase(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            # по ключу мы достаём запись
            edit_purchase_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for edit purchase')
            Purchase.operating_purchase = arg
            modal_edit_purchase_window(command='edit', purchase_request=edit_purchase_request, text='Edit purchase')


def copy_purchase(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            copy_purchase_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for copy purchase')
            modal_edit_purchase_window(command='copy', purchase_request=copy_purchase_request, text='Copy purchase')


def done_purchase(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            done_purchase_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for make purchase done')
            Purchase.operating_purchase = arg
            modal_edit_purchase_window(command='done', purchase_request=done_purchase_request, text='Purchase done?')


def delete_purchase(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            delete_purchase_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for delete purchase')
            Purchase.operating_purchase = arg
            modal_edit_purchase_window(command='delete', purchase_request=delete_purchase_request, text='Delete this purchase?')


def refill_shopping_list_layout():
    app = App.get_running_app()

    shopping_list_layout = app.root.ids['shopping_list_screen'].ids['shopping_layout']
    for w in shopping_list_layout.walk():
        # Удаляем только FloatLayout
        if w.__class__ == FloatLayout or w.__class__ == Label:
            shopping_list_layout.remove_widget(w)
    shopping_list_filling()


def modal_edit_purchase_window(command, purchase_request, text):
    app = App.get_running_app()
    purchase_data = json.loads(purchase_request.content.decode())

    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    t_i = TextInput(text=purchase_data['purchase_text'], size_hint=  (1, .3),
            pos_hint={'top': .85, 'right': 1})
    bl.add_widget(t_i)
    bl2 = BoxLayout(orientation='horizontal')
    but_no = Button(text='Back without saving', font_size=12, size_hint=(.3, .5))
    but_yes = Button(text=text, font_size=12, size_hint=(.3, .5))
    bl2.add_widget(but_no)
    bl2.add_widget(but_yes)
    bl.add_widget(bl2)
    popup = Popup(title=text, content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
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
            edit_purchase_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                % (constants.LOCAL_ID, Purchase.operating_purchase, constants.ID_TOKEN),
                data=json.dumps({'purchase_text': t_i.text}))
            log.info(edit_purchase_request)
        elif command == 'copy':
            log.info('Sends new purchase data to the server')
            new_purchase_request = requests.post(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list.json?auth=%s'
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'purchase_text': t_i.text, 'status': 'active'}))
            log.info(new_purchase_request)
        elif command == 'done':
            log.info('Patch data on server')
            done_purchase_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                % (constants.LOCAL_ID, Purchase.operating_purchase, constants.ID_TOKEN),
                data=json.dumps({'status': 'inactive'}))
            log.info(done_purchase_request)
        elif command == 'delete':
            log.info('Delete data on server')
            delete_purchase_request = requests.delete(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                % (constants.LOCAL_ID, Purchase.operating_purchase, constants.ID_TOKEN))
            log.info(delete_purchase_request)

        refill_shopping_list_layout()
        Purchase.operating_purchase = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()


def modal_delete_window(command, *args):
    if command == 'delete':
        text_label = 'Delete this shopping list?'
        text_popup = 'Delete this shopping list'
    elif command == "delete_with_added":
        text_label = 'Create new shopping list?'
        text_popup = 'Create new shopping list'
    else:
        text_label = ''
        text_popup = ''
    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text=text_label, font_size=12)
    bl.add_widget(l)
    bl2 = BoxLayout(orientation='horizontal')
    but_no = Button(text='No!', font_size=12, size_hint=(.3, .5))
    but_yes = Button(text='Yes!', font_size=12, size_hint=(.3, .5))
    bl2.add_widget(but_no)
    bl2.add_widget(but_yes)
    bl.add_widget(bl2)
    popup = Popup(title=text_popup, content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
                  auto_dismiss=False)

    def no(*args):
        popup.dismiss()

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        popup.dismiss()
        result = requests.get(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
        log.debug(f'Get shopping list data from the server {result}')
        data = json.loads(result.content.decode())
        if 'shop_list' in data:
            # словарь словарей
            purchases = data['shop_list']
            # ключи словаря - идентификаторы в базе
            purchase_keys = purchases.keys()
            # проходим по значениям через ключи словаря
            if command == 'delete':
                for purchase_key in purchase_keys:
                    log.info('Delete data on server')
                    delete_purchase_request = requests.delete(
                        'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                        % (constants.LOCAL_ID, purchase_key, constants.ID_TOKEN))
                    log.info(delete_purchase_request)
                Purchase.operating_purchase = ''
                refill_shopping_list_layout()
            elif command == 'delete_with_added':
                # Второе модальное окно, предлагающее сохранить активные покупки
                bl = BoxLayout(orientation='vertical')
                l = Label(text='Do you want to save unfinished purchases?', size_hint=(1, .3),
                                pos_hint={'top': .85, 'right': 1})
                bl.add_widget(l)
                bl2 = BoxLayout(orientation='horizontal')
                but_cancel = Button(text='Cancel creation \n of  new \n shopping list', font_size=12, size_hint=(.3, .5))
                but_no = Button(text="Don't save \n unfinished \npurchases", font_size=12, size_hint=(.3, .5))
                but_yes = Button(text='Save unfinished \n purchases', font_size=12, size_hint=(.3, .5))
                bl2.add_widget(but_cancel)
                bl2.add_widget(but_no)
                bl2.add_widget(but_yes)
                bl.add_widget(bl2)
                small_popup = Popup(title='Save unfinished purchases?', content=bl, size_hint=(0.4, 0.4), pos_hint={"x": 0.2, "top": 0.9},
                              auto_dismiss=False)

                def small_no(*args):
                    small_popup.dismiss()
                    for purchase_key in purchase_keys:
                        log.info('Delete data on server')
                        delete_purchase_request = requests.delete(
                            'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                            % (constants.LOCAL_ID, purchase_key, constants.ID_TOKEN))
                        log.info(delete_purchase_request)
                    Purchase.operating_purchase = ''
                    refill_shopping_list_layout()

                def small_cancel(*args):
                    small_popup.dismiss()

                # если хотим оставить незавершенные покупки
                def small_yes(*args):
                    small_popup.dismiss()
                    inactive_purchases = set()
                    for purchase_key in purchase_keys:
                        if purchases[purchase_key]['status'] == 'inactive':
                            inactive_purchases.add(purchase_key)
                    if inactive_purchases:
                        for purchase in inactive_purchases:
                            log.info('Delete data on server')
                            delete_purchase_request = requests.delete(
                                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'
                                % (constants.LOCAL_ID, purchase, constants.ID_TOKEN))
                            log.info(delete_purchase_request)
                        Purchase.operating_purchase = ''
                        refill_shopping_list_layout()

                but_cancel.bind(on_press=small_cancel)
                but_no.bind(on_press=small_no)
                but_yes.bind(on_press=small_yes)
                small_popup.open()

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()
