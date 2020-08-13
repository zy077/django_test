from rest_framework import serializers

from areas.models import Address
from users.models import User
from django_redis import get_redis_connection
import re
from rest_framework_jwt.settings import api_settings
from celery_tasks.tasks import send_verify_email


class RegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    password2 = serializers.CharField(label="确认密码", write_only=True)
    sms_code = serializers.CharField(label="短信验证码", write_only=True)
    allow = serializers.CharField(label="同意协议", write_only=True)
    token = serializers.CharField(label="登录状态token", read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "password2", "mobile", "sms_code", "allow", "token")
        # 补充验证条件
        extra_kwargs = {
            "username": {
                "max_length": 20,
                "min_length": 5,
                "error_messages": {
                    "max_length": "仅允许5-20个字符的用户名",
                    "min_length": "仅允许5-20个字符的用户名"
                }
            },
            "password": {
                "max_length": 20,
                "min_length": 8,
                "error_messages": {
                    "max_length": "仅允许8-20个字符的密码",
                    "min_length": "仅允许8-20个字符的密码"
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号格式"""
        if not re.match(r"^1[345789]\d{9}$", value):
            raise serializers.ValidationError("手机号格式错误！")
        if User.objects.filter(mobile=value).count() != 0:
            raise serializers.ValidationError("该手机号已存在！")
        return value

    def validate_username(self, value):
        """验证用户名是否存在"""
        if User.objects.filter(username=value).count() != 0:
            raise serializers.ValidationError("该用户已存在！")
        return value

    def validate_allow(self, value):
        """验证用户是否同意协议"""
        if value != "true":
            raise serializers.ValidationError("请同意协议！")
        return value

    def validate(self, attrs):
        # 验证用户两次输入的密码是否一致
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("两次输入的密码不一致！")

        # 检查短信验证码
        sms_code = attrs["sms_code"]  # 用户输入的短信验证码
        mobile = attrs["mobile"]
        try:
            redis_conn = get_redis_connection("verify_codes")
            real_sms_code = redis_conn.get("%s" % mobile)  # byte类型
        except Exception as e:
            raise serializers.ValidationError("获取短信验证码失败！")
        if not real_sms_code:
            raise serializers.ValidationError("短信验证码失效！")

        # 解码
        real_sms_code = real_sms_code.decode()

        # 和用户输入的短信验证码对比
        if real_sms_code != sms_code:
            raise serializers.ValidationError("短信验证码错误！")

        return attrs

    def create(self, validated_data):
        """保存数据"""
        # 删除验证数据中不需要保存的数据
        del validated_data["password2"]
        del validated_data["allow"]
        del validated_data["sms_code"]

        # 保存数据
        user = super().create(validated_data)
        # 对密码进行加密
        user.set_password(validated_data["password"])
        user.save()

        # 签发JWT_token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    class Meta:
        model = User
        fields = ["id", "username", "mobile", "email", "email_active"]


class EmailSerializer(serializers.ModelSerializer):
    """邮箱序列化器"""
    class Meta:
        model = User
        fields = ["id", "email"]
        extra_kwargs = {
            "email": {
                "required": True  # 邮箱为必填项
            }
        }

    def update(self, instance, validated_data):
        """保存用户邮箱信息"""
        email = validated_data["email"]
        instance.email = email
        instance.save()

        # 生成邮箱验证激活链接
        email_verify_url = instance.generate_verify_eamil_url()
        # 发送激活链接邮箱
        send_verify_email.delay(email_verify_url, email)

        return instance

class UserAddressSerializer(serializers.ModelSerializer):
    """用户地址序列化器"""

    class Meta:
        model = Address
        exclude = ("user", "is_deleted", "create_time", "update_time")

    def validate_mobile(self, value):
        """校验手机号格式"""
        if not re.match(r"^1[345789]\d{9}$", value):
            return serializers.ValidationError("手机号格式错误！")
        return value

    def validate_email(self, value):
        """验证邮箱格式"""
        if not re.match(r"^[a-zA-Z0-9_-]+@([a-zA-Z0-9]+\.)+(com|cn|net|org)$", value):
            return serializers.ValidationError("邮箱格式错误！")

    # def create(self, validated_data):
    #     if self.context["request"].user.addresses.count() > 20:
    #         return serializers.ValidationError("收获地址数量已达上限！")
    #     validated_data["user"] = self.context["request"].user
    #     return super().create(validated_data)

    # def update(self, instance, validated_data):
    #     print("修改用户地址")
    #     return super().update(instance, validated_data)













