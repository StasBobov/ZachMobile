import json
from functools import partial
import logging

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from own_classes import ImageButton
import requests
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
import constants

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu


log = logging.getLogger('notes_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


class Note:
    operating_note = ''


class Item(OneLineAvatarIconListItem):
    left_icon = StringProperty()
    right_icon = StringProperty()
    right_text = StringProperty()


def dropdown_menu():
    app = App.get_running_app()
    menu_items = [{
        "text": "some_text",
        "right_text": "right_text",
        "right_icon": "icons/add_field.png",
        "left_icon": "icons/plus.png",
        "viewclass": "Item",
        "height": dp(54),
        "on_release": print('release')},
        {
            "text": "some_text",
            "right_text": "right_text",
            "right_icon": "icons/add_field.png",
            "left_icon": "icons/plus.png",
            "viewclass": "Item",
            "height": dp(54),
            "on_release": print('release'),
    }]
    menu = MDDropdownMenu(
        caller = app.root.ids["one_note_screen"].ids["transfer"],
        items = menu_items,
        position = 'auto',
        width_mult = 4,
    )
    menu.open()


def save_note():
    app = App.get_running_app()

    description = app.root.ids["one_note_screen"].ids["description"].text
    note_data_for_load = {'description': description}
    if description == '':
        app.root.ids["one_note_screen"].ids["info_label"].text = "Please fill in the description field"
    else:
        if Note.operating_note == '':
            # requests.post присваивает запросу ключ
            log.info('Sends new note data to the server')
            new_note_request = requests.post(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes.json?auth=%s'
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(note_data_for_load))
            log.info(new_note_request)
        else:
            log.info('Sends patch note data to the server')
            edit_note_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes/%s.json?auth=%s'
                % (constants.LOCAL_ID, Note.operating_note, constants.ID_TOKEN),
                data=json.dumps(note_data_for_load))
            log.info(edit_note_request)
            Note.operating_note = ''
        clear_one_note_screen()
        app.change_screen("notes_screen")
        refill_notes_screen()


def fill_notes_screen():
    app = App.get_running_app()

    result = requests.get(
        'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
    data = json.loads(result.content.decode())
    log.debug(f'Get app projects data from the server {result}')

    # GreedLayout в projects_screen
    notes_layout = app.root.ids['notes_screen'].ids['notes_layout']

    if 'notes' in data:
        notes = data['notes']
        # ключи событий
        notes_keys = notes.keys()
        notes_list = []
        # добавляем в словарь второго порядка поле с ключами
        for note_key in notes_keys:
            notes[note_key]['note_key'] = str(note_key)
            notes_list.append(notes[note_key])
            # Заполнение
        for note in notes_list:
            layout_for_note = FloatLayout()
            description = Label(text=note['description'], size_hint=(.8, .4),
                                pos_hint={"top": .7, "left": .5})

            edit_button = ImageButton(source="icons/edit.png", size_hint=(.2, .2),
                                      pos_hint={"top": 1, "right": 1})
            but_edit_callback = partial(edit_note, note['note_key'])
            edit_button.bind(on_release=but_edit_callback)
            #
            # move_button = ImageButton(source="icons/done.jpg", size_hint=(.2, .2),
            #                           pos_hint={"top": .7, "right": 1})
            # but_move_callback = partial(move_to_archive, project['project_key'])
            # move_button.bind(on_release=but_move_callback)

            delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                        pos_hint={"top": .4, "right": 1})
            but_delete_callback = partial(delete_note, note['note_key'])
            delete_button.bind(on_release=but_delete_callback)

            layout_for_note.add_widget(description)
            layout_for_note.add_widget(edit_button)
    #         layout_for_project.add_widget(move_button)
            layout_for_note.add_widget(delete_button)
            notes_layout.add_widget(layout_for_note)
    else:
        l = Label(text='You have not notes', font_size='20sp')
        notes_layout.add_widget(l)


def refill_notes_screen():
    app = App.get_running_app()

    notes_layout = app.root.ids['notes_screen'].ids['notes_layout']
    for w in notes_layout.walk():
        # Удаляем только FloatLayout
        if w.__class__ == FloatLayout or w.__class__ == Label:
            notes_layout.remove_widget(w)
    fill_notes_screen()


def fill_one_note_screen(note_request):
    app = App.get_running_app()

    note_data = json.loads(note_request.content.decode())
    app.previous_screen = 'notes_screen'
    app.root.ids["one_note_screen"].ids["info_label"].text = ''
    app.root.ids["one_note_screen"].ids["description"].text = note_data['description']
    app.change_screen('one_note_screen')


def clear_one_note_screen():
    app = App.get_running_app()

    app.root.ids["one_note_screen"].ids["description"].text = ''
    app.root.ids["one_project_screen"].ids["info_label"].text = ''


def edit_note(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            edit_note_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for edit note')
            Note.operating_note = arg
            fill_one_note_screen(edit_note_request)


def delete_note(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            get_note_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for delete project')
            Note.operating_note = arg
            modal_note_window(name='Delete!', label='Delete this note!?', command='delete')
            fill_one_note_screen(get_note_request)


def modal_note_window(name, label, command):
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
        clear_one_note_screen()
        app.change_screen(app.previous_screen)
        Note.operating_note = ''

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        popup.dismiss()
        # if command == 'patch_to':
        #     log.info('Patch data on server')
        #     move_project_request = requests.patch(
        #         'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes/%s.json?auth=%s'
        #         % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN), data=json.dumps({'status': 'inactive'}))
        #     log.info(move_project_request)
        # elif command == 'patch_from':
        #     log.info('Patch data on server')
        #     move_project_request = requests.patch(
        #         'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes/%s.json?auth=%s'
        #         % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN), data=json.dumps({'status': 'active'}))
        #     log.info(move_project_request)
        if command == 'delete':
            log.info('Delete data on server')
            delete_note_request = requests.delete(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes/%s.json?auth=%s'
                % (constants.LOCAL_ID, Note.operating_note, constants.ID_TOKEN))
            log.info(delete_note_request)
        refill_notes_screen()
        clear_one_note_screen()
        app.change_screen(app.previous_screen)
        Note.operating_note = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()
