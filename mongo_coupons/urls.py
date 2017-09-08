"""django_mongo_coupons URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url

from mongo_coupons.views import CouponView, CampaignView

coupon_list = CouponView.as_view({
    'get': 'list',
    'post': 'create'
})
coupon_detail = CouponView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

campaign_list = CampaignView.as_view({
    'get': 'list',
    'post': 'create'
})
campaign_detail = CampaignView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    url(r'coupons/$', coupon_list, name='coupon-list'),
    url(r'coupons/(?P<code>\w+)/$', coupon_detail, name='coupon-detail'),
    url(r'campaign/$', campaign_list, name='campaign-list'),
    url(r'campaign/(?P<name>\w+)/$', campaign_detail, name='campaign-detail'),
    url(r'check/(?P<name>\w+)/$', campaign_detail, name='campaign-detail'),
]
