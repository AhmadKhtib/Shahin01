from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.label import Label

import arabic_reshaper
from bidi.algorithm import get_display
from ArTextInput import ArText

from models import session, Client, Transaction, Device

# Register Arabic font and clear background
LabelBase.register(name="ArabicFont", fn_regular="Amiri-Regular.ttf")
Window.clearcolor = (1, 1, 1, 1)

# Utility to reshape and format Arabic labels
def make_ar_label(text, color=(0, 0, 0, 1), bold=False, font_size=16):
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    lbl = Label(
        text=bidi_text,
        font_name="ArabicFont",
        color=color,
        font_size=font_size,
        size_hint_y=None,
        halign='right',
        valign='top',
        text_size=(Window.width - dp(40), None),
        bold=bold
    )
    lbl.bind(texture_size=lambda l, s: setattr(l, 'height', s[1]))
    return lbl


class SearchPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        # Arabic-correct hint text
        reshaped_hint = get_display(arabic_reshaper.reshape("ابحث عن الاسم"))

        self.search_box = ArText(
            hint_text=reshaped_hint,
            size_hint_y=None,
            height=50,
        )
        self.search_box.bind(text=self.on_search)

        self.results_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.results_layout)

        self.add_widget(self.search_box)
        self.add_widget(self.scroll)

    def on_search(self, instance, value):
        query = self.search_box.str.strip()
        self.results_layout.clear_widgets()

        if not query:
            return

        clients = session.query(Client).filter(Client.name.ilike(f'%{query}%')).all()

        for client in clients:
            self.results_layout.add_widget(make_ar_label(f"الاسم: {client.name}", bold=True))

            transactions = session.query(Transaction).filter(Transaction.client_id == client.id).all()
            if transactions:
                for t in transactions:
                    self.results_layout.add_widget(make_ar_label(f"عدد الأجهزة: {t.NumberOfDevices}"))
                    self.results_layout.add_widget(make_ar_label(f"المبلغ: {t.amount}"))
                    self.results_layout.add_widget(make_ar_label(f"رقم المعاملة: {t.id}"))
                    self.results_layout.add_widget(make_ar_label(f"تاريخ التسليم: {t.time}"))

                    if t.notes:
                        self.results_layout.add_widget(make_ar_label(f"ملاحظات: {t.notes}"))
                    else:
                        self.results_layout.add_widget(make_ar_label("ملاحظات: لا توجد ملاحظات"))

            devices = session.query(Device).filter(Device.client_id == client.id).all()
            if devices:
                self.results_layout.add_widget(make_ar_label("📱 الأجهزة:", bold=True))
                for device in devices:
                    self.results_layout.add_widget(make_ar_label(f"نوع الجهاز: {device.device_type}"))
                    self.results_layout.add_widget(make_ar_label(f"الماركة: {device.brand}"))
            else:
                self.results_layout.add_widget(make_ar_label(f"لا يوجد أجهزة لـ {client.name}", color=(1, 0, 0, 1)))


class SearchApp(App):
    def build(self):
        return SearchPage()


if __name__ == '__main__':
    SearchApp().run()
