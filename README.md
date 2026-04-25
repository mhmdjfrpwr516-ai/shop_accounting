# 📱 نرم‌افزار حسابداری فروشگاهی - راهنمای کامل

## ساختار پروژه

```
shop_accounting/
├── main.py                  ← نقطه ورود اصلی
├── buildozer.spec           ← تنظیمات ساخت APK
├── screens/
│   ├── __init__.py
│   ├── base.py              ← صفحه پایه + نوار ناوبری
│   ├── dashboard.py         ← داشبورد
│   ├── invoice.py           ← ثبت فاکتور
│   ├── invoice_view.py      ← مشاهده فاکتور + تاریخچه
│   ├── products.py          ← مدیریت کالا
│   ├── customers.py         ← مدیریت مشتریان
│   └── reports.py           ← گزارشات مالی
├── utils/
│   ├── __init__.py
│   ├── database.py          ← SQLite - تمام عملیات DB
│   ├── theme.py             ← رنگ‌ها و توابع کمکی
│   ├── widgets.py           ← ویجت‌های مشترک
│   └── invoice_pdf.py       ← پیش‌نمایش + تولید PDF
└── assets/
    └── (icon.png, presplash.png, Vazir.ttf)
```

---

## 🖥️ اجرا روی کامپیوتر (تست)

```bash
# ۱. نصب وابستگی‌ها
pip install kivy reportlab jdatetime

# ۲. اجرا
cd shop_accounting
python main.py
```

---

## 📦 ساخت APK برای اندروید

### روش ۱: Ubuntu/Linux (توصیه می‌شود)

```bash
# ۱. نصب پیش‌نیازها
sudo apt update
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk \
    python3-setuptools libssl-dev libffi-dev build-essential \
    libltdl-dev ccache autoconf libtool pkg-config

# ۲. نصب buildozer
pip3 install --upgrade buildozer cython

# ۳. رفتن به دایرکتوری پروژه
cd shop_accounting

# ۴. ساخت APK (دیباگ - برای تست)
buildozer android debug

# ۵. APK در این مسیر قرار می‌گیرد:
# bin/shopaccounting-1.0.0-arm64-v8a-debug.apk
```

### روش ۲: Docker (آسان‌ترین)

```bash
# اجرای buildozer در داکر
docker run --volume "$(pwd)":/home/user/hostcwd \
  kivy/buildozer android debug

# APK در پوشه bin/ ساخته می‌شود
```

### روش ۳: GitHub Actions (خودکار)

فایل `.github/workflows/build.yml` را بسازید:

```yaml
name: Build APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install buildozer cython
          sudo apt-get install -y \
            python3-pip build-essential git \
            libssl-dev libffi-dev \
            openjdk-17-jdk zip unzip
      - name: Build APK
        run: |
          cd shop_accounting
          buildozer android debug
      - uses: actions/upload-artifact@v3
        with:
          name: APK
          path: shop_accounting/bin/*.apk
```

---

## ✨ امکانات کامل

| بخش | امکانات |
|-----|---------|
| 📊 داشبورد | آمار فروش امروز/ماه، نمودار ۷ روزه، هشدار موجودی کم، آخرین فاکتورها |
| 🧾 فاکتور | ثبت فاکتور کامل، انتخاب مشتری، چند کالا، تخفیف٪، مالیات٪، وضعیت پرداخت |
| 👁️ پیش‌نمایش | پیش‌نمایش فاکتور قبل از ذخیره، خروجی PDF |
| 📦 کالا | ثبت/ویرایش/حذف، موجودی انبار، هشدار کمبود، دسته‌بندی، بارکد |
| 👥 مشتریان | ثبت اطلاعات کامل، کد ملی، آمار خرید هر مشتری |
| 📈 گزارش | پرفروش‌ترین کالاها، بهترین مشتریان، خروجی JSON/CSV |
| 🗄️ دیتابیس | SQLite - ذخیره کامل روی دستگاه، بدون نیاز به اینترنت |
| 📄 PDF | تولید فاکتور PDF با reportlab |

---

## 🔧 تنظیمات فروشگاه

برای تغییر نام فروشگاه، تلفن و آدرس در فاکتور:
```python
db.set_setting('shop_name', 'نام فروشگاه شما')
db.set_setting('shop_phone', '02112345678')
db.set_setting('shop_address', 'تهران، ...')
```

یا از طریق صفحه تنظیمات (قابل اضافه شدن).

---

## 📝 نکات مهم

- **فونت فارسی**: فایل `Vazir.ttf` را در `assets/` قرار دهید
- **آیکون**: فایل `icon.png` (512×512) را در `assets/` قرار دهید
- **اولین بار**: نمونه داده‌های demo به صورت خودکار ثبت می‌شوند
- **دیتابیس**: در Android در `app_storage_path()` ذخیره می‌شود
- **PDF**: در اندروید در حافظه خارجی (Downloads) ذخیره می‌شود

---

## 🚀 Release APK (امضا شده)

```bash
# ساخت keystore
keytool -genkey -v -keystore my-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias my-key-alias

# ساخت APK Release
buildozer android release

# امضای APK
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore my-release-key.jks \
  bin/shopaccounting-1.0.0-arm64-v8a-release-unsigned.apk \
  my-key-alias

# بهینه‌سازی
zipalign -v 4 \
  bin/shopaccounting-1.0.0-arm64-v8a-release-unsigned.apk \
  bin/shopaccounting-release.apk
```
