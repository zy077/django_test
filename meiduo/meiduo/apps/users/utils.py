import re
from users.models import User
from django.contrib.auth.backends import ModelBackend


def jwt_response_payload_handler(token, user=None, request=None):
    """自定义jwt认证成功返回数据"""
    return {
        "token": token,
        "username": user.username,
        "user_id": user.id
    }


def get_user_by_account(account):
    """
    根据帐号获取user对象
    :param account: 账号，可以是用户名，也可以是手机号
    :return: User对象 或者 None
    """
    try:
        if re.match(r'^1[345789]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    return user

class AuthenticateBack(ModelBackend):
    """自定义验证后端：支持用户名或者手机号"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user:
            # 校验密码
            if user.check_password(password):
                return user
