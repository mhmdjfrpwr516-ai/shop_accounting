"""
screens/invoice.py
Invoice creation screen
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as hex_c

from screens.base import BaseScreen, HeaderLabel
from utils.theme import THEME, num, fa
from utils.widgets import (Card, FormInput, FormLabel, FormGroup, FormSpinner,
                            RoundedButton, IconButton, SectionTitle, Spacer,
                            VBox, HBox, make_color, make_popup, AlertBox)


class InvoiceScreen(BaseScreen):
    def __init__(self, db, **kwargs):
        super().__init__(db, **kwargs)
        self.items = []
        self._build_header()
        self._build_body()

    def _build_header(self):
        self._header.clear_widgets()
        self._header.add_widget(HeaderLabel('🧾 ثبت فاکتور'))
        hist_btn = Button(
            text='📋 تاریخچه', font_size=sp(12),
            color=make_color(THEME['accent']),
            background_color=(0, 0, 0, 0),
            size_hint=(None, 1), width=dp(90)
        )
        hist_btn.bind(on_release=lambda *a: self._show_history())
        self._header.add_widget(hist_btn)

    def _build_body(self):
        sv = self._content
        body = VBox(padding=dp(12), spacing=dp(10))
        sv.add_widget(body)

        # Invoice number
        inv_row = HBox(size_hint_y=None, height=dp(24), spacing=dp(6))
        self._inv_num_lbl = Label(
            text='', font_size=sp(12),
            color=make_color(THEME['text2']), halign='right'
        )
        self._inv_num_lbl.bind(size=self._inv_num_lbl.setter('text_size'))
        inv_row.add_widget(self._inv_num_lbl)
        body.add_widget(inv_row)

        # Customer selection
        cust_card = Card()
        cust_card.add_widget(FormLabel('مشتری'))
        self._cust_spinner = FormSpinner(['-- انتخاب مشتری --'])
        cust_card.add_widget(self._cust_spinner)
        cust_card.add_widget(Spacer(dp(8)))
        cust_card.add_widget(FormLabel('توضیحات'))
        self._desc_input = FormInput(hint='توضیحات اختیاری...')
        cust_card.add_widget(self._desc_input)
        body.add_widget(cust_card)

        # Add item section
        body.add_widget(SectionTitle('➕ افزودن کالا'))
        item_card = Card()

        item_card.add_widget(FormLabel('انتخاب کالا'))
        self._prod_spinner = FormSpinner(['انتخاب کالا...'])
        self._prod_spinner.bind(text=self._on_product_selected)
        item_card.add_widget(self._prod_spinner)

        qty_price_row = HBox(size_hint_y=None, height=dp(82), spacing=dp(8))

        qty_box = VBox(spacing=dp(4))
        qty_box.add_widget(FormLabel('تعداد'))
        self._qty_input = FormInput(hint='۱', input_filter='float')
        self._qty_input.text = '1'
        qty_box.add_widget(self._qty_input)
        qty_price_row.add_widget(qty_box)

        price_box = VBox(spacing=dp(4))
        price_box.add_widget(FormLabel('قیمت (تومان)'))
        self._price_input = FormInput(hint='۰', input_filter='float')
        self._price_input.bind(text=self._calc_total)
        price_box.add_widget(self._price_input)
        qty_price_row.add_widget(price_box)

        item_card.add_widget(qty_price_row)

        add_btn = RoundedButton('+ افزودن به فاکتور')
        add_btn.bind(on_release=lambda *a: self._add_item())
        item_card.add_widget(add_btn)
        body.add_widget(item_card)

        # Items list (dynamic)
        self._items_section = VBox(spacing=dp(6))
        body.add_widget(self._items_section)

        # Totals card
        self._totals_card = Card()
        self._totals_card.opacity = 0

        disc_tax_row = HBox(size_hint_y=None, height=dp(88), spacing=dp(8))

        disc_box = VBox(spacing=dp(4))
        disc_box.add_widget(FormLabel('تخفیف (٪)'))
        self._disc_input = FormInput(hint='۰', input_filter='float')
        self._disc_input.text = '0'
        self._disc_input.bind(text=self._recalc)
        disc_box.add_widget(self._disc_input)
        disc_tax_row.add_widget(disc_box)

        tax_box = VBox(spacing=dp(4))
        tax_box.add_widget(FormLabel('مالیات (٪)'))
        self._tax_input = FormInput(hint='۹', input_filter='float')
        self._tax_input.text = '9'
        self._tax_input.bind(text=self._recalc)
        tax_box.add_widget(self._tax_input)
        disc_tax_row.add_widget(tax_box)

        self._totals_card.add_widget(disc_tax_row)

        self._totals_card.add_widget(FormLabel('وضعیت پرداخت'))
        self._status_spinner = FormSpinner(['پرداخت شده', 'در انتظار پرداخت'])
        self._totals_card.add_widget(self._status_spinner)

        self._totals_card.add_widget(Spacer(dp(8)))
        self._grand_lbl = Label(
            text='مبلغ نهایی: ۰ تومان', font_size=sp(16), bold=True,
            color=make_color(THEME['accent']),
            halign='right', size_hint_y=None, height=dp(28)
        )
        self._grand_lbl.bind(size=self._grand_lbl.setter('text_size'))
        self._totals_card.add_widget(self._grand_lbl)

        body.add_widget(self._totals_card)

        # Action buttons
        self._action_row = HBox(size_hint_y=None, height=dp(46), spacing=dp(8))
        self._action_row.opacity = 0

        preview_btn = RoundedButton('👁️ پیش‌نمایش', bg_color=THEME['bg3'])
        preview_btn.bind(on_release=lambda *a: self._preview())
        self._action_row.add_widget(preview_btn)

        save_btn = RoundedButton('💾 ذخیره فاکتور', bg_color=THEME['green'])
        save_btn.bind(on_release=lambda *a: self._save())
        self._action_row.add_widget(save_btn)

        body.add_widget(self._action_row)
        body.add_widget(Spacer(dp(70)))

    def refresh(self):
        # Update invoice number
        inv_num = self.db.get_setting('inv_counter', '1')
        self._inv_num_lbl.text = f"شماره فاکتور: #{fa(str(inv_num).zfill(3))}"

        # Update customer spinner
        customers = self.db.get_customers()
        cust_names = ['-- انتخاب مشتری --'] + [c['name'] for c in customers]
        self._cust_spinner.values = cust_names
        self._cust_spinner._customers = customers

        # Update product spinner
        products = self.db.get_products()
        prod_names = ['انتخاب کالا...'] + [f"{p['name']} (موجودی: {fa(p['stock'])})" for p in products]
        self._prod_spinner.values = prod_names
        self._prod_spinner._products = products

    def _on_product_selected(self, spinner, text):
        if not hasattr(spinner, '_products'):
            return
        if text == 'انتخاب کالا...':
            return
        for p in spinner._products:
            display = f"{p['name']} (موجودی: {fa(p['stock'])})"
            if display == text:
                self._price_input.text = str(int(p['price']))
                self._qty_input.text = '1'
                self._calc_total()
                break

    def _calc_total(self, *a):
        try:
            qty = float(self._qty_input.text or 0)
            price = float(self._price_input.text or 0)
        except ValueError:
            pass

    def _add_item(self):
        prod_text = self._prod_spinner.text
        if prod_text == 'انتخاب کالا...' or not hasattr(self._prod_spinner, '_products'):
            self._show_error('کالا را انتخاب کنید')
            return
        try:
            qty = float(self._qty_input.text or 0)
            price = float(self._price_input.text or 0)
        except ValueError:
            self._show_error('تعداد و قیمت معتبر وارد کنید')
            return
        if qty <= 0 or price <= 0:
            self._show_error('تعداد و قیمت باید بیش از صفر باشد')
            return

        prod = None
        for p in self._prod_spinner._products:
            display = f"{p['name']} (موجودی: {fa(p['stock'])})"
            if display == prod_text:
                prod = p
                break
        if not prod:
            return

        if qty > prod['stock']:
            self._show_error(f"موجودی کافی نیست! موجودی: {fa(prod['stock'])}")
            return

        # Check if already in items
        existing = next((i for i in self.items if i['pid'] == prod['id']), None)
        if existing:
            existing['qty'] += qty
            existing['total'] = existing['qty'] * existing['price']
        else:
            self.items.append({
                'pid': prod['id'], 'name': prod['name'],
                'qty': qty, 'price': price,
                'total': qty * price, 'unit': prod['unit']
            })

        self._render_items()
        self._prod_spinner.text = 'انتخاب کالا...'
        self._qty_input.text = '1'
        self._price_input.text = ''

    def _render_items(self):
        self._items_section.clear_widgets()
        if not self.items:
            self._totals_card.opacity = 0
            self._action_row.opacity = 0
            return

        self._totals_card.opacity = 1
        self._action_row.opacity = 1

        self._items_section.add_widget(SectionTitle('📋 اقلام فاکتور'))
        card = Card(padding=dp(8))
        for i, item in enumerate(self.items):
            row = HBox(size_hint_y=None, height=dp(44), spacing=dp(6))
            info = Label(
                text=f"{item['name']}\n{fa(item['qty'])} {item['unit']} × {num(item['price'])} = {num(item['total'])} ت",
                font_size=sp(11), color=make_color(THEME['text']),
                halign='right', size_hint_x=1
            )
            info.bind(size=info.setter('text_size'))
            del_btn = IconButton('✕', bg_color=THEME['red'])
            del_btn.size_hint_x = None
            idx = i
            del_btn.bind(on_release=lambda *a, ii=idx: self._remove_item(ii))
            row.add_widget(info)
            row.add_widget(del_btn)
            card.add_widget(row)
        self._items_section.add_widget(card)
        self._recalc()

    def _remove_item(self, idx):
        if 0 <= idx < len(self.items):
            self.items.pop(idx)
        self._render_items()

    def _recalc(self, *a):
        if not self.items:
            return
        subtotal = sum(i['total'] for i in self.items)
        try:
            disc = float(self._disc_input.text or 0)
            tax = float(self._tax_input.text or 0)
        except ValueError:
            disc, tax = 0, 9
        disc_amt = subtotal * disc / 100
        after_disc = subtotal - disc_amt
        tax_amt = after_disc * tax / 100
        grand = round(after_disc + tax_amt)
        self._grand_lbl.text = f"مبلغ نهایی: {num(grand)} تومان"

    def _get_invoice_data(self):
        subtotal = sum(i['total'] for i in self.items)
        try:
            disc = float(self._disc_input.text or 0)
            tax = float(self._tax_input.text or 0)
        except ValueError:
            disc, tax = 0, 9
        disc_amt = round(subtotal * disc / 100)
        after_disc = subtotal - disc_amt
        tax_amt = round(after_disc * tax / 100)
        grand = round(after_disc + tax_amt)

        cust_name = 'مشتری آزاد'
        cust_id = None
        cust_phone = ''
        if hasattr(self._cust_spinner, '_customers'):
            sel = self._cust_spinner.text
            for c in self._cust_spinner._customers:
                if c['name'] == sel:
                    cust_name = c['name']
                    cust_id = c['id']
                    cust_phone = c.get('phone', '')
                    break

        inv_num = int(self.db.get_setting('inv_counter', '1'))
        status = 'paid' if self._status_spinner.text == 'پرداخت شده' else 'pending'

        return {
            'number': inv_num,
            'customer_id': cust_id,
            'customer_name': cust_name,
            'customer_phone': cust_phone,
            'items': list(self.items),
            'subtotal': subtotal,
            'discount_pct': disc,
            'discount_amt': disc_amt,
            'tax_pct': tax,
            'tax_amt': tax_amt,
            'grand_total': grand,
            'description': self._desc_input.text,
            'status': status,
        }

    def _preview(self):
        if not self.items:
            self._show_error('حداقل یک کالا اضافه کنید')
            return
        data = self._get_invoice_data()
        self._show_invoice_preview(data, save_on_confirm=True)

    def _save(self):
        if not self.items:
            self._show_error('حداقل یک کالا اضافه کنید')
            return
        data = self._get_invoice_data()
        self.db.save_invoice(data)
        self._reset_form()
        self._show_success(f"فاکتور #{fa(data['number'])} با موفقیت ذخیره شد!")

    def _reset_form(self):
        self.items = []
        self._items_section.clear_widgets()
        self._totals_card.opacity = 0
        self._action_row.opacity = 0
        self._desc_input.text = ''
        self._disc_input.text = '0'
        self._tax_input.text = '9'
        if hasattr(self._cust_spinner, 'values') and self._cust_spinner.values:
            self._cust_spinner.text = self._cust_spinner.values[0]
        inv_num = self.db.get_setting('inv_counter', '1')
        self._inv_num_lbl.text = f"شماره فاکتور: #{fa(str(inv_num).zfill(3))}"

    def _show_history(self):
        from screens.invoice_list import InvoiceListPopup
        InvoiceListPopup(self.db, self.manager).open()

    def _show_invoice_preview(self, data, save_on_confirm=False):
        from utils.invoice_pdf import InvoicePreviewPopup
        InvoicePreviewPopup(data, self.db, on_save=self._save if save_on_confirm else None).open()

    def _show_error(self, msg):
        from utils.widgets import make_popup
        from kivy.uix.label import Label as KLabel
        content = VBox(padding=dp(16), spacing=dp(12))
        content.add_widget(KLabel(
            text=msg, font_size=sp(14),
            color=make_color(THEME['red']),
            halign='center'
        ))
        ok = RoundedButton('باشه')
        content.add_widget(ok)
        pop = make_popup('خطا', content, size=(dp(320), dp(160)))
        ok.bind(on_release=lambda *a: pop.dismiss())
        pop.open()

    def _show_success(self, msg):
        from utils.widgets import make_popup
        content = VBox(padding=dp(16), spacing=dp(12))
        content.add_widget(Label(
            text=msg, font_size=sp(14),
            color=make_color(THEME['green']),
            halign='center'
        ))
        ok = RoundedButton('باشه')
        content.add_widget(ok)
        pop = make_popup('✅ موفق', content, size=(dp(320), dp(160)))
        ok.bind(on_release=lambda *a: pop.dismiss())
        pop.open()
