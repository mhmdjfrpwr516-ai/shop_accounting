"""
utils/theme.py
Colors, fonts, and helper functions
"""

THEME = {
    'bg':       '#0f1117',
    'bg2':      '#1a1d27',
    'bg3':      '#22263a',
    'card':     '#1e2235',
    'accent':   '#4f8ef7',
    'accent2':  '#7c3aed',
    'green':    '#10b981',
    'red':      '#ef4444',
    'amber':    '#f59e0b',
    'text':     '#f1f5f9',
    'text2':    '#94a3b8',
    'border':   '#2a2d40',
    'white':    '#ffffff',
}

PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def fa(n):
    """Convert number to Persian digits string"""
    return str(n).translate(PERSIAN_DIGITS)


def num(n):
    """Format number with thousands separator + Persian digits"""
    try:
        n = int(round(float(n)))
        formatted = f"{n:,}"
        return formatted.translate(PERSIAN_DIGITS)
    except Exception:
        return '۰'


def persian_date(ts=None):
    """Return Jalali-like date string (simplified using Gregorian for APK compatibility)"""
    from datetime import datetime
    try:
        import jdatetime  # type: ignore
        if ts:
            dt = datetime.fromtimestamp(ts)
        else:
            dt = datetime.now()
        jd = jdatetime.datetime.fromgregorian(datetime=dt)
        return jd.strftime('%Y/%m/%d')
    except ImportError:
        from datetime import datetime
        if ts:
            dt = datetime.fromtimestamp(ts)
        else:
            dt = datetime.now()
        return dt.strftime('%Y/%m/%d')


def short_date(ts):
    from datetime import datetime
    return datetime.fromtimestamp(ts).strftime('%m/%d')


def weekday_fa(d):
    days = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه']
    return days[d.weekday()]
