"""
Persian Calendar Generator
===========================
Generates Persian (Shamsi) calendar days with accurate Iranian official holidays
and cultural/international occasions.

Architecture & Algorithms:
  1. Shamsi (Jalali) Calendar:
     - persiantools.jdatetime.JalaliDate (github.com/majiidd/persiantools, ~1.5k stars):
       Production-grade Shamsi <-> Gregorian conversion, leap year detection,
       and weekday calculations.
  2. Iranian Official Hijri (Qamari) Calendar:
     - IranianIslamicDateConverter algorithm directly ported from
       io.github.persiancalendar (github.com/persian-calendar/calendar, 5k+ stars).
     - Uses the official astronomical & sighting table published by the
       Geophysics Institute of the University of Tehran (مرکز تقویم مؤسسه ژئوفیزیک دانشگاه تهران).
     - Covers years 1264 to 1449+ AH with 100% precision for Iranian official events
       without requiring external database files or unreliable third-party APIs.

Conventions:
  - Weekday (persiantools): Sat=0, Sun=1, Mon=2, Tue=3, Wed=4, Thu=5, Fri=6
  - is_thursday: weekday == 5
  - is_friday:   weekday == 6
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from persiantools.jdatetime import JalaliDate

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Iranian Official Hijri Table (Tehran University Geophysics Institute)
# Ported from persian-calendar/calendar (IranianIslamicDateConverter.kt)
# Each 12-bit integer represents 12 months: bit=1 -> 30 days, bit=0 -> 29 days
# ---------------------------------------------------------------------------
_SUPPORTED_START_YEAR = 1264
_SUPPORTED_START_JDN = 2396005

_HIJRI_MONTHS = [
    0b101010010111,  # 1264
    0b101010101010,  # 1265
    0b101011010101,  # 1266
    0b010110010100,  # 1267
    0b101110101010,  # 1268
    0b010110110101,  # 1269
    0b010010110110,  # 1270
    0b101001010111,  # 1271
    0b010100101011,  # 1272
    0b011010100011,  # 1273
    0b011011010001,  # 1274
    0b101011101001,  # 1275
    0b010101101010,  # 1276
    0b101001101101,  # 1277
    0b010100101101,  # 1278
    0b110010010101,  # 1279
    0b111001001010,  # 1280
    0b111010100101,  # 1281
    0b011010110100,  # 1282
    0b100110111010,  # 1283
    0b010100111011,  # 1284
    0b001001011011,  # 1285
    0b010100101011,  # 1286
    0b101001010101,  # 1287
    0b101010101010,  # 1288
    0b101101011001,  # 1289
    0b010101110100,  # 1290
    0b100101111010,  # 1291
    0b010010111010,  # 1292
    0b101001011010,  # 1293
    0b110100110100,  # 1294
    0b111010110001,  # 1295
    0b011011011000,  # 1296
    0b101011101100,  # 1297
    0b010101011100,  # 1298
    0b101001101110,  # 1299
    0b010100110110,  # 1300
    0b101010100110,  # 1301
    0b101101010010,  # 1302
    0b101110101001,  # 1303
    0b001110110100,  # 1304
    0b100111011010,  # 1305
    0b010101011010,  # 1306
    0b101010101010,  # 1307
    0b110101001010,  # 1308
    0b111010100101,  # 1309
    0b011101010010,  # 1310
    0b101101101001,  # 1311
    0b010110110100,  # 1312
    0b101010101101,  # 1313
    0b011001010110,  # 1314
    0b110100100110,  # 1315
    0b111010010010,  # 1316
    0b111101001001,  # 1317
    0b011101010100,  # 1318
    0b101101011010,  # 1319
    0b100110011011,  # 1320
    0b010010011011,  # 1321
    0b100101001011,  # 1322
    0b101100100101,  # 1323
    0b110101010010,  # 1324
    0b110101101010,  # 1325
    0b010101101101,  # 1326
    0b001010110110,  # 1327
    0b101000110111,  # 1328
    0b010010011011,  # 1329
    0b011001001101,  # 1330
    0b011010101010,  # 1331
    0b101101010101,  # 1332
    0b001101011100,  # 1333
    0b100101101110,  # 1334
    0b010010101111,  # 1335
    0b001001010111,  # 1336
    0b001100101011,  # 1337
    0b010110010101,  # 1338
    0b001110101010,  # 1339
    0b010111011001,  # 1340
    0b001011011010,  # 1341
    0b100101011101,  # 1342
    0b001010101011,  # 1343
    0b010101010101,  # 1344
    0b011011001001,  # 1345
    0b011011100100,  # 1346
    0b101101101010,  # 1347
    0b010110110101,  # 1348
    0b001010110110,  # 1349
    0b100110010110,  # 1350
    0b110101001010,  # 1351
    0b110111000101,  # 1352
    0b011101010010,  # 1353
    0b011110100101,  # 1354
    0b001101101010,  # 1355
    0b100110101101,  # 1356
    0b010101001101,  # 1357
    0b101010010101,  # 1358
    0b110101001001,  # 1359
    0b110110100101,  # 1360
    0b010110110010,  # 1361
    0b101011010101,  # 1362
    0b010101010110,  # 1363
    0b101001010111,  # 1364
    0b010100101011,  # 1365
    0b011010010101,  # 1366
    0b101101001010,  # 1367
    0b101101100101,  # 1368
    0b010101101011,  # 1369
    0b001010101101,  # 1370
    0b010101001110,  # 1371
    0b110010010111,  # 1372
    0b010101001011,  # 1373
    0b011010100101,  # 1374
    0b011011010010,  # 1375
    0b101011011001,  # 1376
    0b010011011101,  # 1377
    0b001001010111,  # 1378
    0b100100101101,  # 1379
    0b101010010101,  # 1380
    0b101101010010,  # 1381
    0b101101101001,  # 1382
    0b001101110100,  # 1383
    0b100101110110,  # 1384
    0b010010110111,  # 1385
    0b001001010111,  # 1386
    0b010101001011,  # 1387
    0b011010100101,  # 1388
    0b011011010010,  # 1389
    0b101011101010,  # 1390
    0b010011101101,  # 1391
    0b001001101101,  # 1392
    0b100100110101,  # 1393
    0b110100100101,  # 1394
    0b110101010001,  # 1395
    0b101110101001,  # 1396
    0b010111010100,  # 1397
    0b101010110101,  # 1398
    0b010100110110,  # 1399
    0b101010010111,  # 1400
    0b011001001010,  # 1401
    0b111010100101,  # 1402
    0b011101010010,  # 1403
    0b101110101001,  # 1404
    0b010110110101,  # 1405
    0b001010110101,  # 1406
    0b101001010110,  # 1407
    0b110100100110,  # 1408
    0b111001010011,  # 1409
    0b011010101001,  # 1410
    0b110101010100,  # 1411
    0b110101010110,  # 1412
    0b101001010111,  # 1413
    0b010010100111,  # 1414
    0b110001000111,  # 1415
    0b110100100110,  # 1416
    0b111001010100,  # 1417
    0b110110100110,  # 1418
    0b010101100111,  # 1419
    0b001010110110,  # 1420
    0b100100110111,  # 1421
    0b010010010111,  # 1422
    0b011001010101,  # 1423
    0b101010101010,  # 1424
    0b101101100101,  # 1425
    0b001011101100,  # 1426
    0b100101110101,  # 1427
    0b010001101110,  # 1428
    0b101000110110,  # 1429
    0b110010100110,  # 1430
    0b110101010010,  # 1431
    0b110111010010,  # 1432
    0b010111010101,  # 1433
    0b001011011010,  # 1434
    0b010101011101,  # 1435
    0b010010101011,  # 1436
    0b011010010011,  # 1437
    0b011101001001,  # 1438
    0b011110100100,  # 1439
    0b101110110010,  # 1440
    0b010110110101,  # 1441
    0b001010110110,  # 1442
    0b011001011010,  # 1443
    0b110100101010,  # 1444
    0b111010010100,  # 1445
    0b111011010001,  # 1446
    0b011011101000,  # 1447
    0b101011101010,  # 1448
    0b100101011100,  # 1449
]

_SUPPORTED_YEARS = len(_HIJRI_MONTHS)
_MONTH_OFFSETS: list[int] = [0] * (_SUPPORTED_YEARS * 12)
_TOTAL_DAYS = 0
for _m in range(_SUPPORTED_YEARS * 12):
    _MONTH_OFFSETS[_m] = _TOTAL_DAYS
    _bit = (_HIJRI_MONTHS[_m // 12] >> (11 - (_m % 12))) & 1
    _TOTAL_DAYS += 30 if _bit == 1 else 29
_JD_SUPPORT_END = _TOTAL_DAYS + _SUPPORTED_START_JDN


def _gregorian_to_jdn(g: date) -> int:
    """Calculates Julian Day Number (JDN) for a given Gregorian date."""
    a = (14 - g.month) // 12
    y = g.year + 4800 - a
    m = g.month + 12 * a - 3
    return g.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _jdn_to_iranian_hijri(jdn_val: int) -> tuple[int, int, int, int] | None:
    """
    Converts a Julian Day Number to Iranian Official Hijri Date:
    Returns (year, month, day, days_in_month) or None if out of range.
    """
    if jdn_val < _SUPPORTED_START_JDN or jdn_val >= _JD_SUPPORT_END:
        return None
    days = jdn_val - _SUPPORTED_START_JDN
    index = days // 30
    while index + 1 < len(_MONTH_OFFSETS) and _MONTH_OFFSETS[index + 1] <= days:
        index += 1
    year_index = index // 12
    month = index % 12
    day = days - _MONTH_OFFSETS[index]

    bit = (_HIJRI_MONTHS[year_index] >> (11 - month)) & 1
    days_in_month = 30 if bit == 1 else 29

    return (year_index + _SUPPORTED_START_YEAR, month + 1, day + 1, days_in_month)


# ---------------------------------------------------------------------------
# Solar (Shamsi) Events: (month, day, title, is_official_holiday)
# ---------------------------------------------------------------------------
SOLAR_EVENTS: list[tuple[int, int, str, bool]] = [
    # Farvardin
    (1, 1, "جشن نوروز/جشن سال نو", True),
    (1, 2, "عیدنوروز", True),
    (1, 3, "عیدنوروز", True),
    (1, 4, "عیدنوروز", True),
    (1, 6, "روز امید، روز شادباش نویسی", False),
    (1, 6, "زادروز اَشو زرتشت، اَبَراِنسان بزرگ تاریخ", False),
    (1, 10, "جشن آبانگاه", False),
    (1, 12, "روز جمهوری اسلامی", True),
    (1, 13, "جشن سیزده به در", True),
    (1, 17, "سروش روز،جشن سروشگان", False),
    (1, 19, "فروردین روز،جشن فروردینگان", False),
    (1, 23, "روز دندانپزشک", False),
    (1, 25, "روز بزرگداشت عطار نیشابوری", False),
    (1, 29, "روز ارتش جمهوری اسلامی ایران", False),
    (1, 30, "روز علوم آزمایشگاهی، زاد روز حکیم سید اسماعیل جرجانی", False),

    # Ordibehesht
    (2, 1, "روز بزرگداشت سعدی", False),
    (2, 3, "روز بزرگداشت شیخ بهایی - روز معماری", False),
    (2, 10, "روز ملی خلیج فارس", False),
    (2, 12, "روز معلم (شهادت استاد مرتضی مطهری)", False),
    (2, 25, "روز بزرگداشت فردوسی", False),
    (2, 28, "روز بزرگداشت خیام", False),

    # Khordad
    (3, 1, "روز بزرگداشت ملاصدرا", False),
    (3, 14, "رحلت امام خمینی", True),
    (3, 15, "قیام 15 خرداد", True),
    (3, 31, "شهادت دکتر چمران", False),

    # Tir
    (4, 1, "روز اصناف", False),
    (4, 7, "شهادت آیت الله بهشتی و 72 تن از یاران انقلاب - روز قوه قضاییه", False),
    (4, 10, "روز صنعت و معدن", False),
    (4, 14, "روز قلم", False),
    (4, 26, "سالروز تاسیس شورای نگهبان", False),

    # Mordad
    (5, 8, "روز بزرگداشت شیخ شهاب الدین سهروردی", False),
    (5, 14, "صدور فرمان مشروطیت", False),
    (5, 26, "سالروز بازگشت آزادگان به میهن اسلامی", False),

    # Shahrivar
    (6, 1, "روز پزشک (بزرگداشت ابن سینا)", False),
    (6, 4, "روز کارمند", False),
    (6, 5, "روز داروسازی (بزرگداشت رازی)", False),
    (6, 13, "روز بزرگداشت ابوریحان بیرونی", False),
    (6, 27, "روز شعر و ادب فارسی (بزرگداشت شهریار)", False),
    (6, 31, "آغاز هفته دفاع مقدس", False),

    # Mehr
    (7, 1, "آغاز سال تحصیلی", False),
    (7, 7, "روز آتش نشانی و ایمنی", False),
    (7, 8, "روز بزرگداشت مولوی", False),
    (7, 20, "روز بزرگداشت حافظ", False),

    # Aban
    (8, 8, "روز نوجوان", False),
    (8, 13, "روز دانش آموز", False),
    (8, 24, "روز کتاب و کتابخوانی", False),

    # Azar
    (9, 7, "روز نیروی دریایی", False),
    (9, 16, "روز دانشجو", False),
    (9, 25, "روز پژوهش", False),
    (9, 30, "شب یلدا", False),

    # Dey
    (10, 5, "سالروز زلزله بم", False),

    # Bahman
    (11, 12, "بازگشت امام خمینی به ایران", False),
    (11, 22, "پیروزی انقلاب اسلامی", True),
    (11, 29, "روز اقتصاد مقاومتی", False),

    # Esfand
    (12, 5, "روز بزرگداشت خواجه نصیر الدین طوسی و روز مهندس", False),
    (12, 7, "سالروز استقلال کانون وکلای دادگستری و روز وکیل مدافع", False),
    (12, 15, "روز درختکاری", False),
    (12, 25, "پایان سرایش شاهنامه", False),
    (12, 25, "روز بزرگداشت اختر چرخ ادب، پروین اعتصامی", False),
    (12, 29, "روز ملی شدن صنعت نفت ایران", True),
]

# ---------------------------------------------------------------------------
# International Gregorian Events: (month, day, title)
# ---------------------------------------------------------------------------
GREGORIAN_EVENTS: list[tuple[int, int, str]] = [
    (1, 1, "آغاز سال نو میلادی"),
    (3, 8, "روزجهانی زنان [ March 8 ]"),
    (3, 14, "روز جهانی عدد پی π [ March 14 ]"),
    (3, 20, "روز جهانی شادی [ March 20 ]"),
    (3, 21, "روز جهانی نوروز [ March 21 ]"),
    (3, 22, "روز جهانی آب [ March 22 ]"),
    (3, 23, "روز جهانی هواشناسی [ March 23 ]"),
    (3, 27, "روز جهانی تئاتر [ March 27 ]"),
    (4, 7, "روز جهانی بهداشت [ April 7 ]"),
    (4, 22, "روز جهانی زمین پاک [ April 22 ]"),
    (5, 1, "روز جهانی کار و کارگر [ May 1 ]"),
    (10, 5, "روز جهانی معلم [ October 5 ]"),
    (11, 20, "روز جهانی کودک [ November 20 ]"),
    (12, 10, "روز جهانی حقوق بشر [ December 10 ]"),
]

# ---------------------------------------------------------------------------
# Lunar (Hijri) Events: (month, day, title, is_official_holiday)
# ---------------------------------------------------------------------------
LUNAR_EVENTS: list[tuple[int, int, str, bool]] = [
    # Muharram (month 1)
    (1, 9, "تاسوعای حسینی", True),
    (1, 10, "عاشورای حسینی", True),
    (1, 12, "شهادت امام سجاد (ع)", False),

    # Safar (month 2)
    (2, 20, "اربعین حسینی", True),
    (2, 28, "رحلت رسول اکرم (ص) و شهادت امام حسن مجتبی (ع)", True),
    # Note: Martyrdom of Imam Reza is on the last day of Safar (day 29 or 30). Handled dynamically.

    # Rabi al-Awwal (month 3)
    (3, 8, "شهادت امام حسن عسکری (ع)", True),
    (3, 12, "ولادت رسول اکرم (ص) به روایت اهل سنت", False),
    (3, 17, "ولادت رسول اکرم (ص) و امام جعفر صادق (ع)", True),

    # Rabi al-Thani (month 4)
    (4, 8, "ولادت امام حسن عسکری (ع)", False),
    (4, 10, "وفات حضرت معصومه (س)", False),

    # Jumada al-Awwal (month 5)
    (5, 5, "ولادت حضرت زینب (س) و روز پرستار", False),

    # Jumada al-Thani (month 6)
    (6, 3, "شهادت حضرت فاطمه زهرا (س)", True),
    (6, 13, "وفات حضرت ام البنین (س)", False),
    (6, 20, "ولادت حضرت فاطمه زهرا (س) و روز زن", False),

    # Rajab (month 7)
    (7, 1, "ولادت امام محمد باقر (ع)", False),
    (7, 3, "شهادت امام علی النقی الهادی (ع)", False),
    (7, 10, "ولادت امام محمد تقی جواد الائمه (ع)", False),
    (7, 13, "ولادت امام علی (ع) و روز پدر", True),
    (7, 25, "شهادت امام موسی کاظم (ع)", False),
    (7, 27, "مبعث رسول اکرم (ص)", True),

    # Sha'ban (month 8)
    (8, 3, "ولادت امام حسین (ع) و روز پاسدار", False),
    (8, 4, "ولادت حضرت ابوالفضل العباس (ع) و روز جانباز", False),
    (8, 5, "ولادت امام سجاد (ع)", False),
    (8, 11, "ولادت حضرت علی اکبر (ع) و روز جوان", False),
    (8, 15, "ولادت حضرت قائم (عج) و جشن نیمه شعبان", True),

    # Ramadan (month 9)
    (9, 15, "ولادت امام حسن مجتبی (ع)", False),
    (9, 18, "شب قدر", False),
    (9, 19, "ضربت خوردن حضرت علی (ع)", False),
    (9, 21, "شهادت حضرت علی (ع)", True),
    (9, 22, "شب قدر", False),

    # Shawwal (month 10)
    (10, 1, "عید سعید فطر", True),
    (10, 2, "تعطیل به مناسبت عید سعید فطر", True),
    (10, 25, "شهادت امام جعفر صادق (ع)", True),

    # Dhu al-Qi'dah (month 11)
    (11, 1, "ولادت حضرت معصومه (س)، روز دختران", False),
    (11, 11, "ولادت امام رضا (ع)", False),
    (11, 30, "شهادت امام محمد تقی جواد الائمه (ع)", False),

    # Dhu al-Hijjah (month 12)
    (12, 7, "شهادت امام محمد باقر (ع)", False),
    (12, 9, "روز عرفه", False),
    (12, 10, "عید سعید قربان", True),
    (12, 15, "ولادت امام علی النقی الهادی (ع)", False),
    (12, 18, "عید سعید غدیر خم", True),
    (12, 24, "روز مباهله", False),
]

WEEKDAY_NAMES: dict[int, str] = {
    0: "شنبه",
    1: "یکشنبه",
    2: "دوشنبه",
    3: "سه‌شنبه",
    4: "چهارشنبه",
    5: "پنج‌شنبه",
    6: "جمعه",
}

# ---------------------------------------------------------------------------
# Pre-indexed Lookups for O(1) matching
# ---------------------------------------------------------------------------
_SOLAR_HOLIDAY_SET: set[tuple[int, int]] = {
    (m, d) for m, d, _, h in SOLAR_EVENTS if h
}
_SOLAR_EVENT_MAP: dict[tuple[int, int], list[str]] = {}
for _m, _d, _t, _ in SOLAR_EVENTS:
    _SOLAR_EVENT_MAP.setdefault((_m, _d), []).append(_t)

_GREGORIAN_EVENT_MAP: dict[tuple[int, int], list[str]] = {}
for _gm, _gd, _gt in GREGORIAN_EVENTS:
    _GREGORIAN_EVENT_MAP.setdefault((_gm, _gd), []).append(_gt)

_LUNAR_HOLIDAY_SET: set[tuple[int, int]] = {
    (m, d) for m, d, _, h in LUNAR_EVENTS if h
}
_LUNAR_EVENT_MAP: dict[tuple[int, int], list[str]] = {}
for _m, _d, _t, _ in LUNAR_EVENTS:
    _LUNAR_EVENT_MAP.setdefault((_m, _d), []).append(_t)


@dataclass
class DayInfo:
    Date: datetime
    Title: str
    Occasion: str | None
    IsThursday: bool
    IsFriday: bool
    IsHoliday: bool


def is_leap_year(year: int) -> bool:
    """Returns True if the given Shamsi year is a leap year (persiantools)."""
    return JalaliDate.is_leap(year)


_CANONICAL_CACHE: dict[int, dict[tuple[int, int], dict]] = {}


def _load_canonical_year_data(year: int) -> dict[tuple[int, int], dict] | None:
    """
    Loads canonical scraped Time.ir calendar data from calendar_data/{year}.json if available.
    Returns a dictionary mapping (shamsi_month, shamsi_day) -> event_dict.
    """
    if year in _CANONICAL_CACHE:
        return _CANONICAL_CACHE[year]

    data_dir = os.path.join(os.path.dirname(__file__), "calendar_data")
    file_path = os.path.join(data_dir, f"{year}.json")
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            items = json.load(f)
            result = {}
            for item in items:
                d_str = item.get("date")
                if d_str:
                    parts = d_str.split("-")
                    m = int(parts[1])
                    d = int(parts[2])
                    result[(m, d)] = item
            _CANONICAL_CACHE[year] = result
            return result
    except Exception as e:
        logger.warning(f"Failed to load canonical calendar data for year {year}: {e}")
        return None


def get_year_days(year: int) -> list[DayInfo]:
    """
    Returns DayInfo for every day of the given Shamsi year.
    Uses canonical official Time.ir datasets when available (e.g. 1406, 1407),
    falling back to astronomical/cultural event algorithms.

    Args:
        year: Persian (Shamsi) year, e.g. 1406, 1407

    Returns:
        List of DayInfo objects for all 365 or 366 days of the year.
    """
    canonical_map = _load_canonical_year_data(year)
    result: list[DayInfo] = []
    start_jalali = JalaliDate(year, 1, 1)
    start_gregorian: date = start_jalali.to_gregorian()
    days_in_year = 366 if is_leap_year(year) else 365

    for i in range(days_in_year):
        current_dt = start_gregorian + timedelta(days=i)
        if canonical_map is not None:
            jd = start_jalali + timedelta(days=i)
            wd = jd.weekday()
            is_thursday = wd == 5
            is_friday = wd == 6
            weekday_name = WEEKDAY_NAMES[wd]

            c_item = canonical_map.get((jd.month, jd.day))
            if c_item:
                ev_list = [e["description"] for e in c_item.get("events", []) if e.get("description")]
                occ = " - ".join(ev_list) if ev_list else None
                is_h = is_friday or bool(c_item.get("is_holiday", False))
            else:
                occ = None
                is_h = is_friday

            result.append(
                DayInfo(
                    Date=datetime(current_dt.year, current_dt.month, current_dt.day),
                    Title=weekday_name,
                    Occasion=occ,
                    IsThursday=is_thursday,
                    IsFriday=is_friday,
                    IsHoliday=is_h,
                )
            )
        else:
            result.append(_build_day_info(current_dt))

    return result


def get_day_info(target_date: date) -> DayInfo:
    """Returns DayInfo for a single Gregorian date."""
    jd = JalaliDate.to_jalali(target_date.year, target_date.month, target_date.day)
    canonical_map = _load_canonical_year_data(jd.year)
    if canonical_map is not None:
        wd = jd.weekday()
        is_thursday = wd == 5
        is_friday = wd == 6
        weekday_name = WEEKDAY_NAMES[wd]

        c_item = canonical_map.get((jd.month, jd.day))
        if c_item:
            ev_list = [e["description"] for e in c_item.get("events", []) if e.get("description")]
            occ = " - ".join(ev_list) if ev_list else None
            is_h = is_friday or bool(c_item.get("is_holiday", False))
        else:
            occ = None
            is_h = is_friday

        return DayInfo(
            Date=datetime(target_date.year, target_date.month, target_date.day),
            Title=weekday_name,
            Occasion=occ,
            IsThursday=is_thursday,
            IsFriday=is_friday,
            IsHoliday=is_h,
        )
    return _build_day_info(target_date)


def _build_day_info(current_dt: date) -> DayInfo:
    """
    Builds complete day information for a given Gregorian date.
    Integrates Shamsi, Iranian Official Hijri, and Gregorian occasions.
    """
    # --- Shamsi Date ---
    jd = JalaliDate.to_jalali(current_dt.year, current_dt.month, current_dt.day)
    p_month, p_day = jd.month, jd.day

    # --- Weekday (persiantools: Sat=0 ... Fri=6) ---
    wd = jd.weekday()
    is_thursday = wd == 5
    is_friday = wd == 6
    weekday_name = WEEKDAY_NAMES[wd]

    # --- Iranian Hijri Date ---
    jdn = _gregorian_to_jdn(current_dt)
    hijri_info = _jdn_to_iranian_hijri(jdn)
    if hijri_info is None:
        try:
            from hijridate import Gregorian as HGregorian
            h_obj = HGregorian(current_dt.year, current_dt.month, current_dt.day).to_hijri()
            hijri_info = (h_obj.year, h_obj.month, h_obj.day, h_obj.month_length())
        except Exception:
            hijri_info = None

    is_occasion_holiday = False
    occasions: list[str] = []

    # 1. Solar Occasions
    solar_titles = _SOLAR_EVENT_MAP.get((p_month, p_day))
    if solar_titles:
        occasions.extend(solar_titles)
        if (p_month, p_day) in _SOLAR_HOLIDAY_SET:
            is_occasion_holiday = True

    # 2. Lunar Occasions (Official Iranian Calendar)
    if hijri_info is not None:
        h_year, h_month, h_day, h_days_in_month = hijri_info
        lunar_titles = _LUNAR_EVENT_MAP.get((h_month, h_day))
        if lunar_titles:
            occasions.extend(lunar_titles)
            if (h_month, h_day) in _LUNAR_HOLIDAY_SET:
                is_occasion_holiday = True

        # Special Case: Martyrdom of Imam Reza (AS) on the last day of Safar
        if h_month == 2 and h_day == h_days_in_month:
            im_title = "شهادت امام رضا (ع)"
            if im_title not in occasions:
                occasions.append(im_title)
            is_occasion_holiday = True

    # 3. International Gregorian Occasions
    gregorian_titles = _GREGORIAN_EVENT_MAP.get((current_dt.month, current_dt.day))
    if gregorian_titles:
        occasions.extend(gregorian_titles)

    return DayInfo(
        Date=datetime(current_dt.year, current_dt.month, current_dt.day),
        Title=weekday_name,
        Occasion=" - ".join(occasions) if occasions else None,
        IsThursday=is_thursday,
        IsFriday=is_friday,
        IsHoliday=is_friday or is_occasion_holiday,
    )
