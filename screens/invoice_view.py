"""
screens/invoice_view.py
View a single saved invoice + Invoice list popup
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp, sp
from datetime import datetime

from screens.base import BaseScreen, HeaderLabel
from utils.theme import THEME, num, fa
from utils.widgets import (Card, RoundedButton, IconButton, SectionTitle,
                            Spacer, VBox, HBox, make_color, make_popup,
                            InvoiceRow, FormInput, ConfirmPopup)


class InvoiceViewScreen(BaseScreen):
    def __init__(self, db, **kwargs):
        super().__init__(db, **kwargs)
        self._inv_id = None
        self._build_header()
        self._build_body()

    def _build_header(self):
        self._header.clear_widgets()
        back_btn = IconButton('← ')
        back_btn.bind(on_release=lambda *a: self._go_back())
        self._header.add_widget(back_btn)
        self._title_lbl = HeaderLabel('مشاهده فاکتور')
        self._header.add_widget(self._title_lbl)

    def _go_back(self):
        if self.manager.current == 'invoice_view':
            self.manager.current = 'dashboard'

    def _build_body(self):
        sv = self._content
        self._body = VBox(padding=dp(12), spacing=dp(10))
        sv.add_widget(self._body)

    def load_invoice(self, inv_id):
        self._inv_id = inv_id

    def refresh(self):
        if not self._inv_id:
            return
        self._body.clear_widgets()
        inv = self.db.get_invoice(self._inv_id)
        if not inv:
            self._body.add_widget(Label(
                text='فاکتور یافت نشد',
                color=make_color(THEME['red']),
                font_size=sp(14), size_hint_y=None, height=dp(50)
            ))
            return

        dt = datetime.fromtimestamp(inv['created_at']).strftime('%Y/%m/%d  %H:%M')
        status_text = '✅ پرداخت شده' if inv['status'] == 'paid' else '⏳ در انتظار'
        status_color = THEME['green'] if inv['status'] == 'paid' else THEME['amber']

        self._title_lbl.text = f"فاکتور #{fa(inv['number'])}"

        # Info card
        info_card = Card()
        info_data = [
            ('شماره فاکتور', f"#{fa(inv['number'])}"),
            ('تاریخ', dt),
            ('مشتری', inv['customer_name']),
            ('تلفن', inv.get('customer_phone') or '---'),
            ('وضعیت', status_text),
            ('توضیحات', inv.get('description') or '---'),
        ]
        for label, value in info_data:
            row = HBox(size_hint_y=None, height=dp(28))
            row.add_widget(Label(
                text=label + ':', font_size=sp(12),
                color=make_color(THEME['text2']),
                halign='right', size_hint_x=None, width=dp(90)
            ))
            lbl = Label(
                text=value, font_size=sp(12),
                color=make_color(status_color if label == 'وضعیت' else THEME['text']),
                halign='right', bold=(label == 'وضعیت')
            )
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)
            for l in row.children:
                if isinstance(l, Label):
                    l.bind(size=l.setter('text_size'))
            info_card.add_widget(row)
        self._body.add_widget(info_card)

        # Items table
        self._body.add_widget(SectionTitle('📋 اقلام فاکتور'))
        items_card = Card(padding=dp(8))
        # Header row
        h_row = HBox(size_hint_y=None, height=dp(28))
        for text, w in [('کالا', 1), ('تعداد', None), ('قیمت', None), ('جمع', None)]:
            kw = {'size_hint_x': w} if w else {'size_hint_x': None, 'width': dp(70)}
            items_card.add_widget(Label(
                text=text, font_size=sp(11), bold=True,
                color=make_color(THEME['text2']),
                halign='center', **kw
            ))
        for item in inv['items']:
            row = HBox(size_hint_y=None, height=dp(36))
            name_lbl = Label(text=item['name'], font_size=sp(11), color=make_color(THEME['text']), halign='right', size_hint_x=1)
            name_lbl.bind(size=name_lbl.setter('text_size'))
            row.add_widget(name_lbl)
            row.add_widget(Label(text=f"{fa(item['qty'])}{item['unit']}", font_size=sp(11), color=make_color(THEME['text']), size_hint_x=None, width=dp(70), halign='center'))
            row.add_widget(Label(text=num(item['price']), font_size=sp(11), color=make_color(THEME['text']), size_hint_x=None, width=dp(70), halign='center'))
            row.add_widget(Label(text=num(item['total']), font_size=sp(11), color=make_color(THEME['green']), size_hint_x=None, width=dp(70), halign='center'))
            items_card.add_widget(row)
        self._body.add_widget(items_card)

        # Totals
        totals_card = Card()
        totals = [
            ('جمع کل:', num(inv['subtotal']) + ' ت', THEME['text']),
        ]
        if inv['discount_pct'] > 0:
            totals.append((f"تخفیف ({fa(int(inv['discount_pct']))}٪):", '- ' + num(inv['discount_amt']) + ' ت', THEME['red']))
        if inv['tax_pct'] > 0:
            totals.append((f"مالیات ({fa(int(inv['tax_pct']))}٪):", num(inv['tax_amt']) + ' ت', THEME['amber']))
        totals.append(('مبلغ نهایی:', num(inv['grand_total']) + ' تومان', THEME['accent']))
        for label, value, color in totals:
            row = HBox(size_hint_y=None, height=dp(30))
            row.add_widget(Label(text=label, font_size=sp(13 if label == 'مبلغ نهایی:' else 12), color=make_color(THEME['text2']), halign='right'))
            row.add_widget(Label(text=value, font_size=sp(14 if label == 'مبلغ نهایی:' else 12), bold=(label == 'مبلغ نهایی:'), color=make_color(color), halign='left'))
            for l in row.children:
                l.bind(size=l.setter('text_size'))
            totals_card.add_widget(row)
        self._body.add_widget(totals_card)

        # Action buttons
        btn_row = HBox(size_hint_y=None, height=dp(46), spacing=dp(8))
        toggle_lbl = 'تغییر به: در انتظار' if inv['status'] == 'paid' else 'تغییر به: پرداخت شده'
        toggle_color = THEME['amber'] if inv['status'] == 'paid' else THEME['green']
        toggle_btn = RoundedButton(toggle_lbl, bg_color=toggle_color)
        toggle_btn.bind(on_release=lambda *a: self._toggle_status(inv))
        del_btn = RoundedButton('🗑️ حذف', bg_color=THEME['red'])
        del_btn.bind(on_release=lambda *a: self._confirm_delete(inv['id']))
        btn_row.add_widget(toggle_btn)
        btn_row.add_widget(del_btn)
        self._body.add_widget(btn_row)
        self._body.add_widget(Spacer(dp(70)))

    def _toggle_status(self, inv):
        new_status = 'pending' if inv['status'] == 'paid' else 'paid'
        self.db.update_invoice_status(inv['id'], new_status)
        self.refresh()

    def _confirm_delete(self, inv_id):
        content = ConfirmPopup(
            message='آیا از حذف این فاکتور مطمئنید؟\n(موجودی کالاها بازگردانده می‌شود)',
            on_confirm=lambda: self._do_delete(inv_id),
            popup_ref=None
        )
        pop = make_popup('حذف فاکتور', content, size=(dp(320), dp(200)))
        content.popup_ref = pop
        pop.open()

    def _do_delete(self, inv_id):
        self.db.delete_invoice(inv_id)
        self.manager.current = 'dashboard'


# ─── Invoice list popup ───
class InvoiceListPopup:
    def __init__(self, db, manager):
        self.db = db
        self.manager = manager
        self._popup = None

    def open(self):
        body = VBox(padding=dp(12), spacing=dp(8))

        search = FormInput(hint='🔍 جستجو...')
        body.add_widget(search)

        list_area = VBox(spacing=dp(6))
        body.add_widget(list_area)

        def render(q=''):
            list_area.clear_widgets()
            invs = self.db.get_invoices(search=q)
            if not invs:
                list_area.add_widget(Label(
                    text='فاکتوری یافت نشد', font_size=sp(13),
                    color=make_color(THEME['text2']),
                    size_hint_y=None, height=dp(40), halign='center'
                ))
                return
            for inv in invs:
                row = InvoiceRow(inv, on_tap=self._open_inv)
                list_area.add_widget(row)

        search.bind(text=lambda i, t: render(t))
        render()

        sv = ScrollView()
        sv.add_widget(body)
        self._popup = make_popup('📋 تاریخچه فاکتورها', sv, size=(dp(400), dp(600)))
        self._popup.open()

    def _open_inv(self, inv_id):
        if self._popup:
            self._popup.dismiss()
        screen = self.manager.get_screen('invoice_view')
        screen.load_invoice(inv_id)
        self.manager.current = 'invoice_view'
