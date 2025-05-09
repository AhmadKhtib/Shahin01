from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp

from models import session, Transaction, Client, Device
import arabic_reshaper
from bidi.algorithm import get_display
from ArTextInput import ArText

LabelBase.register(name="ArabicFont", fn_regular="Amiri-Regular.ttf")
Window.clearcolor = (0.9, 0.9, 0.9, 1)  # Light grey


def ar(text):
    return get_display(arabic_reshaper.reshape(text))

class UpdateNotesScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        self.note_id_input = TextInput(
            hint_text=ar("رقم المعاملة"), size_hint_y=None, height=45, multiline=False, font_name="ArabicFont",halign='center'

        )
        self.fetch_button = Button(text=ar("إحضار"), size_hint_y=None, height=45, font_name="ArabicFont", on_press=self.fetch_transaction)

        self.client_name_label = Label(text="", font_name="ArabicFont", size_hint_y=None, height=30)
        self.device_count_label = Label(text="", font_name="ArabicFont", size_hint_y=None, height=30)
        self.devices_label = Label(text="", font_name="ArabicFont", size_hint_y=None, height=30)
        self.current_note_label = Label(text="", font_name="ArabicFont", size_hint_y=None, height=30)
        self.current_amount_label = Label(text="", font_name="ArabicFont", size_hint_y=None, height=30)

        self.new_note_input = ArText(hint_text=ar("ملاحظة جديدة"),
                             size_hint_y=None, height=45, multiline=False,
                             opacity=0, disabled=True, halign='right')
        self.new_note_input.font_name="ArabicFont"
        self.new_note_input.halign='center'
        
        self.new_amount_input = TextInput(hint_text=ar("المبلغ الجديد"), font_name="ArabicFont", size_hint_y=None, height=45, multiline=False, opacity=0, disabled=True ,halign='center')
        self.save_button = Button(text=ar("حفظ التغييرات"), font_name="ArabicFont", size_hint_y=None, height=45, on_press=self.save_changes, opacity=0, disabled=True)

        self.clear_button = Button(text=ar("مسح"), font_name="ArabicFont", size_hint_y=None, height=45, on_press=self.clear_all_fields ,opacity=0, disabled=True)
        self.result_label = Label(text="", font_name="ArabicFont", size_hint_y=0,height=0 )

        self.show_all_button = Button(text=ar("عرض جميع العملاء مع ملاحظات"), font_name="ArabicFont", size_hint_y=None, height=45, on_press=self.show_all_clients_with_notes)
        self.clients_list = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.clients_list.bind(minimum_height=self.clients_list.setter('height'))
        self.scroll_view = ScrollView(size_hint=(1, 1), size=(self.width, 300))
        self.scroll_view.add_widget(self.clients_list)

        for widget in [
            self.note_id_input, self.fetch_button, self.client_name_label, self.device_count_label,
            self.devices_label, self.current_note_label, self.current_amount_label,
            self.new_note_input, self.new_amount_input, self.save_button,
            self.clear_button, self.result_label, self.show_all_button, self.scroll_view
        ]:
            self.add_widget(widget)

        self.transaction_to_update = None

    def fetch_transaction(self, instance):
        self.clear_fields_only()
        try:
            transaction_id = int(self.note_id_input.text.strip())
            self.transaction_to_update = session.query(Transaction).filter(Transaction.id == transaction_id).first()

            if not self.transaction_to_update:
                self.result_label.text = ar("لم يتم العثور على المعاملة.")
                return

            client = session.query(Client).filter(Client.id == self.transaction_to_update.client_id).first()
            if client:
                self.client_name_label.text = ar(f"اسم العميل: {client.name}")
                self.client_name_label.color = (0, 0, 0, 1)
                self.device_count_label.text = ar(f"عدد الأجهزة: {self.transaction_to_update.NumberOfDevices}")
                self.device_count_label.color = (0, 0, 0, 1)

                devices = session.query(Device).filter(Device.client_id == client.id).all()
                device_names = [d.device_type for d in devices]
                self.devices_label.text = ar(f"الأجهزة: {', '.join(device_names)}") if device_names else ar("لا توجد أجهزة")
                self.devices_label.color = (0, 0, 0, 1)
            else:
                self.client_name_label.text = ar("لم يتم العثور على العميل.")
                self.client_name_label.color = (0, 0, 0, 1)

            self.current_note_label.text = ar(f"الملاحظة الحالية: {self.transaction_to_update.notes or 'لا توجد'}")
            self.current_note_label.color = (0, 0, 0, 1)
            self.current_amount_label.text = ar(f"المبلغ الحالي: {self.transaction_to_update.amount}")
            self.current_amount_label.color = (0, 0, 0, 1)

            self.new_note_input.opacity = 1
            self.new_note_input.disabled = False
            self.new_amount_input.opacity = 1
            self.new_amount_input.disabled = False
            self.save_button.opacity = 1
            self.save_button.disabled = False
            self.clear_button.opacity=1
            self.clear_button.disabled=False

            self.result_label.text = ""

        except ValueError:
            self.result_label.text = ar("يرجى إدخال رقم صحيح.")

    def save_changes(self, instance):
        if not self.transaction_to_update:
            self.result_label.text = ar("لا توجد معاملة لتحريرها.")
            return

        try:
            new_note = self.new_note_input.str.strip()
            new_amount = float(self.new_amount_input.text.strip())


            self.transaction_to_update.notes = new_note
            self.transaction_to_update.amount = new_amount
            session.commit()

            self.result_label.text = ar("✅ تم التحديث بنجاح.")
            self.clear_all_fields(None)
        except Exception as e:
            self.result_label.text = ar(f"❌ خطأ: {e}")

    def show_all_clients_with_notes(self, _):
        self.clients_list.clear_widgets()

        transactions = session.query(Transaction).filter(
            Transaction.notes.isnot(None),
            Transaction.notes != ""
        ).all()

        if not transactions:
            self.clients_list.add_widget(Label(
                text=ar("لا يوجد عملاء بملاحظات."),
                font_name="ArabicFont",
                color=(0, 0, 0, 1),
                size_hint_y=400,
                height=400,
                halign='center',
                valign='middle',
                text_size=(Window.width - dp(40), None)
            ))
            return

        for t in transactions:
            client = session.query(Client).filter(Client.id == t.client_id).first()
            if client:
                # Outer container for client block
                section = BoxLayout(orientation='vertical', padding=10, spacing=6, size_hint_y=None)
                section.bind(minimum_height=section.setter('height'))

                # Text rows
                lines = [
                    f"رقم المعاملة: {t.id}",
                    f"اسم العميل: {client.name}",
                    f"المبلغ: {t.amount}",
                    f"الملاحظة: {t.notes}"
                ]

                for line in lines:
                    label = Label(
                        text=ar(line),
                        font_name="ArabicFont",
                        color=(0, 0, 0, 1),
                        size_hint_y=None,
                        halign='center',
                        valign='middle',
                        font_size=16,
                        text_size=(Window.width - dp(40), None)
                    )
                    label.bind(texture_size=lambda l, s: setattr(l, 'height', s[1]))
                    section.add_widget(label)

                # Divider
                divider = Label(
                    text=ar("ـــــــــــــــــــــــــــــــــــــــــــــ"),
                    font_name="ArabicFont",
                    color=(0.3, 0.3, 0.3, 1),
                    font_size=14,
                    size_hint_y=None,
                    height=2,
                    halign='center',
                    valign='middle'
                )
                section.add_widget(divider)

                self.clients_list.add_widget(section)



    def clear_fields_only(self):
        self.client_name_label.text = ""
        self.device_count_label.text = ""
        self.devices_label.text = ""
        self.current_note_label.text = ""
        self.current_amount_label.text = ""
        self.result_label.text = ""

    def clear_all_fields(self, instance):
        self.clear_fields_only()
        self.note_id_input.text = ""
        self.new_note_input.text = ""
        self.new_amount_input.text = ""
        self.transaction_to_update = None
        self.clients_list.clear_widgets()

        self.new_note_input.opacity = 0
        self.new_note_input.disabled = True
        self.new_amount_input.opacity = 0
        self.new_amount_input.disabled = True
        self.save_button.opacity = 0
        self.save_button.disabled = True
        self.clear_button.opacity=0
        self.clear_button.disabled=True



class UpdateNotesApp(App):
    def build(self):
        return UpdateNotesScreen()


if __name__ == '__main__':
    UpdateNotesApp().run()
