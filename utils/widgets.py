"""
utils/widgets.py
Reusable UI components for the shop accounting app
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex as hex_c
from utils.theme import THEME, num, fa, short_date, weekday_fa


def make_color(h):
    return hex_c(h) if isinstance(h, str) else h


def VBox(**kwargs):
    b = BoxLayout(orientation='vertical', size_hint_y=None, **kwargs)
    b.bind(minimum_height=b.setter('height'))
    return b


def HBox(**kwargs):
    return BoxLayout(orientation='horizontal', **kwargs)


def Spacer(h=dp(16)):
    w = Widget(size_hint_y=None, height=h)
    return w


# ─── CARD ───
class Card(BoxLayout):
    def __init__(self, padding=dp(14), **kwargs):
        super().__init__(
            orientation='vertical',
            size_hint_y=None,
            padding=padding,
            **kwargs
        )
        with self.canvas.before:
            Color(*make_color(THEME['card']))
            self._bg = RoundedRectangle(radius=[dp(12)], pos=self.pos, size=self.size)
            Color(*make_color(THEME['border']))
            self._border = Line(rounded_rectangle=[*self.pos, *self.size, dp(12)], width=dp(0.5))
        self.bind(pos=self._upd, size=self._upd)
        self.bind(minimum_height=self.setter('height'))

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = [*self.pos, *self.size, dp(12)]


# ─── STAT CARD ───
class StatCard(BoxLayout):
    def __init__(self, label, value, sub='', color=None, **kwargs):
        super().__init__(
            orientation='vertical',
            size_hint_y=None, height=dp(72),
            padding=dp(12), spacing=dp(4),
            **kwargs
        )
        color = color or THEME['accent']
        with self.canvas.before:
            Color(*make_color(THEME['card']))
            self._bg = RoundedRectangle(radius=[dp(10)], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        self.add_widget(Label(
            text=label, font_size=sp(11),
            color=make_color(THEME['text2']),
            halign='right', size_hint_y=None, height=dp(16)
        ))
        self.add_widget(Label(
            text=value, font_size=sp(16), bold=True,
            color=make_color(color),
            halign='right', size_hint_y=None, height=dp(22)
        ))
        if sub:
            self.add_widget(Label(
                text=sub, font_size=sp(10),
                color=make_color(THEME['text2']),
                halign='right', size_hint_y=None, height=dp(14)
            ))

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size


# ─── SECTION TITLE ───
class SectionTitle(Label):
    def __init__(self, text, **kwargs):
        super().__init__(
            text=text, font_size=sp(14), bold=True,
            color=make_color(THEME['text']),
            halign='right', size_hint_y=None, height=dp(32),
            **kwargs
        )
        self.bind(size=self.setter('text_size'))


# ─── ALERT BOX ───
class AlertBox(BoxLayout):
    def __init__(self, msg, color=None, **kwargs):
        super().__init__(
            size_hint_y=None, height=dp(40),
            padding=[dp(12), dp(8)], **kwargs
        )
        color = color or THEME['amber']
        with self.canvas.before:
            Color(*make_color(color), 0.15)
            self._bg = RoundedRectangle(radius=[dp(8)], pos=self.pos, size=self.size)
            Color(*make_color(color))
            self._border = Line(rounded_rectangle=[*self.pos, *self.size, dp(8)], width=dp(0.7))
        self.bind(pos=self._upd, size=self._upd)
        self.add_widget(Label(
            text=msg, font_size=sp(11),
            color=make_color(color),
            halign='right',
        ))
        self.bind(size=lambda *a: [c.__setattr__('text_size', c.size) for c in self.children if isinstance(c, Label)])

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = [*self.pos, *self.size, dp(8)]


# ─── INVOICE ROW ───
class InvoiceRow(Button):
    def __init__(self, inv, on_tap=None, **kwargs):
        self.inv = inv
        self.on_tap_cb = on_tap
        status_color = THEME['green'] if inv['status'] == 'paid' else THEME['amber']
        status_text = 'پرداخت شده' if inv['status'] == 'paid' else 'در انتظار'
        from datetime import datetime
        dt = datetime.fromtimestamp(inv['created_at']).strftime('%m/%d')
        text = (f"فاکتور #{fa(inv['number'])}  {inv['customer_name']}\n"
                f"{dt}  |  {num(inv['grand_total'])} تومان  |  {status_text}")
        super().__init__(
            text=text,
            font_size=sp(12),
            color=make_color(THEME['text']),
            halign='right', valign='middle',
            size_hint_y=None, height=dp(60),
            background_normal='', background_color=(0, 0, 0, 0),
            **kwargs
        )
        with self.canvas.before:
            Color(*make_color(THEME['bg3']))
            self._bg = RoundedRectangle(radius=[dp(8)], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd, size=self.setter('text_size'))
        self.bind(on_release=self._tapped)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _tapped(self, *a):
        if self.on_tap_cb:
            self.on_tap_cb(self.inv['id'])


# ─── ROUNDED BUTTON ───
class RoundedButton(Button):
    def __init__(self, text, bg_color=None, text_color=None, **kwargs):
        bg = bg_color or THEME['accent']
        tc = text_color or THEME['white']
        super().__init__(
            text=text, font_size=sp(14), bold=True,
            color=make_color(tc),
            background_normal='', background_color=(0, 0, 0, 0),
            size_hint_y=None, height=dp(46),
            **kwargs
        )
        with self.canvas.before:
            Color(*make_color(bg))
            self._bg = RoundedRectangle(radius=[dp(10)], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size


# ─── SMALL ICON BUTTON ───
class IconButton(Button):
    def __init__(self, icon, bg_color=None, **kwargs):
        bg = bg_color or THEME['bg3']
        super().__init__(
            text=icon, font_size=sp(14),
            color=make_color(THEME['text']),
            background_normal='', background_color=(0, 0, 0, 0),
            size_hint=(None, None), size=(dp(36), dp(36)),
            **kwargs
        )
        with self.canvas.before:
            Color(*make_color(bg))
            self._bg = RoundedRectangle(radius=[dp(8)], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size


# ─── FORM INPUT ───
class FormInput(TextInput):
    def __init__(self, hint='', **kwargs):
        super().__init__(
            hint_text=hint,
            font_size=sp(14),
            foreground_color=make_color(THEME['text']),
            hint_text_color=make_color(THEME['text2']),
            background_normal='', background_active='',
            background_color=make_color(THEME['bg3']),
            cursor_color=make_color(THEME['accent']),
            padding=[dp(12), dp(10), dp(12), dp(10)],
            size_hint_y=None, height=dp(44),
            multiline=False,
            write_tab=False,
            **kwargs
        )
        with self.canvas.after:
            Color(*make_color(THEME['border']))
            self._border = RoundedRectangle(radius=[dp(8)], pos=self.pos, size=self.size)
        # Override to draw only border
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._border.pos = self.pos
        self._border.size = self.size


# ─── FORM LABEL ───
class FormLabel(Label):
    def __init__(self, text, **kwargs):
        super().__init__(
            text=text, font_size=sp(12),
            color=make_color(THEME['text2']),
            halign='right', size_hint_y=None, height=dp(20),
            **kwargs
        )
        self.bind(size=self.setter('text_size'))


# ─── FORM GROUP ───
class FormGroup(VBox):
    def __init__(self, label, widget, **kwargs):
        super().__init__(spacing=dp(4), **kwargs)
        self.add_widget(FormLabel(label))
        self.add_widget(widget)


# ─── SPINNER INPUT ───
class FormSpinner(Spinner):
    def __init__(self, values, **kwargs):
        super().__init__(
            values=values,
            text=values[0] if values else '',
            font_size=sp(13),
            color=make_color(THEME['text']),
            background_normal='', background_down='',
            background_color=make_color(THEME['bg3']),
            option_cls=SpinnerOption,
            size_hint_y=None, height=dp(44),
            **kwargs
        )
        with self.canvas.before:
            Color(*make_color(THEME['bg3']))
            self._bg = RoundedRectangle(radius=[dp(8)], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size


class SpinnerOption(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = make_color(THEME['bg2'])
        self.color = make_color(THEME['text'])
        self.background_normal = ''
        self.font_size = sp(13)


# ─── BAR CHART ───
class BarChart(Widget):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.size_hint_y = None
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.clear()
        if not self.data:
            return
        max_val = max((d['total'] for d in self.data), default=1) or 1
        w = self.width
        h = self.height
        n = len(self.data)
        bar_w = (w - dp(4) * (n + 1)) / n
        with self.canvas:
            for i, d in enumerate(self.data):
                bar_h = max(dp(3), (d['total'] / max_val) * (h - dp(18)))
                x = self.x + dp(4) + i * (bar_w + dp(4))
                y = self.y + dp(16)
                Color(*make_color(THEME['accent']), 0.8)
                RoundedRectangle(
                    pos=(x, y), size=(bar_w, bar_h),
                    radius=[dp(3), dp(3), 0, 0]
                )
                Color(*make_color(THEME['text2']))
                lbl = d.get('label', weekday_fa(d['date']))[:3]


# ─── PRODUCT ROW ───
class ProductRow(BoxLayout):
    def __init__(self, product, on_edit=None, on_delete=None, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None, height=dp(68),
            padding=[dp(12), dp(8)],
            spacing=dp(8),
            **kwargs
        )
        self.product = product
        with self.canvas.before:
            Color(*make_color(THEME['bg3']))
            self._bg = RoundedRectangle(radius=[dp(8)], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        # Info
        info = VBox(spacing=dp(2))
        info.bind(minimum_height=info.setter('height'))
        stock_color = THEME['red'] if product['stock'] <= product['min_stock'] else THEME['green']
        info.add_widget(Label(
            text=product['name'], font_size=sp(13), bold=True,
            color=make_color(THEME['text']), halign='right',
            size_hint_y=None, height=dp(20)
        ))
        info.add_widget(Label(
            text=f"{product.get('category','بدون دسته')} | {num(product['price'])} ت/{product['unit']}",
            font_size=sp(11), color=make_color(THEME['text2']),
            halign='right', size_hint_y=None, height=dp(16)
        ))
        info.add_widget(Label(
            text=f"موجودی: {fa(product['stock'])} {product['unit']}",
            font_size=sp(11), color=make_color(stock_color),
            halign='right', size_hint_y=None, height=dp(16)
        ))
        for lbl in info.children:
            if isinstance(lbl, Label):
                lbl.bind(size=lbl.setter('text_size'))
        self.add_widget(info)

        # Buttons
        btns = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(72), spacing=dp(4))
        edit_btn = IconButton('✏️')
        del_btn = IconButton('🗑️', bg_color=THEME['red'])
        if on_edit:
            edit_btn.bind(on_release=lambda *a: on_edit(product['id']))
        if on_delete:
            del_btn.bind(on_release=lambda *a: on_delete(product['id']))
        btns.add_widget(edit_btn)
        btns.add_widget(del_btn)
        self.add_widget(btns)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size


# ─── CUSTOMER ROW ───
class CustomerRow(BoxLayout):
    def __init__(self, customer, inv_count=0, inv_total=0, on_delete=None, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None, height=dp(68),
            padding=[dp(12), dp(8)], spacing=dp(8),
            **kwargs
        )
        with self.canvas.before:
            Color(*make_color(THEME['bg3']))
            self._bg = RoundedRectangle(radius=[dp(8)], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        info = VBox(spacing=dp(2))
        info.add_widget(Label(
            text=customer['name'], font_size=sp(13), bold=True,
            color=make_color(THEME['text']), halign='right',
            size_hint_y=None, height=dp(20)
        ))
        info.add_widget(Label(
            text=customer.get('phone') or 'بدون تلفن',
            font_size=sp(11), color=make_color(THEME['text2']),
            halign='right', size_hint_y=None, height=dp(16)
        ))
        info.add_widget(Label(
            text=f"{fa(inv_count)} فاکتور | {num(inv_total)} ت",
            font_size=sp(11), color=make_color(THEME['accent']),
            halign='right', size_hint_y=None, height=dp(16)
        ))
        for lbl in info.children:
            if isinstance(lbl, Label):
                lbl.bind(size=lbl.setter('text_size'))
        self.add_widget(info)

        del_btn = IconButton('🗑️', bg_color=THEME['red'])
        del_btn.size_hint_x = None
        if on_delete:
            del_btn.bind(on_release=lambda *a: on_delete(customer['id']))
        self.add_widget(del_btn)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size


# ─── POPUP BASE ───
from kivy.uix.popup import Popup


def make_popup(title, content, size=None):
    size = size or (dp(380), dp(500))
    pop = Popup(
        title=title,
        content=content,
        size_hint=(None, None),
        size=size,
        background='',
        background_color=make_color(THEME['bg2']),
        title_color=make_color(THEME['text']),
        title_size=sp(15),
        separator_color=make_color(THEME['border']),
    )
    return pop


# ─── CONFIRM POPUP ───
class ConfirmPopup(BoxLayout):
    def __init__(self, message, on_confirm, popup_ref, **kwargs):
        super().__init__(
            orientation='vertical', spacing=dp(16), padding=dp(16), **kwargs
        )
        self.add_widget(Label(
            text=message, font_size=sp(14),
            color=make_color(THEME['text']),
            halign='center', valign='middle',
        ))
        row = HBox(spacing=dp(8), size_hint_y=None, height=dp(46))
        yes = RoundedButton('بله، حذف شود', bg_color=THEME['red'])
        no = RoundedButton('انصراف', bg_color=THEME['bg3'])
        yes.bind(on_release=lambda *a: (popup_ref.dismiss(), on_confirm()))
        no.bind(on_release=lambda *a: popup_ref.dismiss())
        row.add_widget(yes)
        row.add_widget(no)
        self.add_widget(row)
