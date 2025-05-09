from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.text import LabelBase
from kivy.core.window import Window
import arabic_reshaper
from bidi.algorithm import get_display
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle

from insertion import InsertionPage
from SearchBar import SearchPage
from Update_notes import UpdateNotesScreen
from daily_transactions import DailyTransactionsScreen

# Register Arabic-supporting font
LabelBase.register(name="ArabicFont", fn_regular="Amiri-Regular.ttf")
Window.clearcolor = (0, 0, 0, 0)  # Light grey background

# Utility function for reshaping Arabic tab titles
def ar(text):
    return get_display(arabic_reshaper.reshape(text))
def white_background_widget(widget):
    layout = BoxLayout()
    with layout.canvas.before:
        Color(1, 1, 1, 1)  # White
        layout.bg_rect = Rectangle(size=layout.size, pos=layout.pos)
    layout.bind(size=lambda inst, val: setattr(layout.bg_rect, 'size', val))
    layout.bind(pos=lambda inst, val: setattr(layout.bg_rect, 'pos', val))
    layout.add_widget(widget)
    return layout


class MainAppUI(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False

        tab1 = TabbedPanelItem(text=ar("الإدخال"), font_name="ArabicFont" ,background_color='black')
        tab1.add_widget(white_background_widget(InsertionPage()))
        self.add_widget(tab1)

        tab2 = TabbedPanelItem(text=ar("البحث"), font_name="ArabicFont" ,background_color='black')
        tab2.add_widget(white_background_widget(SearchPage()))
        self.add_widget(tab2)

        tab3 = TabbedPanelItem(text=ar("تحديث المعاملات"), font_name="ArabicFont" ,background_color='black')
        tab3.add_widget(white_background_widget(UpdateNotesScreen()))
        self.add_widget(tab3)

        tab4 = TabbedPanelItem(text=ar("المعاملات اليومية"), font_name="ArabicFont",background_color='black')
        tab4.add_widget(white_background_widget(DailyTransactionsScreen()))
        self.add_widget(tab4)


class MainKivyApp(App):
    def build(self):
        self.title = "تطبيق المعاملات"
        return MainAppUI()


if __name__ == '__main__':
    MainKivyApp().run()
