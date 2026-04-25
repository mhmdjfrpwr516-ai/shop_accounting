"""
screens/base.py
Base screen with bottom navigation bar
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp, sp
from utils.theme import THEME
from kivy.utils import get_color_from_hex as hex_c


def make_color(h):
    return hex_c(h)


NAV_ITEMS = [
    ('dashboard',  '📊', 'داشبورد'),
    ('invoice',    '🧾', 'فاکتور'),
    ('products',   '📦', 'کالا'),
    ('customers',  '👥', 'مشتریان'),
    ('reports',    '📈', 'گزارش'),
]


class NavBar(BoxLayout):
    def __init__(self, current, on_nav, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.current = current
        self.on_nav = on_nav
        self._buttons = {}
        self._draw_bg()
        self._build()

    def _draw_bg(self):
        with self.canvas.before:
            Color(*make_color(THEME['bg2']))
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _build(self):
        self.clear_widgets()
        self._buttons = {}
        for screen_name, icon, label in NAV_ITEMS:
            active = (screen_name == self.current)
            col = THEME['accent'] if active else THEME['text2']
            btn = Button(
                text=f"{icon}\n{label}",
                font_name='Vazir' if self._has_vazir() else '',
                font_size=sp(9),
                color=make_color(col),
                background_color=(0, 0, 0, 0),
                background_normal='',
                halign='center',
                valign='middle',
                markup=False,
            )
            btn.bind(on_release=lambda b, sn=screen_name: self.on_nav(sn))
            self._buttons[screen_name] = btn
            self.add_widget(btn)

    def _has_vazir(self):
        try:
            from kivy.core.text import LabelBase
            return 'Vazir' in LabelBase._fonts
        except Exception:
            return False

    def update_active(self, screen_name):
        self.current = screen_name
        self._build()


class BaseScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self._root_layout = FloatLayout()
        self.add_widget(self._root_layout)

        # Main content area
        self._main = BoxLayout(
            orientation='vertical',
            pos_hint={'x': 0, 'y': 0},
            size_hint=(1, 1),
        )
        with self._main.canvas.before:
            Color(*make_color(THEME['bg']))
            self._main_bg = Rectangle(pos=self._main.pos, size=self._main.size)
        self._main.bind(pos=self._upd, size=self._upd)
        self._root_layout.add_widget(self._main)

        # Header
        self._header = self._make_header()
        self._main.add_widget(self._header)

        # Content
        self._content = self._make_content()
        self._main.add_widget(self._content)

        # Bottom nav
        self._navbar = NavBar(self.name, self._go_to)
        self._main.add_widget(self._navbar)

    def _upd(self, *a):
        self._main_bg.pos = self._main.pos
        self._main_bg.size = self._main.size

    def _go_to(self, screen_name):
        self.manager.current = screen_name

    def _make_header(self):
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), dp(8)],
        )
        with header.canvas.before:
            Color(*make_color(THEME['bg2']))
            self._header_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda *a: setattr(self._header_bg, 'pos', header.pos),
                    size=lambda *a: setattr(self._header_bg, 'size', header.size))
        return header

    def _make_content(self):
        from kivy.uix.scrollview import ScrollView
        sv = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        return sv

    def on_enter(self):
        self._navbar.update_active(self.name)
        self.refresh()

    def refresh(self):
        pass


class HeaderLabel(Label):
    def __init__(self, text, **kwargs):
        super().__init__(
            text=text,
            font_size=sp(17),
            bold=True,
            color=make_color(THEME['text']),
            halign='right',
            valign='middle',
            size_hint_x=1,
            **kwargs
        )
        self.bind(size=self.setter('text_size'))
