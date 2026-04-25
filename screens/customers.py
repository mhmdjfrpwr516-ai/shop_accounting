"""
screens/customers.py
Customer management screen
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp, sp
from kivy.clock import Clock

from screens.base import BaseScreen, HeaderLabel
from utils.theme import THEME, num, fa
from utils.widgets import (Card, FormInput, FormLabel, FormSpinner,
                            RoundedButton, IconButton, SectionTitle, Spacer,
                            CustomerRow, VBox, HBox, make_color, make_popup,
                            ConfirmPopup)


class CustomersScreen(BaseScreen):
    def __init__(self, db, **kwargs):
        super().__init__(db, **kwargs)
        self._build_header()
        self._build_body()

    def _build_header(self):
        self._header.clear_widgets()
        self._header.add_widget(HeaderLabel('👥 مشتریان'))
        add_btn = RoundedButton('+ افزودن', bg_color=THEME['accent'])
        add_btn.size_hint = (None, None)
        add_btn.size = (dp(90), dp(36))
        add_btn.bind(on_release=lambda *a: self._open_add())
        self._header.add_widget(add_btn)

    def _build_body(self):
        sv = self._content
        self._body = VBox(padding=dp(12), spacing=dp(8))
        sv.add_widget(self._body)

        self._search = FormInput(hint='🔍  جستجوی مشتری...')
        self._search.bind(text=lambda i, t: self._filter(t))
        self._body.add_widget(self._search)

        self._list = VBox(spacing=dp(6))
        self._body.add_widget(self._list)
        self._body.add_widget(Spacer(dp(70)))

    def refresh(self):
        self._filter(self._search.text if hasattr(self, '_search') else '')

    def _filter(self, q=''):
        self._list.clear_widgets()
        customers = self.db.get_customers(search=q)
        if not customers:
            self._list.add_widget(Label(
                text='مشتری‌ای یافت نشد', font_size=sp(13),
                color=make_color(THEME['text2']),
                size_hint_y=None, height=dp(50), halign='center'
            ))
            return
        for c in customers:
            invs = self.db.get_invoices()
            inv_count = sum(1 for i in invs if i.get('customer_id') == c['id'])
            inv_total = sum(i['grand_total'] for i in invs if i.get('customer_id') == c['id'])
            row = CustomerRow(c, inv_count=inv_count, inv_total=inv_total,
                              on_delete=self._confirm_delete)
            self._list.add_widget(row)

    def _open_add(self):
        content = self._make_form_content(None, None)
        self._form_popup = make_popup('افزودن مشتری', content, size=(dp(380), dp(440)))
        self._form_popup.open()

    def _make_form_content(self, customer, cid):
        body = VBox(padding=dp(12), spacing=dp(8))

        body.add_widget(FormLabel('نام و نام‌خانوادگی *'))
        name_input = FormInput(hint='نام مشتری')
        if customer:
            name_input.text = customer['name']
        body.add_widget(name_input)

        body.add_widget(FormLabel('شماره تلفن'))
        phone_input = FormInput(hint='۰۹۱۲۳۴۵۶۷۸۹', input_filter='int')
        if customer:
            phone_input.text = customer.get('phone', '')
        body.add_widget(phone_input)

        body.add_widget(FormLabel('آدرس'))
        addr_input = FormInput(hint='آدرس اختیاری')
        if customer:
            addr_input.text = customer.get('address', '')
        body.add_widget(addr_input)

        body.add_widget(FormLabel('کد ملی / شناسه'))
        natid_input = FormInput(hint='اختیاری', input_filter='int')
        if customer:
            natid_input.text = customer.get('national_id', '')
        body.add_widget(natid_input)

        body.add_widget(FormLabel('یادداشت'))
        notes_input = FormInput(hint='یادداشت اختیاری')
        if customer:
            notes_input.text = customer.get('notes', '')
        body.add_widget(notes_input)

        btn_row = HBox(size_hint_y=None, height=dp(46), spacing=dp(8))
        cancel_btn = RoundedButton('انصراف', bg_color=THEME['bg3'])
        save_btn = RoundedButton('💾 ذخیره')

        def do_save(*a):
            name = name_input.text.strip()
            if not name:
                return
            data = {
                'name': name,
                'phone': phone_input.text.strip(),
                'address': addr_input.text.strip(),
                'national_id': natid_input.text.strip(),
                'notes': notes_input.text.strip(),
            }
            self.db.save_customer(data, cid=cid)
            self._form_popup.dismiss()
            self.refresh()

        save_btn.bind(on_release=do_save)
        cancel_btn.bind(on_release=lambda *a: self._form_popup.dismiss())
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        body.add_widget(btn_row)

        sv = ScrollView()
        sv.add_widget(body)
        return sv

    def _confirm_delete(self, cid):
        customer = self.db.get_customer(cid)
        if not customer:
            return
        content = ConfirmPopup(
            message=f"آیا از حذف مشتری '{customer['name']}' مطمئنید؟",
            on_confirm=lambda: self._do_delete(cid),
            popup_ref=None
        )
        pop = make_popup('حذف مشتری', content, size=(dp(320), dp(180)))
        content.popup_ref = pop
        pop.open()

    def _do_delete(self, cid):
        self.db.delete_customer(cid)
        self.refresh()
