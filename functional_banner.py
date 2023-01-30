from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image

class FunctionBanner(GridLayout):
    rows = 1

    def __int__(self, **kwargs):
        super(FunctionBanner, self).__init__(self, **kwargs)
        left = FloatLayout()
        left_image = None