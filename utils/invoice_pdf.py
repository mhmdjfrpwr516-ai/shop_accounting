"""
utils/invoice_pdf.py
Invoice preview popup + PDF generation
"""

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.utils import platform
from datetime import datetime

from utils.theme import THEME, num, fa
from utils.widgets import (Card, RoundedButton, Spacer, VBox, HBox,
                            make_color, make_popup, SectionTitle)


class InvoicePreviewPopup:
    def __init__(self, data, db, on_save=None):
        self.data = data
        self.db = db
        self.on_save = on_save
        self._popup = None

    def open(self):
        body = VBox(padding=dp(14), spacing=dp(10))

        # Invoice header
        shop_name = self.db.get_setting('shop_name', 'فروشگاه من')
        shop_phone = self.db.get_setting('shop_phone', '')
        shop_addr = self.db.get_setting('shop_address', '')

        header_card = Card()
        header_card.add_widget(Label(
            text=f"🏪 {shop_name}", font_size=sp(18), bold=True,
            color=make_color(THEME['accent']),
            halign='center', size_hint_y=None, height=dp(30)
        ))
        inv_num = self.data.get('number', 1)
        dt = datetime.now().strftime('%Y/%m/%d  %H:%M')
        header_card.add_widget(Label(
            text=f"فاکتور شماره: #{fa(str(inv_num).zfill(3))}",
            font_size=sp(13), color=make_color(THEME['text']),
            halign='center', size_hint_y=None, height=dp(22)
        ))
        header_card.add_widget(Label(
            text=f"تاریخ: {dt}",
            font_size=sp(12), color=make_color(THEME['text2']),
            halign='center', size_hint_y=None, height=dp(20)
        ))
        if self.data.get('customer_name') and self.data['customer_name'] != 'مشتری آزاد':
            header_card.add_widget(Label(
                text=f"مشتری: {self.data['customer_name']}",
                font_size=sp(12), color=make_color(THEME['text']),
                halign='center', size_hint_y=None, height=dp(20)
            ))
        if shop_phone:
            header_card.add_widget(Label(
                text=f"تلفن: {shop_phone}",
                font_size=sp(11), color=make_color(THEME['text2']),
                halign='center', size_hint_y=None, height=dp(18)
            ))
        body.add_widget(header_card)

        # Items
        items_card = Card(padding=dp(8))
        # Header
        h = HBox(size_hint_y=None, height=dp(26))
        for t, w in [('کالا', 1), ('تعداد', dp(55)), ('قیمت', dp(75)), ('جمع', dp(75))]:
            kw = {'size_hint_x': 1} if w == 1 else {'size_hint_x': None, 'width': w}
            lbl = Label(text=t, font_size=sp(10), bold=True,
                        color=make_color(THEME['text2']), halign='center', **kw)
            lbl.bind(size=lbl.setter('text_size'))
            h.add_widget(lbl)
        items_card.add_widget(h)

        for item in self.data['items']:
            row = HBox(size_hint_y=None, height=dp(32))
            n = Label(text=item['name'], font_size=sp(11), color=make_color(THEME['text']),
                      halign='right', size_hint_x=1)
            n.bind(size=n.setter('text_size'))
            row.add_widget(n)
            row.add_widget(Label(text=f"{fa(item['qty'])}{item['unit']}", font_size=sp(10),
                                 color=make_color(THEME['text']), size_hint_x=None, width=dp(55), halign='center'))
            row.add_widget(Label(text=num(item['price']), font_size=sp(10),
                                 color=make_color(THEME['text']), size_hint_x=None, width=dp(75), halign='center'))
            row.add_widget(Label(text=num(item['total']), font_size=sp(10),
                                 color=make_color(THEME['green']), size_hint_x=None, width=dp(75), halign='center'))
            items_card.add_widget(row)
        body.add_widget(items_card)

        # Totals
        totals_card = Card()
        totals = [('جمع:', num(self.data['subtotal']) + ' ت', THEME['text'])]
        if self.data.get('discount_pct', 0) > 0:
            totals.append((f"تخفیف {fa(int(self.data['discount_pct']))}٪:", '- ' + num(self.data['discount_amt']) + ' ت', THEME['red']))
        if self.data.get('tax_pct', 0) > 0:
            totals.append((f"مالیات {fa(int(self.data['tax_pct']))}٪:", num(self.data['tax_amt']) + ' ت', THEME['amber']))
        totals.append(('مبلغ نهایی:', num(self.data['grand_total']) + ' تومان', THEME['accent']))
        for label, value, color in totals:
            row = HBox(size_hint_y=None, height=dp(28))
            row.add_widget(Label(text=label, font_size=sp(12), color=make_color(THEME['text2']), halign='right'))
            row.add_widget(Label(text=value, font_size=sp(13 if 'نهایی' in label else 12),
                                 bold=('نهایی' in label), color=make_color(color), halign='left'))
            for l in row.children:
                l.bind(size=l.setter('text_size'))
            totals_card.add_widget(row)
        body.add_widget(totals_card)

        # Footer
        body.add_widget(Label(
            text='با تشکر از خرید شما 🙏', font_size=sp(12),
            color=make_color(THEME['text2']),
            halign='center', size_hint_y=None, height=dp(26)
        ))

        # Buttons
        btn_row = HBox(size_hint_y=None, height=dp(46), spacing=dp(8))
        pdf_btn = RoundedButton('📄 ذخیره PDF', bg_color=THEME['accent2'])
        pdf_btn.bind(on_release=lambda *a: self._export_pdf())

        save_btn = RoundedButton('💾 ذخیره فاکتور', bg_color=THEME['green'])
        def do_save(*a):
            if self.on_save:
                self.on_save()
            if self._popup:
                self._popup.dismiss()
        save_btn.bind(on_release=do_save)

        btn_row.add_widget(pdf_btn)
        btn_row.add_widget(save_btn)
        body.add_widget(btn_row)
        body.add_widget(Spacer(dp(10)))

        sv = ScrollView()
        sv.add_widget(body)
        self._popup = make_popup('پیش‌نمایش فاکتور', sv, size=(dp(400), dp(580)))
        self._popup.open()

    def _export_pdf(self):
        try:
            self._generate_pdf()
        except ImportError:
            self._show_msg('⚠️ برای PDF لطفاً reportlab را نصب کنید:\npip install reportlab')
        except Exception as e:
            self._show_msg(f'خطا در ذخیره PDF:\n{str(e)}')

    def _generate_pdf(self):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer as RLSpacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # Save path
        if platform == 'android':
            try:
                from android.storage import primary_external_storage_path  # type: ignore
                base = primary_external_storage_path()
            except Exception:
                base = os.path.expanduser('~')
        else:
            base = os.path.expanduser('~')

        inv_num = self.data.get('number', 1)
        filename = f"invoice_{inv_num}.pdf"
        path = os.path.join(base, filename)

        shop_name = self.db.get_setting('shop_name', 'فروشگاه من')
        shop_phone = self.db.get_setting('shop_phone', '')
        dt = datetime.now().strftime('%Y/%m/%d')

        doc = SimpleDocTemplate(path, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []

        # Try to use a Persian-compatible font if available
        try:
            font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'Vazir.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Vazir', font_path))
                base_font = 'Vazir'
            else:
                base_font = 'Helvetica'
        except Exception:
            base_font = 'Helvetica'

        title_style = ParagraphStyle('title', fontName=base_font, fontSize=18,
                                     alignment=1, textColor=colors.HexColor('#1e40af'))
        normal_style = ParagraphStyle('normal', fontName=base_font, fontSize=11,
                                      alignment=2)
        small_style = ParagraphStyle('small', fontName=base_font, fontSize=9,
                                     alignment=2, textColor=colors.grey)

        story.append(Paragraph(shop_name, title_style))
        story.append(RLSpacer(1, 0.3*cm))
        story.append(Paragraph(f"Invoice #{inv_num} | {dt}", normal_style))
        story.append(Paragraph(f"Customer: {self.data.get('customer_name', 'Guest')}", normal_style))
        if shop_phone:
            story.append(Paragraph(f"Phone: {shop_phone}", small_style))
        story.append(RLSpacer(1, 0.5*cm))

        # Items table
        table_data = [['#', 'Item', 'Qty', 'Unit Price', 'Total']]
        for i, item in enumerate(self.data['items'], 1):
            table_data.append([
                str(i), item['name'],
                f"{item['qty']} {item['unit']}",
                f"{int(item['price']):,}",
                f"{int(item['total']):,}"
            ])

        tbl = Table(table_data, colWidths=[1*cm, 6*cm, 2.5*cm, 3*cm, 3*cm])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), base_font),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(tbl)
        story.append(RLSpacer(1, 0.3*cm))

        # Totals
        totals_data = [[f"Subtotal:", f"{int(self.data['subtotal']):,} Toman"]]
        if self.data.get('discount_pct', 0) > 0:
            totals_data.append([f"Discount {self.data['discount_pct']}%:", f"-{int(self.data['discount_amt']):,}"])
        if self.data.get('tax_pct', 0) > 0:
            totals_data.append([f"Tax {self.data['tax_pct']}%:", f"+{int(self.data['tax_amt']):,}"])
        totals_data.append(["TOTAL:", f"{int(self.data['grand_total']):,} Toman"])

        t2 = Table(totals_data, colWidths=[10*cm, 4*cm])
        t2.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), base_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), base_font),
            ('FONTSIZE', (0, -1), (-1, -1), 13),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1e40af')),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1e40af')),
        ]))
        story.append(t2)
        story.append(RLSpacer(1, 0.5*cm))
        story.append(Paragraph('Thank you for your purchase!', small_style))

        doc.build(story)
        self._show_msg(f'✅ PDF ذخیره شد:\n{path}')

    def _show_msg(self, msg):
        content = VBox(padding=dp(16), spacing=dp(12))
        content.add_widget(Label(
            text=msg, font_size=sp(12),
            color=make_color(THEME['text']),
            halign='center', size_hint_y=None, height=dp(60)
        ))
        ok = RoundedButton('باشه')
        content.add_widget(ok)
        pop = make_popup('نتیجه', content, size=(dp(340), dp(180)))
        ok.bind(on_release=lambda *a: pop.dismiss())
        pop.open()
