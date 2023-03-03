import json
from functools import partial
import logging

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from own_classes import ImageButton, LabelButton
import requests
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
import constants
import tasks
import shopping_list

from kivy.metrics import dp
from kivy.properties import StringProperty

from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu

log = logging.getLogger('notes_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


class Note:
    operating_note = ''


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


def dropdown_menu(text):
    app = App.get_running_app()
    if text:
        menu_items = [{
            "text": "Create new event",
            "icon": "icons/plus.png",
            "viewclass": "IconListItem",
            "height": dp(54),
            "on_release": lambda x='event': transfer_to_event(menu, text)},
            {
                "text": "Create new To-Do task",
                "icon": "icons/plus.png",
                "viewclass": "IconListItem",
                "height": dp(54),
                "on_release": lambda x='todo': transfer_to_todo_list(menu, text)},
            {
                "text": "Add to shoplist",
                "icon": "icons/plus.png",
                "viewclass": "IconListItem",
                "height": dp(54),
                "on_release": lambda x='purchase': transfer_to_shopping_list(menu, text)},
            {
                "text": "Add to project",
                "icon": "icons/plus.png",
                "viewclass": "IconListItem",
                "height": dp(54),
                "on_release": lambda x='project': transfer_to_project(menu, text)},
        ]
        menu = MDDropdownMenu(
            caller=app.root.ids["one_note_screen"].ids["transfer"],
            items=menu_items,
            position='auto',
            width_mult=4,
        )
        menu.open()
    else:
        app.root.ids["one_note_screen"].ids["info_label"].text = 'Your Note is empty'


def transfer_to_project(menu, text):
    app = App.get_running_app()
    result = requests.get(
        'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
    data = json.loads(result.content.decode())
    log.debug(f'Get app projects data from the server {result}')

    # перекидываем заметку в проект
    def one_click_add(key, description_text, adding_text, *args):
        if key is None:
            app.root.ids["one_project_screen"].ids["description"].text = adding_text
            app.root.ids["one_project_screen"].ids["info_label"].text = ''
            app.change_screen('one_project_screen')
        else:
            new_description_text = f'{description_text} \n {adding_text}'
            log.info('Patch data on server')
            transfer_project_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, key, constants.ID_TOKEN),
                data=json.dumps({'description': new_description_text}))
            log.info(transfer_project_request)
            app.change_screen(app.previous_screen)
        popup.dismiss()

    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text="Chose the project", font_size=12)
    bl.add_widget(l)
    sw = ScrollView(pos_hint={"top": 1, "right": 1}, size_hint=(1, 1))
    gl = GridLayout(cols=1, spacing=10, size_hint_y=None, row_fource_default=True)
    but_callback = partial(one_click_add, None, '', text)
    lb = LabelButton(text='New project', on_release=but_callback)
    gl.add_widget(lb)
    # заполняем проекты
    if 'projects' in data:
        projects = data['projects']
        for project in projects:
            if projects[project]['status'] == 'active':
                but_callback = partial(one_click_add, project, projects[project]['description'], text)
                lb = LabelButton(text=projects[project]['title'], on_release=but_callback)
                gl.add_widget(lb)
    sw.add_widget(gl)

    bl2 = BoxLayout(orientation='horizontal')
    but_cancel = Button(text='No!', font_size=12, size_hint=(.3, .5))
    bl2.add_widget(but_cancel)
    bl.add_widget(sw)
    bl.add_widget(bl2)
    popup = Popup(title="Transfer_to_project", content=bl, size_hint=(0.4, 0.6), pos_hint={"x": 0.2, "top": 0.9},
                  auto_dismiss=False)

    # усли не будешь менять статус
    def cancel(*args):
        popup.dismiss()

    but_cancel.bind(on_press=cancel)
    popup.open()
    menu.dismiss()


def transfer_to_event(menu, text):
    app = App.get_running_app()
    app.root.ids["new_event_screen"].ids["description"].text = text
    app.change_screen('new_event_screen')
    menu.dismiss()


def transfer_to_todo_list(menu, text):
    app = App.get_running_app()
    tasks.save_new_task(text)
    app.change_screen('notes_screen')
    menu.dismiss()


def transfer_to_shopping_list(menu, text):
    shopping_list.Purchase.operating_purchase = ''
    shopping_list.save_new_purchase(text)
    menu.dismiss()


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
    log.debug('Get app projects data from the server')
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
    app.root.ids["one_note_screen"].ids["info_label"].text = ''


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
