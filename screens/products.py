"""
screens/products.py
Product management screen
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp, sp
from kivy.clock import Clock

from screens.base import BaseScreen, HeaderLabel
from utils.theme import THEME, num, fa
from utils.widgets import (Card, FormInput, FormLabel, FormSpinner, FormGroup,
                            RoundedButton, IconButton, SectionTitle, Spacer,
                            ProductRow, VBox, HBox, make_color, make_popup,
                            ConfirmPopup)


class ProductsScreen(BaseScreen):
    def __init__(self, db, **kwargs):
        super().__init__(db, **kwargs)
        self._build_header()
        self._build_body()

    def _build_header(self):
        self._header.clear_widgets()
        self._header.add_widget(HeaderLabel('📦 مدیریت کالا'))
        add_btn = RoundedButton('+ افزودن', bg_color=THEME['accent'])
        add_btn.size_hint = (None, None)
        add_btn.size = (dp(90), dp(36))
        add_btn.bind(on_release=lambda *a: self._open_add())
        self._header.add_widget(add_btn)

    def _build_body(self):
        sv = self._content
        self._body = VBox(padding=dp(12), spacing=dp(8))
        sv.add_widget(self._body)

        # Search
        self._search = FormInput(hint='🔍  جستجوی کالا...')
        self._search.bind(text=lambda i, t: self._filter(t))
        self._body.add_widget(self._search)

        self._list = VBox(spacing=dp(6))
        self._body.add_widget(self._list)
        self._body.add_widget(Spacer(dp(70)))

    def refresh(self):
        self._filter(self._search.text if hasattr(self, '_search') else '')

    def _filter(self, q=''):
        self._list.clear_widgets()
        products = self.db.get_products(search=q)
        if not products:
            self._list.add_widget(Label(
                text='کالایی یافت نشد', font_size=sp(13),
                color=make_color(THEME['text2']),
                size_hint_y=None, height=dp(50), halign='center'
            ))
            return
        for p in products:
            row = ProductRow(p, on_edit=self._open_edit, on_delete=self._confirm_delete)
            self._list.add_widget(row)

    def _open_add(self):
        self._open_form(None)

    def _open_edit(self, pid):
        self._open_form(pid)

    def _open_form(self, pid):
        product = self.db.get_product(pid) if pid else None
        content = self._make_form_content(product, pid)
        size = (dp(380), dp(520))
        title = 'ویرایش کالا' if pid else 'افزودن کالا جدید'
        self._form_popup = make_popup(title, content, size=size)
        self._form_popup.open()

    def _make_form_content(self, product, pid):
        body = VBox(padding=dp(12), spacing=dp(8))

        name_input = FormInput(hint='نام کالا *')
        if product:
            name_input.text = product['name']
        body.add_widget(FormLabel('نام کالا'))
        body.add_widget(name_input)

        row1 = HBox(size_hint_y=None, height=dp(82), spacing=dp(8))
        price_box = VBox(spacing=dp(4))
        price_box.add_widget(FormLabel('قیمت فروش (تومان)'))
        price_input = FormInput(hint='۰', input_filter='float')
        if product:
            price_input.text = str(int(product['price']))
        price_box.add_widget(price_input)
        row1.add_widget(price_box)

        stock_box = VBox(spacing=dp(4))
        stock_box.add_widget(FormLabel('موجودی'))
        stock_input = FormInput(hint='۰', input_filter='float')
        if product:
            stock_input.text = str(product['stock'])
        stock_box.add_widget(stock_input)
        row1.add_widget(stock_box)
        body.add_widget(row1)

        row2 = HBox(size_hint_y=None, height=dp(82), spacing=dp(8))
        cat_box = VBox(spacing=dp(4))
        cat_box.add_widget(FormLabel('دسته‌بندی'))
        cat_input = FormInput(hint='مثال: لبنیات')
        if product:
            cat_input.text = product.get('category', '')
        cat_box.add_widget(cat_input)
        row2.add_widget(cat_box)

        unit_box = VBox(spacing=dp(4))
        unit_box.add_widget(FormLabel('واحد'))
        unit_spin = FormSpinner(['عدد', 'کیلوگرم', 'لیتر', 'بسته', 'متر', 'جفت'])
        if product:
            unit_spin.text = product.get('unit', 'عدد')
        unit_box.add_widget(unit_spin)
        row2.add_widget(unit_box)
        body.add_widget(row2)

        body.add_widget(FormLabel('حداقل موجودی (هشدار)'))
        min_stock_input = FormInput(hint='۵', input_filter='float')
        min_stock_input.text = str(product['min_stock']) if product else '5'
        body.add_widget(min_stock_input)

        body.add_widget(FormLabel('بارکد (اختیاری)'))
        barcode_input = FormInput(hint='بارکد')
        if product:
            barcode_input.text = product.get('barcode', '')
        body.add_widget(barcode_input)

        btn_row = HBox(size_hint_y=None, height=dp(46), spacing=dp(8))
        cancel_btn = RoundedButton('انصراف', bg_color=THEME['bg3'])
        save_btn = RoundedButton('💾 ذخیره')

        def do_save(*a):
            name = name_input.text.strip()
            if not name:
                return
            data = {
                'name': name,
                'price': float(price_input.text or 0),
                'stock': float(stock_input.text or 0),
                'category': cat_input.text.strip(),
                'unit': unit_spin.text,
                'min_stock': float(min_stock_input.text or 5),
                'barcode': barcode_input.text.strip(),
            }
            self.db.save_product(data, pid=pid)
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

    def _confirm_delete(self, pid):
        product = self.db.get_product(pid)
        if not product:
            return
        content = ConfirmPopup(
            message=f"آیا از حذف '{product['name']}' مطمئنید؟",
            on_confirm=lambda: self._do_delete(pid),
            popup_ref=None
        )
        pop = make_popup('حذف کالا', content, size=(dp(320), dp(180)))
        content.popup_ref = pop
        pop.open()

    def _do_delete(self, pid):
        self.db.delete_product(pid)
        self.refresh()
