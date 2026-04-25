"""
screens/dashboard.py
Dashboard screen - sales overview, stats, charts, recent invoices
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex as hex_c
from kivy.clock import Clock

from screens.base import BaseScreen, HeaderLabel
from utils.theme import THEME, num, fa, short_date, weekday_fa
from utils.widgets import (Card, StatCard, SectionTitle, InvoiceRow,
                            AlertBox, RoundedButton, Spacer, BarChart,
                            make_color, VBox, HBox)


class DashboardScreen(BaseScreen):
    def __init__(self, db, **kwargs):
        super().__init__(db, **kwargs)
        self._build_header()
        self._build_body()

    def _build_header(self):
        self._header.clear_widgets()
        self._header.add_widget(HeaderLabel('📊 داشبورد'))
        self._today_badge = Label(
            text='', font_size=sp(11),
            color=make_color(THEME['white']),
            size_hint=(None, None), size=(dp(100), dp(26)),
        )
        with self._today_badge.canvas.before:
            Color(*make_color(THEME['accent']))
            self._badge_bg = RoundedRectangle(radius=[dp(13)],
                                              pos=self._today_badge.pos,
                                              size=self._today_badge.size)
        self._today_badge.bind(
            pos=lambda *a: setattr(self._badge_bg, 'pos', self._today_badge.pos),
            size=lambda *a: setattr(self._badge_bg, 'size', self._today_badge.size)
        )
        self._header.add_widget(self._today_badge)

    def _build_body(self):
        sv = self._content
        self._body = VBox(padding=dp(12), spacing=dp(10))
        sv.add_widget(self._body)

    def refresh(self):
        Clock.schedule_once(lambda dt: self._do_refresh(), 0)

    def _do_refresh(self):
        self._body.clear_widgets()
        stats = self.db.get_stats()
        low_stock = self.db.get_low_stock()

        # Header badge
        self._today_badge.text = f"امروز: {num(stats['today_total'])} ت"

        # Stats grid 2x2
        grid = GridLayout(cols=2, spacing=dp(8),
                          size_hint_y=None, height=dp(160))
        grid.add_widget(StatCard('فروش امروز',
                                 num(stats['today_total']) + ' ت',
                                 fa(stats['today_count']) + ' فاکتور',
                                 THEME['green']))
        grid.add_widget(StatCard('فروش ماه',
                                 num(stats['month_total']) + ' ت',
                                 fa(stats['month_count']) + ' فاکتور',
                                 THEME['accent']))
        grid.add_widget(StatCard('تعداد کالا',
                                 fa(stats['prod_count']),
                                 'موجودی کم: ' + fa(stats['low_stock_count']),
                                 THEME['amber']))
        grid.add_widget(StatCard('مشتریان',
                                 fa(stats['cust_count']),
                                 'ثبت شده',
                                 THEME['accent2']))
        self._body.add_widget(grid)

        # Low stock alert
        if low_stock:
            names = '، '.join(p['name'] for p in low_stock[:3])
            suffix = ' ...' if len(low_stock) > 3 else ''
            msg = f"⚠️ {fa(len(low_stock))} کالا موجودی کم: {names}{suffix}"
            self._body.add_widget(AlertBox(msg, THEME['amber']))

        # Weekly chart
        weekly = self.db.get_weekly_sales()
        chart_card = Card()
        chart_inner = VBox(padding=dp(10), spacing=dp(6))
        chart_inner.add_widget(Label(
            text='نمودار فروش ۷ روز', font_size=sp(12),
            color=make_color(THEME['text2']),
            size_hint_y=None, height=dp(20), halign='right'
        ))
        chart_inner.add_widget(BarChart(weekly, height=dp(80)))
        chart_card.add_widget(chart_inner)
        chart_card.height = dp(130)
        self._body.add_widget(chart_card)

        # Recent invoices
        self._body.add_widget(SectionTitle('🕐 آخرین فاکتورها'))
        recent = self.db.get_invoices(limit=5)
        if not recent:
            self._body.add_widget(Label(
                text='هنوز فاکتوری ثبت نشده',
                color=make_color(THEME['text2']),
                font_size=sp(13), size_hint_y=None, height=dp(40)
            ))
        else:
            for inv in recent:
                row = InvoiceRow(inv, on_tap=self._open_invoice)
                self._body.add_widget(row)

        self._body.add_widget(Spacer(dp(70)))

    def _open_invoice(self, inv_id):
        screen = self.manager.get_screen('invoice_view')
        screen.load_invoice(inv_id)
        self.manager.current = 'invoice_view'
