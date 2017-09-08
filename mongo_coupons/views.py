from mongoengine import ValidationError
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.views import APIView
from rest_framework_mongoengine.viewsets import ModelViewSet, GenericViewSet

from mongo_coupons.models import Coupon, Campaign, CouponUser
from mongo_coupons.serializer import CouponGenSerializer, CampaignSerializer


class CouponView(ModelViewSet):
    model = Coupon
    serializer_class = CouponGenSerializer
    lookup_field = 'code'
    queryset = Coupon.objects

    def get_queryset(self):
        return Coupon.objects.all()


class CampaignView(ModelViewSet):
    model = Campaign
    serializer_class = CampaignSerializer
    queryset = Campaign.objects
    lookup_field = 'name'

    def get_queryset(self):
        return Campaign.objects.all()


class CouponValidityView(APIView):
    def get(self, request, **kwargs):
        code = request.data['code']
        if 'types' in kwargs:
            types = kwargs['types']
            del kwargs['types']
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise ValidationError("This code is not valid.")

        if request.user is None and coupon.user_limit is not 1:
            # coupons with can be used only once can be used without tracking the user, otherwise there is no chance
            # of excluding an unknown user from multiple usages.
            raise ValidationError(
                "The server must provide an user to this form to allow you to use this code. Maybe you need to sign in?"
            )

        if coupon.is_redeemed:
            raise ValidationError("This code has already been used.")

        if request.user and not coupon.is_valid(request.user):
            raise ValidationError("This code has already been used.")

        try:  # check if there is a user bound coupon existing
            user_coupon = CouponUser.objects.get(user=request.user, coupon=coupon)
            if user_coupon.redeemed_at is not None:
                raise ValidationError(_("This code has already been used by your account."))
        except CouponUser.DoesNotExist:
            if coupon.user_limit is not 0:  # zero means no limit of user count
                # only user bound coupons left and you don't have one
                if coupon.user_limit is coupon.users.filter(user__exists=True).count():
                    raise ValidationError("This code is not valid for your account.")
                if coupon.user_limit is coupon.users.filter(redeemed_at__exists=True).count():  # all coupons redeemed
                    raise ValidationError("This code has already been used.")
        if types and coupon.type not in types:
            raise ValidationError("This code is not meant to be used here.")
        if coupon.expired():
            raise ValidationError("This code is expired.")
        return code
