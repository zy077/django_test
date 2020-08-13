from django.conf.urls import url
from verifications import views


urlpatterns = [
    url(r'^image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view(), name='image_code'),  # 图片验证码
    url(r'^sms_codes/(?P<mobile>\d{11})/$', views.SmsCodeView.as_view(), name='sms_code'),
]