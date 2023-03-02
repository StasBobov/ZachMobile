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


log = logging.getLogger('projects_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


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
            log.info('Sends new project data to the server')
            new_project_request = requests.post(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects.json?auth=%s'
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(project_data_for_load))
        # если эвент уже существует, то меняем
            log.info(new_project_request)

        else:
            log.info('Sends patch project data to the server')
            edit_project_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN),
                data=json.dumps(project_data_for_load))
            log.info(edit_project_request)
            Project.operating_project = ''
        clear_one_project_screen()
        app.change_screen("projects_screen")
        refill_projects_screen()


def fill_projects_screen():
    app = App.get_running_app()

    result = requests.get(
        'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
    data = json.loads(result.content.decode())
    log.debug(f'Get app projects data from the server {result}')

    # GreedLayout в projects_screen
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
                                          pos_hint={"top": .7, "right": 1})
                but_move_callback = partial(move_to_archive, project['project_key'])
                move_button.bind(on_release=but_move_callback)

                delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                            pos_hint={"top": .4, "right": 1})
                but_delete_callback = partial(delete_project, project['project_key'])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_project.add_widget(title)
                layout_for_project.add_widget(description)
                layout_for_project.add_widget(edit_button)
                layout_for_project.add_widget(move_button)
                layout_for_project.add_widget(delete_button)
                projects_layout.add_widget(layout_for_project)
            elif project['status'] == 'inactive':
                archive += 1
                title = Label(text=project['title'], size_hint=(.8, .3),
                              pos_hint={"top": 1, "left": .5})
                description = Label(text=project['description'], size_hint=(.8, .4),
                                    pos_hint={"top": .7, "left": .5})

                move_button = ImageButton(source="icons/done.jpg", size_hint=(.2, .2),
                                          pos_hint={"top": .7, "right": 1})
                but_move_callback = partial(move_from_archive, project['project_key'])
                move_button.bind(on_release=but_move_callback)

                delete_button = ImageButton(source="icons/delete.jpg", size_hint=(.2, .2),
                                            pos_hint={"top": .4, "right": 1})
                but_delete_callback = partial(delete_project, project['project_key'])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_project.add_widget(title)
                layout_for_project.add_widget(description)
                layout_for_project.add_widget(move_button)
                layout_for_project.add_widget(delete_button)
                archive_projects_layout.add_widget(layout_for_project)
    #
        # Если нет эвентов в списке
        if active == 0:
            l = Label(text='You have not projectss', font_size='20sp')
            projects_layout.add_widget(l)
        if archive == 0:
            l = Label(text='Your archive is empty', font_size='20sp')
            archive_projects_layout.add_widget(l)
    else:
        l = Label(text='You have not projects', font_size='20sp')
        projects_layout.add_widget(l)
        l = Label(text='Your archive is empty', font_size='20sp')
        archive_projects_layout.add_widget(l)


# перезаполняет layouts с проектами
def refill_projects_screen():
    app = App.get_running_app()

    projects_layout = app.root.ids['projects_screen'].ids['projects_layout']
    archive_projects_layout = app.root.ids['archive_projects_screen'].ids['archive_projects_layout']
    for w in projects_layout.walk():
        # Удаляем только FloatLayout
        if w.__class__ == FloatLayout or w.__class__ == Label:
            projects_layout.remove_widget(w)
    for w in archive_projects_layout.walk():
        if w.__class__ == FloatLayout or w.__class__ == Label:
            archive_projects_layout.remove_widget(w)
    fill_projects_screen()


def fill_one_project_screen(project_request):
    app = App.get_running_app()

    project_data = json.loads(project_request.content.decode())
    if project_data['status'] == 'archive':
        app.previous_screen = 'archive_projects_screen'
    else:
        app.previous_screen = 'projects_screen'
    app.root.ids["one_project_screen"].ids["info_label"].text = ''
    app.root.ids["one_project_screen"].ids["title"].text = project_data['title']
    app.root.ids["one_project_screen"].ids["description"].text = project_data['description']
    app.previous_screen = 'projects_screen'
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
        log.debug('Entering new data into the project')


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
            log.debug('Get data from server for edit project')

            Project.operating_project = arg
            fill_one_project_screen(edit_project_request)


def move_to_archive(*args):
    for arg in args:
         if arg.__class__ != ImageButton:
            edit_project_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for move project to archive')
            Project.operating_project = arg
            fill_one_project_screen(edit_project_request)
            modal_project_window(name='Remove!', label="Remove project to archive?", command='patch_to')


def move_from_archive(*args):
    for arg in args:
         if arg.__class__ != ImageButton:
            edit_project_request = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
            log.debug('Get data from server for move project from archive')
            Project.operating_project = arg
            fill_one_project_screen(edit_project_request)
            modal_project_window(name='Restore!', label="Restore project from archive?", command='patch_from')


def delete_project(*args):
        for arg in args:
            if arg.__class__ != ImageButton:
                get_project_request = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                log.debug('Get data from server for delete project')
                Project.operating_project = arg
                modal_project_window(name='Delete!', label='Delete this project!?', command='delete')
                fill_one_project_screen(get_project_request)


def modal_project_window(name, label, command):
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
        if command == 'patch_to':
            log.info('Patch data on server')
            move_project_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN), data=json.dumps({'status': 'inactive'}))
            log.info(move_project_request)
        elif command == 'patch_from':
            log.info('Patch data on server')
            move_project_request = requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN), data=json.dumps({'status': 'active'}))
            log.info(move_project_request)
        elif command == 'delete':
            log.info('Delete data on server')
            delete_project_request = requests.delete(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN))
            log.info(delete_project_request)
        refill_projects_screen()
        app.change_screen(app.previous_screen)
        clear_one_project_screen()
        Project.operating_project = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()



