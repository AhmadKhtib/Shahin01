from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.core.window import Window
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from models import Transaction, Client, session

LabelBase.register(name="ArabicFont", fn_regular="Amiri-Regular.ttf")
Window.clearcolor = (0.9, 0.9, 0.9, 1)  # Light grey

def ar(text):
    return get_display(arabic_reshaper.reshape(text))

class DailyTransactionsScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=15, padding=15, **kwargs)

        # --- Date selection spinners ---
        self.day_input = Spinner(
            text=ar("اليوم"),
            values=[str(i) for i in range(1, 32)],
            size_hint_y=None,
            height=45,
            font_name="ArabicFont",
            color=(0, 0, 0, 1)
        )
        self.month_input = Spinner(
            text=ar("الشهر"),
            values=[str(i) for i in range(1, 13)],
            size_hint_y=None,
            height=45,
            font_name="ArabicFont",
            color=(0, 0, 0, 1)
        )
        self.year_input = Spinner(
            text=ar("السنة"),
            values=[str(i) for i in range(2025, 2030)],
            size_hint_y=None,
            height=45,
            font_name="ArabicFont",
            color=(0, 0, 0, 1)
        )

        self.add_widget(Label(
            text=ar("🔍 البحث عن المعاملات اليومية"),
            font_size=18,
            font_name="ArabicFont",
            size_hint_y=None,
            height=35,
            color=(0, 0, 0, 1)
        ))
        self.add_widget(self._row([self.day_input, self.month_input, self.year_input]))

        # --- Search button ---
        self.search_button = Button(
            text=ar("بحث"),
            font_name="ArabicFont",
            size_hint_y=None,
            height=45,
            color=(0, 0, 0, 1),
            on_press=self.search_transactions
        )
        self.add_widget(self.search_button)

        # --- Result label ---
        self.result_label = Label(
            text="",
            font_name="ArabicFont",
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(200),
            font_size=14,
            halign='right',
            valign='top',
            text_size=(Window.width - dp(40), None)
        )
        self.result_label.bind(texture_size=lambda lbl, size: setattr(lbl, 'height', size[1]))

        self.result_scroll = ScrollView(size_hint=(1, 1))
        self.result_scroll.add_widget(self.result_label)
        self.add_widget(self.result_scroll)

    def _row(self, widgets):
        row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)
        for w in widgets:
            row.add_widget(w)
        return row

    def search_transactions(self, instance):
        try:
            today = datetime.today()

            # If user didn’t select a date, use today’s values
            try:
                day = int(self.day_input.text) if self.day_input.text != ar("اليوم") else today.day
                month = int(self.month_input.text) if self.month_input.text != ar("الشهر") else today.month
                year = int(self.year_input.text) if self.year_input.text != ar("السنة") else today.year
            except ValueError:
                raise ValueError(ar("تأكد من صحة التاريخ المدخل"))

            if not (1 <= day <= 31 and 1 <= month <= 12 and year > 0):
                raise ValueError(ar("تاريخ غير صالح"))

            search_date = f"{year:04d}-{month:02d}-{day:02d}"

            results = session.query(
                func.date(Transaction.time).label('day'),
                func.sum(Transaction.amount).label('total_amount'),
                func.group_concat(Client.name, ', ').label('clients')
            ).join(Client, Transaction.client_id == Client.id)\
             .filter(func.date(Transaction.time) == search_date)\
             .group_by('day').all()

            if results:
                output = ""
                for day, total, clients in results:
                    output += ar(f"التاريخ: {day}") + "\n"
                    output += ar(f" إجمالي المبلغ: {total}") + "\n"
                    output += ar(f" العملاء: {clients}") + "\n\n"
                self.result_label.text = output
                self.result_label.halign = 'center'  # Center-align the content
                self.result_label.font_size = 20
            else:
                self.result_label.text = ar("لا توجد معاملات في هذا التاريخ.")
                self.result_label.halign = 'center'


        except ValueError as ve:
            self.result_label.text = ar(f"خطأ في الإدخال: {ve}")
        except SQLAlchemyError as db_error:
            self.result_label.text = ar(f"خطأ في قاعدة البيانات: {db_error}")
        except Exception as ex:
            self.result_label.text = ar(f"خطأ غير متوقع: {ex}")


class DailyTransactionsApp(App):
    def build(self):
        return DailyTransactionsScreen()


if __name__ == '__main__':
    DailyTransactionsApp().run()
