"""
نرم‌افزار حسابداری فروشگاهی
Shop Accounting App - Kivy/Python Android APK
"""

import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.metrics import dp

# ─── Window size for desktop testing ───
if platform not in ('android', 'ios'):
    Window.size = (400, 750)
    Window.minimum_width = 360
    Window.minimum_height = 600

from kivy.lang import Builder
from screens.dashboard import DashboardScreen
from screens.invoice  import InvoiceScreen
from screens.products import ProductsScreen
from screens.customers import CustomersScreen
from screens.reports  import ReportsScreen
from screens.invoice_view import InvoiceViewScreen
from utils.database  import Database
from utils.theme     import THEME

# ─── Load all KV files ───
import glob
for kv_file in glob.glob(os.path.join(os.path.dirname(__file__), 'screens', '*.kv')):
    Builder.load_file(kv_file)


class ShopAccountingApp(App):
    title = 'حسابداری فروشگاهی'
    db: Database = None

    def build(self):
        self.db = Database()
        self.db.init_db()

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(DashboardScreen(self.db, name='dashboard'))
        sm.add_widget(InvoiceScreen(self.db, name='invoice'))
        sm.add_widget(ProductsScreen(self.db, name='products'))
        sm.add_widget(CustomersScreen(self.db, name='customers'))
        sm.add_widget(ReportsScreen(self.db, name='reports'))
        sm.add_widget(InvoiceViewScreen(self.db, name='invoice_view'))
        return sm

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    ShopAccountingApp().run()
