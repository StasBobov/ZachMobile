import json
from own_classes import ImageButton

import requests
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput

import constants


class Project:
    operating_project = ''
    projects_ids = [0]

    # def __init__(self):
    #     print('hello')
    #     self.project_id = Project.projects_ids[-1] + 1
    #     print(self.project_id)

    def save_project(self):

        app = App.get_running_app()

        title = app.root.ids["one_project_screen"].ids["title"].text
        description = app.root.ids["one_project_screen"].ids["description"].text
        # Todo все поля
        # проверяем заполнение полей
        if title == '':
            app.root.ids["new_event_screen"].ids["info_label"].text = "Please fill in the title field"
        elif description == '':
            app.root.ids["new_event_screen"].ids["info_label"].text = "Please fill in the description field"
        else:
            # Отправляем данные в firebase
            project_data_for_load = {'title': title, 'description': description,
                                     'status': 'active'}
            if Project.operating_project == '':
                # requests.post присваивает запросу ключ
                new_project_request = requests.post(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects.json?auth=%s'
                    % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(project_data_for_load))
            # если эвент уже существует, то меняем
            else:
                edit_project_request = requests.patch(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                    % (constants.LOCAL_ID, self.operating_project, constants.ID_TOKEN),
                    data=json.dumps(project_data_for_load))
                self.operating_event = ''

            # self.clear_new_event_screen()
            app.change_screen("projects_screen")
            # self.refill_events_layouts(sort=self.date_sort)

    # добавляет новое поле в окно проекта
    def add_field(self):
        app = App.get_running_app()
        project_box_layout = app.root.ids['one_project_screen'].ids['one_project_layout']
        layout_for_note = FloatLayout()
        note = TextInput(hint_text='add new note', size_hint=(.8, .1),
                         pos_hint={"top": 1, "right": .9})
        # delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
        #                             pos_hint={"top": .5, "right": 1})
        # but_delete_callback = partial(self.delete_event, event['event_key'])
        # delete_button.bind(on_release=but_delete_callback)

        project_box_layout.add_widget(note)
