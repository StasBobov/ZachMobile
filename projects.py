import json
from functools import partial

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from own_classes import ImageButton
import requests
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput

import constants


class Project:
    operating_project = ''


def save_project():
    app = App.get_running_app()

    title = app.root.ids["one_project_screen"].ids["title"].text
    description = app.root.ids["one_project_screen"].ids["description"].text
    project_data_for_load = {'title': title, 'description': description,
                             'status': 'active'}
    if title == '':
        app.root.ids["one_project_screen"].ids["info_label"].text = "Please fill in the title field"
    else:
        if Project.operating_project == '':
            # requests.post присваивает запросу ключ
            new_project_request = requests.post(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects.json?auth=%s'
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(project_data_for_load))
        # если эвент уже существует, то меняем

        else:
            edit_project_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN),
                data=json.dumps(project_data_for_load))
            Project.operating_project = ''
        clear_one_project_screen()
        app.change_screen("projects_screen")
        refill_projects_screen()


def fill_one_project_screen(event_request):
    app = App.get_running_app()

    event_data = json.loads(event_request.content.decode())
    if event_data['status'] == 'archive':
        app.previous_screen = 'archive_projects_screen'
    else:
        app.previous_screen = 'projects_screen'
    app.root.ids["one_project_screen"].ids["info_label"].text = ''
    app.root.ids["one_project_screen"].ids["title"].text = event_data['title']
    app.root.ids["one_project_screen"].ids["description"].text = event_data['description']
    app.change_screen('one_project_screen')


def supplement_save():
    app = App.get_running_app()
    addition = app.root.ids["supplement_screen"].ids["addition"].text

    # проверяем заполнение поля
    if addition == '':
        app.root.ids["supplement_screen"].ids["info_label"].text = "You have not completed the addendum"
    else:
        app.root.ids["one_project_screen"].ids["description"].text = \
            f'{app.root.ids["one_project_screen"].ids["description"].text}\n- ' \
            f'{app.root.ids["supplement_screen"].ids["addition"].text}'
        app.change_screen("one_project_screen")

    # project_box_layout = app.root.ids['one_project_screen'].ids['one_project_layout']
    # layout_for_note = FloatLayout()
    # note = TextInput(hint_text='add new note', size_hint=(.9, 1),
    #                  pos_hint={"top": 1, "left": 1})
    # delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.1, .3),
    #                             pos_hint={"top": .5, "right": 1})
    # # but_delete_callback = partial(self.delete_event, event['event_key'])
    # # delete_button.bind(on_release=print(app.root.ids['one_project_screen'].ids[str(field_id) + 'f']))
    #
    # layout_for_note.add_widget(note)
    # layout_for_note.add_widget(delete_button)
    # project_box_layout.add_widget(layout_for_note)


def clear_supplement_screen():
    app = App.get_running_app()

    app.root.ids["supplement_screen"].ids["addition"].text = ''
    app.root.ids["supplement_screen"].ids["info_label"].text = ''


def clear_one_project_screen():
    app = App.get_running_app()

    app.root.ids["one_project_screen"].ids["title"].text = ''
    app.root.ids["one_project_screen"].ids["description"].text = ''
    app.root.ids["one_project_screen"].ids["info_label"].text = ''


def edit_project(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            edit_project_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            Project.operating_project = arg
            fill_one_project_screen(edit_project_request)


def modal_project_window(self, name, label, command):
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
        clear_one_project_screen()
        Project.operating_project = ''

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        popup.dismiss()
        if command == 'patch':
            move_project_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'
                % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN), data=json.dumps({'status': 'inactive'}))
        elif command == 'delete':
            delete_project_request = requests.delete(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'
                % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN))
        refill_projects_screen()
        app.change_screen(app.previous_screen)
        clear_one_project_screen()
        Project.operating_project = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()


def fill_projects_screen():
    app = App.get_running_app()

    result = requests.get(
        'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
    data = json.loads(result.content.decode())

    # GreenLayout в events_screen
    projects_layout = app.root.ids['projects_screen'].ids['projects_layout']
    archive_projects_layout = app.root.ids['archive_projects_screen'].ids['archive_projects_layout']

    if 'projects' in data:
        projects = data['projects']
        # ключи событий
        projects_keys = projects.keys()
        projects_list = []
        # добавляем в словарь второго порядка поле с ключами
        for project_key in projects_keys:
            projects[project_key]['project_key'] = str(project_key)
            projects_list.append(projects[project_key])
            # self.events_list = events_list
            # Заполнение
            active = 0
            archive = 0
        for project in projects_list:
            layout_for_project = FloatLayout()
            # добавляем в активные или не активные проекты
            if project['status'] == 'active':
                active += 1
                title = Label(text=project['title'], size_hint=(.8, .3),
                              pos_hint={"top": 1, "left": .5})
                description = Label(text=project['description'], size_hint=(.8, .4),
                                    pos_hint={"top": .7, "left": .5})
                edit_button = ImageButton(source="icons/edit.png", size_hint=(.2, .2),
                                          pos_hint={"top": 1, "right": 1})
                but_edit_callback = partial(edit_project, project['project_key'])
                edit_button.bind(on_release=but_edit_callback)

                move_button = ImageButton(source="icons/done.jpg", size_hint=(.2, .2),
                                          pos_hint={"top": .5, "right": 1})
                but_move_callback = partial(move_to_archive, project['project_key'])
                move_button.bind(on_release=but_move_callback)
                #
                # delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                #                             pos_hint={"top": .25, "right": 1})
                # but_delete_callback = partial(self.delete_event, event['event_key'])
                # delete_button.bind(on_release=but_delete_callback)
                layout_for_project.add_widget(title)
                layout_for_project.add_widget(description)
                layout_for_project.add_widget(edit_button)
                layout_for_project.add_widget(move_button)
                # layout_for_event.add_widget(delete_button)
                projects_layout.add_widget(layout_for_project)
    #             elif event['status'] == 'inactive':
    #                 inactive += 1
    #                 title = Label(text=event['title'], size_hint=(.8, .3),
    #                               pos_hint={"top": 1, "left": .5})
    #                 description = Label(text=event['description'], size_hint=(.8, .4),
    #                                     pos_hint={"top": .7, "left": .5})
    #                 date = Label(text=event['date'], size_hint=(.4, .3),
    #                              pos_hint={"top": .3, "left": .5})
    #                 time = Label(text=event['time'], size_hint=(.4, .3),
    #                              pos_hint={"top": .3, "right": .8})
    #
    #                 copy_button = ImageButton(source="icons/copy.jpg", size_hint=(.2, .2),
    #                                           pos_hint={"top": .9, "right": 1})
    #                 but_copy_callback = partial(self.copy_event, event['event_key'])
    #                 copy_button.bind(on_release=but_copy_callback)
    #
    #                 delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
    #                                             pos_hint={"top": .3, "right": 1})
    #                 but_delete_callback = partial(self.delete_event, event['event_key'])
    #                 delete_button.bind(on_release=but_delete_callback)
    #                 layout_for_event.add_widget(title)
    #                 layout_for_event.add_widget(description)
    #                 layout_for_event.add_widget(date)
    #                 layout_for_event.add_widget(time)
    #                 layout_for_event.add_widget(copy_button)
    #                 layout_for_event.add_widget(delete_button)
    #                 inactive_events_box_layout.add_widget(layout_for_event)
    #
    #     # Если нет эвентов в списке
    #     if active == 0:
    #         l = Label(text='You have no scheduled events', font_size='20sp')
    #         events_box_layout.add_widget(l)
    #     if inactive == 0:
    #         l = Label(text='You have no completed events', font_size='20sp')
    #         inactive_events_box_layout.add_widget(l)
    # else:
    #     l = Label(text='You have no scheduled events', font_size='20sp')
    #     events_box_layout.add_widget(l)
    #     l = Label(text='You have no completed events', font_size='20sp')
    #     inactive_events_box_layout.add_widget(l)
    # # заполняем календарь
    # start_calendar_fill(self)


def move_to_archive(self, *args):
    print(args)
    for arg in args:
        print(arg)
        if arg.__class__ != ImageButton:
            print('I am here')
            edit_project_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            Project.operating_event = arg
            print('I am here')
            fill_one_project_screen(edit_project_request)
            modal_project_window(name='Remove!', label="Remove project to archive?", command='patch')


# перезаполняет layouts с эвентами
def refill_projects_screen():
    app = App.get_running_app()

    projects_layout = app.root.ids['projects_screen'].ids['projects_layout']
    archive_projects_layout = app.root.ids['archive_projects_screen'].ids['archive_projects_layout']
    for w in projects_layout.walk():
        print(w.__class__)
        # Удаляем только FloatLayout
        if w.__class__ == FloatLayout or w.__class__ == Label:
            projects_layout.remove_widget(w)
    for w in archive_projects_layout.walk():
        if w.__class__ == FloatLayout or w.__class__ == Label:
            archive_projects_layout.remove_widget(w)
    fill_projects_screen()

