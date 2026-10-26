import sys
import unittest

# Ensure Microservice-AppManagement is in path
sys.path.insert(0, 'Back-End/Microservice-AppManagement')
from services.persian_calendar_generator import get_year_days, get_day_info, is_leap_year


class TestPersianCalendarGenerator(unittest.TestCase):
    def test_leap_years(self):
        self.assertFalse(is_leap_year(1405))
        self.assertFalse(is_leap_year(1406))
        self.assertFalse(is_leap_year(1407))
        self.assertTrue(is_leap_year(1408))

    def test_year_1406_events(self):
        days = get_year_days(1406)
        self.assertEqual(len(days), 365)

        # 12 Aban 1406 (2027-11-03): شهادت حضرت فاطمه زهرا (س) [ ۳ جمادی الثانیه ] -> IsHoliday=True
        d_12_aban = [d for d in days if d.Date.strftime('%Y-%m-%d') == '2027-11-03'][0]
        self.assertTrue(d_12_aban.IsHoliday)
        self.assertIn('شهادت حضرت فاطمه زهرا', d_12_aban.Occasion or '')

        # 29 Aban 1406 (2027-11-20): ولادت حضرت فاطمه زهرا (س) و روز مادر [ ۲۰ جمادی الثانیه ] -> IsHoliday=False
        d_29_aban = [d for d in days if d.Date.strftime('%Y-%m-%d') == '2027-11-20'][0]
        self.assertIn('ولادت حضرت فاطمه زهرا', d_29_aban.Occasion or '')
        self.assertFalse(d_29_aban.IsHoliday)

        # 8 Esfand 1406 (2028-02-27): عید سعید فطر [ ۱ شوال ] -> IsHoliday=True
        d_08_esfand = [d for d in days if d.Date.strftime('%Y-%m-%d') == '2028-02-27'][0]
        self.assertTrue(d_08_esfand.IsHoliday)
        self.assertIn('عید سعید فطر', d_08_esfand.Occasion or '')

    def test_year_1407_events(self):
        days = get_year_days(1407)
        self.assertEqual(len(days), 365)

        # 12 Bahman 1407 (2029-01-31): ولادت امام حسن مجتبی (ع) [ ۱۵ رمضان ] -> IsHoliday=False
        d_12_bahman = [d for d in days if d.Date.strftime('%Y-%m-%d') == '2029-01-31'][0]
        self.assertIn('ولادت امام حسن مجتبی', d_12_bahman.Occasion or '')
        self.assertFalse(d_12_bahman.IsHoliday)

        # 18 Bahman 1407 (2029-02-06): شهادت حضرت علی (ع) [ ۲۱ رمضان ] -> IsHoliday=True
        d_18_bahman = [d for d in days if d.Date.strftime('%Y-%m-%d') == '2029-02-06'][0]
        self.assertTrue(d_18_bahman.IsHoliday)
        self.assertIn('شهادت حضرت علی', d_18_bahman.Occasion or '')

        # 27 Bahman 1407 (2029-02-15): عید سعید فطر [ ۱ شوال ] -> IsHoliday=True
        d_27_bahman = [d for d in days if d.Date.strftime('%Y-%m-%d') == '2029-02-15'][0]
        self.assertTrue(d_27_bahman.IsHoliday)
        self.assertIn('عید سعید فطر', d_27_bahman.Occasion or '')

        # 28 Bahman 1407 (2029-02-16): تعطیل به مناسبت عید سعید فطر [ ۲ شوال ] -> IsHoliday=True
        d_28_bahman = [d for d in days if d.Date.strftime('%Y-%m-%d') == '2029-02-16'][0]
        self.assertTrue(d_28_bahman.IsHoliday)


if __name__ == '__main__':
    unittest.main()
