from rest_framework_mongoengine.serializers import DocumentSerializer

from mongo_coupons.models import Coupon, Campaign, CouponUser


class CouponGenSerializer(DocumentSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


class CampaignSerializer(DocumentSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


class CouponUserSerializer(DocumentSerializer):
    class Meta:
        model = CouponUser
        fields = '__all__'
