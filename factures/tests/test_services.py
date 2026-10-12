from django.test import SimpleTestCase

from factures.services import calculate_usage_amount, calculate_total_with_fees


class FactureServiceTests(SimpleTestCase):
    def test_calculate_usage_amount_for_first_tier(self):
        amount = calculate_usage_amount(10)
        self.assertEqual(amount, 2000)

    def test_calculate_usage_amount_across_multiple_tiers(self):
        amount = calculate_usage_amount(35)
        self.assertEqual(amount, 2400 + 5100 + 2430)

    def test_calculate_total_with_fees(self):
        total = calculate_total_with_fees(13000, 230, 345)
        self.assertEqual(total, 13575)
