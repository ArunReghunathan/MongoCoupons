import string
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

COUPON_TYPES = getattr(settings, 'COUPONS_COUPON_TYPES', (
    ('monetary', 'Money based coupon'),
    ('percentage', 'Percentage discount'),
    ('virtual_currency', 'Virtual currency'),
))

CODE_LENGTH = getattr(settings, 'COUPONS_CODE_LENGTH', 15)

CODE_CHARS = getattr(settings, 'COUPONS_CODE_CHARS', string.ascii_letters + string.digits)

SEGMENTED_CODES = getattr(settings, 'COUPONS_SEGMENTED_CODES', False)
SEGMENT_LENGTH = getattr(settings, 'COUPONS_SEGMENT_LENGTH', 4)
SEGMENT_SEPARATOR = getattr(settings, 'COUPONS_SEGMENT_SEPARATOR', "-")

try:
    User = settings.COUPON_USER
except AttributeError:
    try:
        User = settings.AUTH_USER_MODEL
    except AttributeError:
        try:
            from django_mongoengine.mongo_auth.models import MongoUser
        except ImportError:
            raise ImproperlyConfigured('No Coupon User Provided')
        else:
            User = MongoUser
