from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image

class MyBox(BoxLayout):
    orientation = 'vertical'

    def __int__(self, **kwargs):
        super(MyBox, self).__int__(**kwargs)
        image = Image(source="icons/events.jpg")
        self.add_widget(image)


class EventsBanner(GridLayout):
    rows = 1

    def __int__(self, **kwargs):
        super(EventsBanner, self).__int__(**kwargs)

        image = Image(source="icons/calendar.jpg")
        self.add_widget(image)

        # left = FloatLayout()
        # left_image = Image(source="icons/" + kwargs['event_image'], size_hint=(1, 0.8), pos_hint={"top": 1, "left": 1})
        # left_label = Label(text=kwargs['description'], size_hint=(1, .2), pos_hint={"top": .2, "left": 1})
        # left.add_widget(left_image)
        # left.add_widget(left_label)
        #
        # self.add_widget(left)