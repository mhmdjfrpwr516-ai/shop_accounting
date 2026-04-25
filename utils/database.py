"""
utils/database.py
SQLite database manager for shop accounting
"""

import sqlite3
import os
import json
from datetime import datetime
from kivy.utils import platform


def get_db_path():
    if platform == 'android':
        from android.storage import app_storage_path  # type: ignore
        return os.path.join(app_storage_path(), 'shop_accounting.db')
    return os.path.join(os.path.expanduser('~'), 'shop_accounting.db')


class Database:
    def __init__(self):
        self.db_path = get_db_path()
        self._conn = None

    def get_conn(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def init_db(self):
        conn = self.get_conn()
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL DEFAULT 0,
            stock REAL DEFAULT 0,
            category TEXT DEFAULT '',
            unit TEXT DEFAULT 'عدد',
            min_stock REAL DEFAULT 5,
            barcode TEXT DEFAULT '',
            created_at INTEGER DEFAULT (strftime('%s','now'))
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            address TEXT DEFAULT '',
            national_id TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at INTEGER DEFAULT (strftime('%s','now'))
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER NOT NULL,
            customer_id INTEGER,
            customer_name TEXT DEFAULT 'مشتری آزاد',
            customer_phone TEXT DEFAULT '',
            subtotal REAL DEFAULT 0,
            discount_pct REAL DEFAULT 0,
            discount_amt REAL DEFAULT 0,
            tax_pct REAL DEFAULT 9,
            tax_amt REAL DEFAULT 0,
            grand_total REAL DEFAULT 0,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'paid',
            items_json TEXT DEFAULT '[]',
            created_at INTEGER DEFAULT (strftime('%s','now')),
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')

        # Default settings
        defaults = [
            ('shop_name', 'فروشگاه من'),
            ('shop_address', ''),
            ('shop_phone', ''),
            ('inv_counter', '1'),
            ('default_tax', '9'),
        ]
        for k, v in defaults:
            c.execute("INSERT OR IGNORE INTO settings VALUES (?,?)", (k, v))

        conn.commit()
        self._seed_demo(c, conn)

    def _seed_demo(self, c, conn):
        c.execute("SELECT COUNT(*) FROM products")
        if c.fetchone()[0] > 0:
            return
        products = [
            ('نان لواش', 5000, 50, 'نانوایی', 'عدد', 10, ''),
            ('شیر پاستوریزه ۱ لیتر', 28000, 30, 'لبنیات', 'عدد', 5, ''),
            ('روغن آفتابگردان', 120000, 15, 'روغن', 'لیتر', 3, ''),
            ('برنج ایرانی', 85000, 8, 'برنج', 'کیلوگرم', 10, ''),
            ('پنیر لیقوان', 95000, 4, 'لبنیات', 'کیلوگرم', 5, ''),
            ('چای احمد ۵۰۰g', 65000, 20, 'چای', 'بسته', 5, ''),
        ]
        c.executemany(
            "INSERT INTO products (name,price,stock,category,unit,min_stock,barcode) VALUES (?,?,?,?,?,?,?)",
            products
        )
        customers = [
            ('محمد رضایی', '09121234567', 'تهران، ولیعصر', ''),
            ('فاطمه احمدی', '09351234567', 'تهران، شهرک غرب', ''),
            ('علی محمدی', '09131234567', 'تهران، نارمک', ''),
        ]
        c.executemany(
            "INSERT INTO customers (name,phone,address,national_id) VALUES (?,?,?,?)",
            customers
        )
        conn.commit()

    # ─── SETTINGS ───
    def get_setting(self, key, default=''):
        c = self.get_conn().cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = c.fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        self.get_conn().execute(
            "INSERT OR REPLACE INTO settings VALUES (?,?)", (key, str(value))
        )
        self.get_conn().commit()

    # ─── PRODUCTS ───
    def get_products(self, search=''):
        c = self.get_conn().cursor()
        if search:
            c.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ? ORDER BY name",
                      (f'%{search}%', f'%{search}%'))
        else:
            c.execute("SELECT * FROM products ORDER BY name")
        return [dict(r) for r in c.fetchall()]

    def get_product(self, pid):
        c = self.get_conn().cursor()
        c.execute("SELECT * FROM products WHERE id=?", (pid,))
        r = c.fetchone()
        return dict(r) if r else None

    def save_product(self, data, pid=None):
        conn = self.get_conn()
        if pid:
            conn.execute('''UPDATE products SET name=?,price=?,stock=?,category=?,unit=?,min_stock=?,barcode=?
                           WHERE id=?''',
                         (data['name'], data['price'], data['stock'], data['category'],
                          data['unit'], data['min_stock'], data.get('barcode', ''), pid))
        else:
            conn.execute(
                "INSERT INTO products (name,price,stock,category,unit,min_stock,barcode) VALUES (?,?,?,?,?,?,?)",
                (data['name'], data['price'], data['stock'], data['category'],
                 data['unit'], data['min_stock'], data.get('barcode', ''))
            )
        conn.commit()

    def delete_product(self, pid):
        self.get_conn().execute("DELETE FROM products WHERE id=?", (pid,))
        self.get_conn().commit()

    def update_stock(self, pid, qty_change):
        self.get_conn().execute(
            "UPDATE products SET stock = MAX(0, stock + ?) WHERE id=?", (qty_change, pid)
        )
        self.get_conn().commit()

    def get_low_stock(self):
        c = self.get_conn().cursor()
        c.execute("SELECT * FROM products WHERE stock <= min_stock ORDER BY stock")
        return [dict(r) for r in c.fetchall()]

    # ─── CUSTOMERS ───
    def get_customers(self, search=''):
        c = self.get_conn().cursor()
        if search:
            c.execute("SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name",
                      (f'%{search}%', f'%{search}%'))
        else:
            c.execute("SELECT * FROM customers ORDER BY name")
        return [dict(r) for r in c.fetchall()]

    def get_customer(self, cid):
        c = self.get_conn().cursor()
        c.execute("SELECT * FROM customers WHERE id=?", (cid,))
        r = c.fetchone()
        return dict(r) if r else None

    def save_customer(self, data, cid=None):
        conn = self.get_conn()
        if cid:
            conn.execute(
                "UPDATE customers SET name=?,phone=?,address=?,national_id=?,notes=? WHERE id=?",
                (data['name'], data['phone'], data['address'], data['national_id'], data.get('notes', ''), cid)
            )
        else:
            conn.execute(
                "INSERT INTO customers (name,phone,address,national_id,notes) VALUES (?,?,?,?,?)",
                (data['name'], data['phone'], data['address'], data['national_id'], data.get('notes', ''))
            )
        conn.commit()

    def delete_customer(self, cid):
        self.get_conn().execute("DELETE FROM customers WHERE id=?", (cid,))
        self.get_conn().commit()

    # ─── INVOICES ───
    def get_invoices(self, search='', status='all', limit=None):
        c = self.get_conn().cursor()
        sql = "SELECT * FROM invoices WHERE 1=1"
        params = []
        if search:
            sql += " AND (customer_name LIKE ? OR CAST(number AS TEXT) LIKE ?)"
            params += [f'%{search}%', f'%{search}%']
        if status != 'all':
            sql += " AND status=?"
            params.append(status)
        sql += " ORDER BY created_at DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        c.execute(sql, params)
        rows = [dict(r) for r in c.fetchall()]
        for r in rows:
            r['items'] = json.loads(r.get('items_json', '[]'))
        return rows

    def get_invoice(self, inv_id):
        c = self.get_conn().cursor()
        c.execute("SELECT * FROM invoices WHERE id=?", (inv_id,))
        r = c.fetchone()
        if not r:
            return None
        d = dict(r)
        d['items'] = json.loads(d.get('items_json', '[]'))
        return d

    def save_invoice(self, data):
        conn = self.get_conn()
        items_json = json.dumps(data['items'], ensure_ascii=False)
        conn.execute('''INSERT INTO invoices
            (number, customer_id, customer_name, customer_phone,
             subtotal, discount_pct, discount_amt, tax_pct, tax_amt,
             grand_total, description, status, items_json, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                     (data['number'], data.get('customer_id'), data['customer_name'],
                      data.get('customer_phone', ''), data['subtotal'],
                      data['discount_pct'], data['discount_amt'],
                      data['tax_pct'], data['tax_amt'], data['grand_total'],
                      data.get('description', ''), data['status'],
                      items_json, int(datetime.now().timestamp())))
        # Reduce stock
        for item in data['items']:
            conn.execute(
                "UPDATE products SET stock = MAX(0, stock - ?) WHERE id=?",
                (item['qty'], item['pid'])
            )
        conn.commit()
        # Update invoice counter
        self.set_setting('inv_counter', str(data['number'] + 1))

    def delete_invoice(self, inv_id):
        inv = self.get_invoice(inv_id)
        if inv:
            for item in inv['items']:
                self.get_conn().execute(
                    "UPDATE products SET stock = stock + ? WHERE id=?",
                    (item['qty'], item['pid'])
                )
        self.get_conn().execute("DELETE FROM invoices WHERE id=?", (inv_id,))
        self.get_conn().commit()

    def update_invoice_status(self, inv_id, status):
        self.get_conn().execute(
            "UPDATE invoices SET status=? WHERE id=?", (status, inv_id)
        )
        self.get_conn().commit()

    # ─── REPORTS ───
    def get_stats(self):
        c = self.get_conn().cursor()
        today_ts = int(datetime.now().replace(hour=0, minute=0, second=0).timestamp())
        month_ts = int(datetime.now().replace(day=1, hour=0, minute=0, second=0).timestamp())

        c.execute("SELECT COALESCE(SUM(grand_total),0), COUNT(*) FROM invoices WHERE created_at>=?", (today_ts,))
        today_total, today_count = c.fetchone()

        c.execute("SELECT COALESCE(SUM(grand_total),0), COUNT(*) FROM invoices WHERE created_at>=?", (month_ts,))
        month_total, month_count = c.fetchone()

        c.execute("SELECT COALESCE(SUM(grand_total),0), COUNT(*) FROM invoices")
        all_total, all_count = c.fetchone()

        c.execute("SELECT COALESCE(SUM(grand_total),0) FROM invoices WHERE status='pending'")
        pending_total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM products")
        prod_count = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM customers")
        cust_count = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM products WHERE stock <= min_stock")
        low_stock_count = c.fetchone()[0]

        return {
            'today_total': today_total or 0,
            'today_count': today_count or 0,
            'month_total': month_total or 0,
            'month_count': month_count or 0,
            'all_total': all_total or 0,
            'all_count': all_count or 0,
            'pending_total': pending_total or 0,
            'prod_count': prod_count or 0,
            'cust_count': cust_count or 0,
            'low_stock_count': low_stock_count or 0,
        }

    def get_weekly_sales(self):
        c = self.get_conn().cursor()
        result = []
        for i in range(6, -1, -1):
            from datetime import date, timedelta
            d = date.today() - timedelta(days=i)
            ts_start = int(datetime(d.year, d.month, d.day, 0, 0, 0).timestamp())
            ts_end = ts_start + 86400
            c.execute("SELECT COALESCE(SUM(grand_total),0) FROM invoices WHERE created_at>=? AND created_at<?",
                      (ts_start, ts_end))
            total = c.fetchone()[0] or 0
            result.append({'date': d, 'total': total})
        return result

    def get_top_products(self, limit=5):
        invs = self.get_invoices()
        sales = {}
        for inv in invs:
            for item in inv['items']:
                k = item['name']
                if k not in sales:
                    sales[k] = {'qty': 0, 'total': 0}
                sales[k]['qty'] += item['qty']
                sales[k]['total'] += item['total']
        return sorted(sales.items(), key=lambda x: x[1]['total'], reverse=True)[:limit]

    def get_top_customers(self, limit=5):
        c = self.get_conn().cursor()
        c.execute('''SELECT customer_name, COUNT(*) as cnt, SUM(grand_total) as total
                     FROM invoices GROUP BY customer_name ORDER BY total DESC LIMIT ?''', (limit,))
        return [dict(r) for r in c.fetchall()]

    def export_json(self):
        return json.dumps({
            'products': self.get_products(),
            'customers': self.get_customers(),
            'invoices': self.get_invoices(),
        }, ensure_ascii=False, indent=2)

    def export_csv_invoices(self):
        invs = self.get_invoices()
        lines = ['شماره,تاریخ,مشتری,تلفن,مبلغ کل,وضعیت']
        for inv in invs:
            dt = datetime.fromtimestamp(inv['created_at']).strftime('%Y-%m-%d')
            status = 'پرداخت شده' if inv['status'] == 'paid' else 'در انتظار'
            lines.append(f"{inv['number']},{dt},{inv['customer_name']},{inv.get('customer_phone','')},{int(inv['grand_total'])},{status}")
        return '\n'.join(lines)
