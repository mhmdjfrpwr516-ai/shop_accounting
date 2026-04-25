[app]
# عنوان اپلیکیشن
title = حسابداری فروشگاهی
# نام پکیج (فقط انگلیسی)
package.name = shopaccounting
package.domain = org.shopaccounting

# فایل اصلی
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db,json
source.exclude_dirs = tests, bin, venv, .git, __pycache__

version = 1.0.0

# وابستگی‌ها
requirements = python3,kivy==2.3.0,sqlite3,reportlab,jdatetime

# آیکون و Splash (اختیاری - فایل‌ها را در assets/ قرار دهید)
# icon.filename = %(source.dir)s/assets/icon.png
# presplash.filename = %(source.dir)s/assets/presplash.png

# Android تنظیمات
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.arch = arm64-v8a

# برای دستگاه‌های قدیمی‌تر هم بسازید:
# android.archs = arm64-v8a, armeabi-v7a

android.release_artifact = apk
android.debug_artifact = apk

# فعال‌سازی SDL2
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
