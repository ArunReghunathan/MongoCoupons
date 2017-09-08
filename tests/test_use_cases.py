from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from mongo_coupons.models import Coupon


class DefaultCouponTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1")
        self.coupon = Coupon.objects.create_coupon('monetary', 100)

    def test_redeem(self):
        self.coupon.redeem(self.user)
        self.assertTrue(self.coupon.is_redeemed)
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertEquals(self.coupon.users.first().user, self.user)


class SingleUserCouponTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1")
        self.coupon = Coupon.objects.create_coupon('monetary', 100, self.user)

    def test_user_limited_coupon(self):
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertEquals(self.coupon.users.first().user, self.user)
        # not redeemed yet
        self.assertIsNone(self.coupon.users.first().redeemed_at)

    def test_redeem_with_user(self):
        self.coupon.redeem(self.user)
        # coupon should be redeemed properly now
        self.assertTrue(self.coupon.is_redeemed)
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertEquals(self.coupon.users.first().user, self.user)


class UnlimitedCouponTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1")
        self.coupon = Coupon.objects.create_coupon('monetary', 100, user_limit=0)

    def test_redeem_with_user(self):
        self.coupon.redeem(self.user)
        # coupon is not redeemed since it can be used unlimited times
        self.assertFalse(self.coupon.is_redeemed)
        # coupon should be redeemed properly now
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertEquals(self.coupon.users.first().user, self.user)
