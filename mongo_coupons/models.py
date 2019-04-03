import random

from datetime import datetime

from django.db import IntegrityError
from django.dispatch import Signal
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_mongoengine.queryset import QuerySetManager
from mongoengine import Document, fields, ValidationError, Q
from mongo_coupons.coupon_settings import User

from .coupon_settings import (
    COUPON_TYPES,
    CODE_LENGTH,
    CODE_CHARS,
    SEGMENTED_CODES,
    SEGMENT_LENGTH,
    SEGMENT_SEPARATOR,
)

redeem_done = Signal(providing_args=["coupon"])


class CouponManager(QuerySetManager):
    def create_coupon(self, coupon_type, value, users=[], valid_until=None, prefix="", campaign=None, user_limit=None,
                      usage_limit=None):
        coupon = self.create(
            value=value,
            code=Coupon.generate_code(prefix),
            type=coupon_type,
            valid_until=valid_until,
            campaign=campaign,
        )
        if user_limit is not None:  # otherwise use default value of model
            coupon.user_limit = user_limit
        if usage_limit is not None:  # otherwise use default value of model
            coupon.usage_limit = usage_limit

        try:
            coupon.save()
        except IntegrityError:
            # Try again with other code
            coupon = Coupon.objects.create_coupon(type, value, users, valid_until, prefix, campaign)
        if not isinstance(users, list):
            users = [users]
        for user in users:
            if user:
                CouponUser(user=user, coupon=coupon).save()
        return coupon

    def create_coupons(self, quantity, type, value, valid_until=None, prefix="", campaign=None):
        coupons = []
        for i in range(quantity):
            coupons.append(self.create_coupon(type, value, None, valid_until, prefix, campaign))
        return coupons

    def used(self):
        return CouponUser.exclude(coupon=self, redeemed_at__exists=True)

    def unused(self):
        return CouponUser.filter(Q(coupon=self) & (Q(redeemed_at__exists=False) | Q(redeemed_at__exists=False)))

    def expired(self):
        return self.filter(valid_until__lt=datetime.utcnow())

    def valid(self):
        return self.filer(Q(users__redeemed_at__exists=False) & Q(valid_until__gt=datetime.utcnow()))


# @python_2_unicode_compatible
class Coupon(Document):
    value = fields.IntField(verbose_name="Value", required=True, help_text=_("Arbitrary coupon value"))
    code = fields.StringField(required=False, verbose_name="Code", unique=True, max_length=30, null=True)
    product = fields.StringField(required=False, default="all", verbose_name="Product", max_length=30, null=True)
    max_discount = fields.IntField(required=False, verbose_name="Maximum discount", null=True)
    type = fields.StringField(verbose_name="Type", required=True, max_length=20, choices=COUPON_TYPES)
    user_limit = fields.IntField(verbose_name="User limit", default=1, min_value=0)
    usage_limit = fields.IntField(verbose_name="Usage limit per user", default=1, min_value=0)
    created_at = fields.DateTimeField(verbose_name="Created at", default=datetime.utcnow())
    valid_until = fields.DateTimeField(verbose_name="Valid until", blank=True, null=True,
                                       help_text="Leave empty for coupons that never expire")
    campaign = fields.ReferenceField('Campaign', verbose_name="Campaign", blank=True, null=True,
                                     related_name='coupons', dbref=True)
    kwargs = fields.DictField(required=False, null=True)

    objects = CouponManager()

    meta = {
        'collection': "coupons",
        'indexes': ['code', 'valid_until']
    }

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Coupon.generate_code()
        super(Coupon, self).save(*args, **kwargs)

    def is_expired(self):
        return self.valid_until is not None and self.valid_until < datetime.utcnow()

    def is_wrong_product(self, product="all"):
        if self.product in ["all", product, None]:
            return False # correct coupon code
        else:
            return True # its a wrong product

    @property
    def is_redeemed(self):
        """ Returns true is a coupon is redeemed (completely for all users) otherwise returns false. """
        return CouponUser.filter(
            redeemed_at__exists=True
        ).count() >= self.user_limit and self.user_limit is not 0

    @property
    def redeemed_at(self):
        # try:
        return CouponUser.objects.get(coupon=self, redeemed_at__ne=[]).sort('-redeemed_at').first().redeemed_at[-1]
        #     # return self.users.filter(redeemed_at__exists=True).order_by('redeemed_at').last().redeemed_at
        # except CouponUser.through.DoesNotExist:
        #     return None

    @classmethod
    def generate_code(cls, prefix="", segmented=SEGMENTED_CODES):
        code = "".join(random.choice(CODE_CHARS) for i in range(CODE_LENGTH))
        if segmented:
            code = SEGMENT_SEPARATOR.join([code[i:i + SEGMENT_LENGTH] for i in range(0, len(code), SEGMENT_LENGTH)])
            return prefix + code
        else:
            return prefix + code

    def redeem(self, user=None):
        if user:
            user = User.objects.get(id=user)
        try:
            coupon_user = CouponUser.objects.get(coupon=self,
                                                 user=user)
        except CouponUser.DoesNotExist:
            try:  # silently fix unbouned or nulled coupon users
                coupon_user = CouponUser.objects.get(user__exists=False)
                coupon_user.user = user
            except CouponUser.DoesNotExist:
                coupon_user = CouponUser(coupon=self, user=user)
        if self.usage_limit and coupon_user.used and coupon_user.used >= self.usage_limit:
            raise ValidationError("This code has already been used.")
        coupon_user.redeemed_at.append(datetime.utcnow())
        coupon_user.used += 1
        coupon_user.save()
        redeem_done.send(sender=self.__class__, coupon=self)

    def is_valid(self, user):
        if user:
            user = User.objects.get(id=user)
        try:
            coupon_user = CouponUser.objects.get(coupon=self, user=user)
        except CouponUser.DoesNotExist:
            return True
        if self.usage_limit and coupon_user.redeemed_at and len(coupon_user.redeemed_at) >= self.usage_limit:
            return False
        return True
    def check_user_limit(self):
        coupon_users = CouponUser.objects.filter(coupon=self)
        if self.user_limit and len(coupon_users) > self.user_limit:
            return False
        return True

    def apply_coupon(self, amount, user=None, product="all"):
        '''amount: amount to be paid'''
        if self.is_wrong_product(product):
            raise ValidationError("Sorry, this coupon is not valid for this product.")

        if self.is_expired():
            raise ValidationError("This code has been expired")

        if user:
            if not self.is_valid(user):
                raise ValidationError("This code has already been used.")
         
        if not self.check_user_limit():
            raise ValidationError("This code has already been used.")

        if self.type == 'percentage':
            discount = amount * self.value / 100
            try:
                if self.max_discount and discount > self.max_discount:
                    discount = self.max_discount
            except AttributeError:
                pass
        else:
            discount = self.value
        amount -= discount
        return amount if amount > 0 else 0


@python_2_unicode_compatible
class Campaign(Document):
    name = fields.StringField(max_length=255, unique=True)
    description = fields.StringField(null=True)
    kwargs = fields.DictField(required=False, null=True)

    meta = {
        'collection': "campaign"
    }

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class CouponUser(Document):
    coupon = fields.ReferenceField(Coupon, dbref=True)
    user = fields.ReferenceField(User, dbref=True, null=True)  #
    # , unique_with=coupon)
    redeemed_at = fields.ListField(fields.DateTimeField(verbose_name="Redeemed at", null=True))
    used = fields.IntField(verbose_name="No of times coupon is reedemed", default=0)
    kwargs = fields.DictField(required=False, null=True)

    meta = {
        'collection': "coupon_user",
        'indexes': ['coupon', 'user', 'redeemed_at', 'used']
    }

    def __str__(self):
        return str(self.user)

