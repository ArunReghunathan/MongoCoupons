from mongoengine import ValidationError
from rest_framework_mongoengine.serializers import DocumentSerializer

from mongo_coupons.models import Coupon, CouponUser
from django.utils.translation import ugettext_lazy as _


class CouponSerializer(DocumentSerializer):
    class Meta:
        model = Coupon
        depth = 4
        fields = '__all__'

    def update(self, instance, validated_data):
        code = validated_data['code']
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise ValidationError(_("This code is not valid."))
        self.coupon = coupon

        if self.user is None and coupon.user_limit is not 1:
            # coupons with can be used only once can be used without tracking the user, otherwise there is no chance
            # of excluding an unknown user from multiple usages.
            raise ValidationError(_(
                "The server must provide an user to this form to allow you to use this code. Maybe you need to sign in?"
            ))

        if coupon.is_redeemed:
            raise ValidationError(_("This code has already been used."))

        try:  # check if there is a user bound coupon existing
            user_coupon = coupon.users.get(user=self.user)
            if user_coupon.redeemed_at is not None:
                raise ValidationError(_("This code has already been used by your account."))
        except CouponUser.DoesNotExist:
            if coupon.user_limit is not 0:  # zero means no limit of user count
                # only user bound coupons left and you don't have one
                if coupon.user_limit is coupon.users.filter(user__isnull=False).count():
                    raise ValidationError(_("This code is not valid for your account."))
                if coupon.user_limit is coupon.users.filter(redeemed_at__isnull=False).count():  # all coupons redeemed
                    raise ValidationError(_("This code has already been used."))
        if self.types is not None and coupon.type not in self.types:
            raise ValidationError(_("This code is not meant to be used here."))
        if coupon.expired():
            raise ValidationError(_("This code is expired."))
        return code
