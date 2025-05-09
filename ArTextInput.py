from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, StringProperty
import arabic_reshaper
from bidi.algorithm import get_display


class ArText(TextInput):
    max_chars = NumericProperty(200)
    str = StringProperty("")

    def __init__(self, **kwargs):
        super(ArText, self).__init__(**kwargs)
        self.font_name = "Cairo-Regular.ttf"
        self.font_size = 16
        self.halign = "right"
        self.cursor_color = [0, 0, 0, 1]
        self.text = get_display(arabic_reshaper.reshape(""))
        self.str = ""

    def insert_text(self, substring, from_undo=False):
        if not from_undo and (len(self.str) + len(substring) > self.max_chars):
            return

        self.str += substring
        self.text = get_display(arabic_reshaper.reshape(self.str))
        super(ArText, self).insert_text("", from_undo)

    def do_backspace(self, from_undo=False, mode='bkspc'):
        self.str = self.str[:-1]
        self.text = get_display(arabic_reshaper.reshape(self.str))
