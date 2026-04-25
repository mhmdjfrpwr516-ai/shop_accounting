"""
screens/reports.py
Financial reports screen
"""

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.clock import Clock

from screens.base import BaseScreen, HeaderLabel
from utils.theme import THEME, num, fa
from utils.widgets import (Card, StatCard, SectionTitle, RoundedButton,
                            Spacer, VBox, HBox, make_color, make_popup)


class ReportsScreen(BaseScreen):
    def __init__(self, db, **kwargs):
        super().__init__(db, **kwargs)
        self._build_header()
        self._build_body()

    def _build_header(self):
        self._header.clear_widgets()
        self._header.add_widget(HeaderLabel('📈 گزارشات مالی'))

    def _build_body(self):
        sv = self._content
        self._body = VBox(padding=dp(12), spacing=dp(10))
        sv.add_widget(self._body)

    def refresh(self):
        Clock.schedule_once(lambda dt: self._do_refresh(), 0)

    def _do_refresh(self):
        self._body.clear_widgets()
        stats = self.db.get_stats()

        # Summary grid
        self._body.add_widget(SectionTitle('💰 خلاصه مالی کل'))
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(160))
        grid.add_widget(StatCard('کل درآمد', num(stats['all_total']) + ' ت', fa(stats['all_count']) + ' فاکتور', THEME['green']))
        grid.add_widget(StatCard('پرداخت نشده', num(stats['pending_total']) + ' ت', 'در انتظار', THEME['amber']))
        avg = round(stats['all_total'] / stats['all_count']) if stats['all_count'] else 0
        grid.add_widget(StatCard('میانگین فاکتور', num(avg) + ' ت', 'به ازای هر فاکتور', THEME['accent']))
        grid.add_widget(StatCard('این ماه', num(stats['month_total']) + ' ت', fa(stats['month_count']) + ' فاکتور', THEME['accent2']))
        self._body.add_widget(grid)

        # Top products
        self._body.add_widget(SectionTitle('🏆 پرفروش‌ترین کالاها'))
        top_prods = self.db.get_top_products()
        prod_card = Card()
        if not top_prods:
            prod_card.add_widget(Label(
                text='داده‌ای موجود نیست', font_size=sp(12),
                color=make_color(THEME['text2']),
                size_hint_y=None, height=dp(36), halign='center'
            ))
        else:
            for name, data in top_prods:
                row = HBox(size_hint_y=None, height=dp(36), spacing=dp(6))
                row.add_widget(Label(
                    text=name, font_size=sp(12),
                    color=make_color(THEME['text']),
                    halign='right', size_hint_x=1
                ))
                row.add_widget(Label(
                    text=f"{num(data['total'])} ت | {fa(data['qty'])} عدد",
                    font_size=sp(11), color=make_color(THEME['green']),
                    size_hint_x=None, width=dp(130), halign='left'
                ))
                for lbl in row.children:
                    if isinstance(lbl, Label):
                        lbl.bind(size=lbl.setter('text_size'))
                prod_card.add_widget(row)
        self._body.add_widget(prod_card)

        # Top customers
        self._body.add_widget(SectionTitle('👑 بهترین مشتریان'))
        top_custs = self.db.get_top_customers()
        cust_card = Card()
        if not top_custs:
            cust_card.add_widget(Label(
                text='داده‌ای موجود نیست', font_size=sp(12),
                color=make_color(THEME['text2']),
                size_hint_y=None, height=dp(36), halign='center'
            ))
        else:
            for c in top_custs:
                row = HBox(size_hint_y=None, height=dp(36), spacing=dp(6))
                row.add_widget(Label(
                    text=c['customer_name'], font_size=sp(12),
                    color=make_color(THEME['text']),
                    halign='right', size_hint_x=1
                ))
                row.add_widget(Label(
                    text=f"{num(c['total'])} ت | {fa(c['cnt'])} فاکتور",
                    font_size=sp(11), color=make_color(THEME['accent']),
                    size_hint_x=None, width=dp(130), halign='left'
                ))
                for lbl in row.children:
                    if isinstance(lbl, Label):
                        lbl.bind(size=lbl.setter('text_size'))
                cust_card.add_widget(row)
        self._body.add_widget(cust_card)

        # Invoice status breakdown
        self._body.add_widget(SectionTitle('📊 وضعیت فاکتورها'))
        status_card = Card()
        invs = self.db.get_invoices()
        paid = [i for i in invs if i['status'] == 'paid']
        pending = [i for i in invs if i['status'] == 'pending']
        paid_total = sum(i['grand_total'] for i in paid)
        pending_total_val = sum(i['grand_total'] for i in pending)
        s_row1 = HBox(size_hint_y=None, height=dp(30))
        s_row1.add_widget(Label(text=f"✅ پرداخت شده: {fa(len(paid))} فاکتور", font_size=sp(12), color=make_color(THEME['green']), halign='right'))
        s_row1.add_widget(Label(text=num(paid_total) + ' ت', font_size=sp(12), color=make_color(THEME['green']), halign='left'))
        s_row2 = HBox(size_hint_y=None, height=dp(30))
        s_row2.add_widget(Label(text=f"⏳ در انتظار: {fa(len(pending))} فاکتور", font_size=sp(12), color=make_color(THEME['amber']), halign='right'))
        s_row2.add_widget(Label(text=num(pending_total_val) + ' ت', font_size=sp(12), color=make_color(THEME['amber']), halign='left'))
        for row in [s_row1, s_row2]:
            for lbl in row.children:
                lbl.bind(size=lbl.setter('text_size'))
        status_card.add_widget(s_row1)
        status_card.add_widget(s_row2)
        self._body.add_widget(status_card)

        # Export section
        self._body.add_widget(SectionTitle('💾 خروجی داده'))
        export_card = Card()
        btn_row = HBox(size_hint_y=None, height=dp(46), spacing=dp(8))
        json_btn = RoundedButton('📦 JSON', bg_color=THEME['accent2'])
        json_btn.bind(on_release=lambda *a: self._export_json())
        csv_btn = RoundedButton('📊 CSV', bg_color=THEME['accent'])
        csv_btn.bind(on_release=lambda *a: self._export_csv())
        btn_row.add_widget(json_btn)
        btn_row.add_widget(csv_btn)
        export_card.add_widget(btn_row)

        clear_btn = RoundedButton('🗑️ پاک کردن همه داده‌ها', bg_color=THEME['red'])
        clear_btn.bind(on_release=lambda *a: self._confirm_clear())
        export_card.add_widget(Spacer(dp(6)))
        export_card.add_widget(clear_btn)
        self._body.add_widget(export_card)

        self._body.add_widget(Spacer(dp(70)))

    def _export_json(self):
        data = self.db.export_json()
        path = self._get_export_path('backup.json')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
        self._show_msg(f'✅ ذخیره شد:\n{path}')

    def _export_csv(self):
        data = self.db.export_csv_invoices()
        path = self._get_export_path('invoices.csv')
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write(data)
        self._show_msg(f'✅ ذخیره شد:\n{path}')

    def _get_export_path(self, filename):
        if platform == 'android':
            try:
                from android.storage import primary_external_storage_path  # type: ignore
                base = primary_external_storage_path()
            except Exception:
                base = os.path.expanduser('~')
        else:
            base = os.path.expanduser('~')
        return os.path.join(base, filename)

    def _confirm_clear(self):
        from utils.widgets import ConfirmPopup
        content = ConfirmPopup(
            message='⚠️ تمام داده‌ها پاک می‌شود!\nاین عمل قابل برگشت نیست.',
            on_confirm=self._do_clear,
            popup_ref=None
        )
        pop = make_popup('هشدار', content, size=(dp(320), dp(200)))
        content.popup_ref = pop
        pop.open()

    def _do_clear(self):
        conn = self.db.get_conn()
        conn.execute('DELETE FROM invoices')
        conn.execute('DELETE FROM products')
        conn.execute('DELETE FROM customers')
        conn.execute("UPDATE settings SET value='1' WHERE key='inv_counter'")
        conn.commit()
        self.refresh()
        self._show_msg('داده‌ها پاک شدند')

    def _show_msg(self, msg):
        content = VBox(padding=dp(16), spacing=dp(12))
        content.add_widget(Label(
            text=msg, font_size=sp(13),
            color=make_color(THEME['text']),
            halign='center', size_hint_y=None, height=dp(60)
        ))
        ok = RoundedButton('باشه')
        content.add_widget(ok)
        pop = make_popup('نتیجه', content, size=(dp(340), dp(180)))
        ok.bind(on_release=lambda *a: pop.dismiss())
        pop.open()
