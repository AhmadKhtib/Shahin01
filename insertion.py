from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from ArTextInput import ArText
from kivy.uix.spinner import Spinner, SpinnerOption
from models import session
from Additon import more_data

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from functools import partial
import datetime

import arabic_reshaper
from bidi.algorithm import get_display

LabelBase.register(name='ArabicFont', fn_regular='Amiri-Regular.ttf')
Window.clearcolor = (1, 1, 1, 1)

device_type_options = ["جوال", "لابتوب", "ايباد", "بطارية", "باوربانك", "سماعة", "كشاف"]
brand_options = {
    "جوال": ["شاومي", "سامسونج", "ايفون", "نوكيا", "اوبو", "هواوي", "بوكو"],
    "لابتوب": ["MSI", "HP", "ASUS", "LENOVO", "APPLE MAC", "Acer"],
    "باوربانك": ["5k", "10k", "15k", "20k", "30k"],
    "سماعة": ["ايربود", "سماعة صب"],
    "ايباد": ["سامسونج", "شاومي", "هواوي", "ايفون"],
    "بطارية": ["200A", "125A", "100A", "75A", "55A", "40A", "26A", "20A", "16A", "18A", "9A"],
    "كشاف": ["صغير", "وسط", "كبير"]
}

# UI Arabic reshaping function
def ar(text):
    return get_display(arabic_reshaper.reshape(text))

# Reverse mapping for device type
reshaped_device_map = {ar(k): k for k in brand_options.keys()}

# Reverse mapping for brands
all_brands = {b for brands in brand_options.values() for b in brands}
reshaped_brand_map = {ar(b): b for b in all_brands}

# Spinner option with Arabic font
class ArabicSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        kwargs['font_name'] = 'ArabicFont'
        super().__init__(**kwargs)

# Label helper
def make_ar_label(text, font_size=16, bold=False):
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    lbl = Label(
        text=bidi_text,
        font_name="ArabicFont",
        font_size=font_size,
        size_hint_y=None,
        halign="center",
        valign="center",
        text_size=(Window.width - dp(10), None),
        bold=bold,
        color=(0, 0, 0, 1),
    )
    lbl.bind(texture_size=lambda l, s: setattr(l, 'height', s[1]))
    return lbl

class InsertionPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        self.device_inputs = []

        self.client_name = ArText(hint_text=ar("اسم الزبون"), size_hint_y=None, height=40)
        self.client_name.font_name = 'ArabicFont'
        self.client_name.halign = 'right'

        self.amount = TextInput(hint_text=ar("المبلغ"), input_filter="float",
                                font_name='ArabicFont', halign='right', size_hint_y=None, height=40)
        self.device_count_input = TextInput(hint_text=ar("عدد الأجهزة"), input_filter="int",
                                            font_name='ArabicFont', halign='right', size_hint_y=None, height=40)
        self.note = ArText(hint_text=ar("ملاحظة"))
        self.note.font_name = 'ArabicFont'
        self.note.halign = 'right'

        self.add_widget(make_ar_label("إدخال بيانات العميل", bold=True, font_size=18))
        self.add_widget(self.client_name)
        self.add_widget(self.amount)
        self.add_widget(self.device_count_input)
        self.add_widget(self.note)
        self.add_widget(make_ar_label("تفاصيل الأجهزة", bold=True, font_size=16))

        self.device_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.device_container.bind(minimum_height=self.device_container.setter('height'))
        self.scroll = ScrollView(size_hint=(1, None), size=(self.width, 250))
        self.scroll.add_widget(self.device_container)
        self.add_widget(self.scroll)

        self.generate_button = Button(text=ar("تحديث الأجهزة"), font_name='ArabicFont', size_hint_y=None, height=40)
        self.generate_button.bind(on_press=self.generate_devices)
        self.add_widget(self.generate_button)

        self.save_button = Button(text=ar("حفظ"), font_name='ArabicFont', size_hint_y=None, height=40)
        self.save_button.bind(on_press=self.save_data)
        self.add_widget(self.save_button)

        self.clear_button = Button(text=ar("مسح"), font_name='ArabicFont', size_hint_y=None, height=40)
        self.clear_button.bind(on_press=self.clear_fields)
        self.add_widget(self.clear_button)

    def generate_devices(self, instance):
        self.device_container.clear_widgets()
        self.device_inputs.clear()
        try:
            count = int(self.device_count_input.text)
            for i in range(count):
                type_spinner = Spinner(
                    text=ar("نوع الجهاز"),
                    values=[ar(opt) for opt in device_type_options],
                    font_name='ArabicFont',
                    option_cls=ArabicSpinnerOption,
                    size_hint_y=None,
                    height=35
                )
                brand_spinner = Spinner(
                    text=ar("الماركة"),
                    values=[],
                    font_name='ArabicFont',
                    option_cls=ArabicSpinnerOption,
                    size_hint_y=None,
                    height=35
                )
                type_spinner.bind(text=partial(self.on_type_select, brand_spinner))
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
                row.add_widget(brand_spinner)
                row.add_widget(type_spinner)
                self.device_container.add_widget(row)
                self.device_inputs.append((type_spinner, brand_spinner))
        except ValueError:
            self.device_container.add_widget(Label(
                text=ar("يرجى إدخال رقم صحيح"), font_name='ArabicFont', size_hint_y=None, height=30, color=(1, 0, 0, 1)
            ))

    def on_type_select(self, brand_spinner, spinner, selected_text):
        original_text = reshaped_device_map.get(selected_text, "")
        reshaped_brands = [ar(b) for b in brand_options.get(original_text, [])]
        brand_spinner.values = reshaped_brands
        brand_spinner.text = ar("الماركة")

    def save_data(self, instance):
        try:
            name = self.client_name.str.strip()
            amount = float(self.amount.text.strip())
            count = int(self.device_count_input.text.strip())
            note = self.note.str.strip()

            if not name or count <= 0:
                raise ValueError("اسم الزبون أو عدد الأجهزة غير صالح.")

            db = more_data(session)
            db.more_clients(name)

            for type_spinner, brand_spinner in self.device_inputs:
                device_type = reshaped_device_map.get(type_spinner.text, type_spinner.text)
                brand = reshaped_brand_map.get(brand_spinner.text, brand_spinner.text)
                db.more_devices(device_type, brand)

            db.more_transaction(
                NumberOfDevices=count,
                amount=amount,
                time=datetime.datetime.now(),
                notes=note
            )

            print("✅ تم الحفظ بنجاح.")
            self.clear_fields(None)

        except Exception as e:
            print(f"❌ خطأ أثناء الحفظ: {e}")

    def clear_fields(self, instance):
        self.client_name.text = ""
        self.amount.text = ""
        self.device_count_input.text = ""
        self.note.text = ""
        self.device_container.clear_widgets()
        self.device_inputs.clear()

class InsertionApp(App):
    def build(self):
        return InsertionPage()

if __name__ == "__main__":
    InsertionApp().run()
