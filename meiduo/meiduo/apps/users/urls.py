from django.conf.urls import url
from users import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name="register"),  # 注册
    url(r'^login/$', obtain_jwt_token),  # 登录
    url(r'^user_detail/$', views.UserDetailView.as_view(), name="detail"),  # 用户详情
    url(r'^send_email/$', views.EmailView.as_view(), name="email"),  # 用户邮箱
    url(r'^verify_email/$', views.VerifyEmailView.as_view(), name='verify_email'),  # 验证邮箱
    url(r'^(?P<user_id>\d+)/addresses/$', views.AddressView.as_view(), name="address"),  # 用户地址
    url(r'^(?P<user_id>\d+)/addresses/(?P<address_id>\d+)/$', views.AddressView2.as_view(), name="address2"),
    url(r'^(?P<user_id>\d+)/addresses/(?P<address_id>\d+)/title/$', views.set_address_title, name="set_address_title"),  # 设置收获地址标题
    url(r'^(?P<user_id>\d+)/addresses/(?P<address_id>\d+)/status/$', views.set_default_address, name="set_default_address"),  # 设置默认收获地址
    url(r'^(?P<user_id>\d+)/reset_password/$', views.reset_password, name="reset_password"),  # 修改用户密码
]
