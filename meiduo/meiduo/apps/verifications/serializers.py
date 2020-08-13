from rest_framework import serializers
from django_redis import get_redis_connection
import re


class ImgaeCodeCheckSerializer(serializers.Serializer):
    """图片验证码序列化器"""
    image_code_id = serializers.UUIDField(label="图片验证码id")
    text = serializers.CharField(label="验证码", max_length=4, min_length=4)

    def validate(self, attrs):
        """校验"""
        # 1、获取请求参数
        image_code_id = attrs["image_code_id"]
        text = attrs["text"]

        # 2、从redis中获取真实的图片验证码
        redis_conn = get_redis_connection('verify_codes')
        real_image_code = redis_conn.get("img_%s" % image_code_id)
        if not real_image_code:
            raise serializers.ValidationError("图片验证码失效")
        redis_conn.delete("img_%s" % image_code_id)  # 删除图片验证码，防止恶意获取
        # 校验图片验证码
        real_image_code = real_image_code.decode()
        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError("图片验证码错误！")

        # 3_1、校验手机号的格式
        mobile = self.context['view'].kwargs['mobile']
        if not re.match(r'^1[3456789]\d{9}$', mobile):
            raise serializers.ValidationError("手机号格式错误！")
        #3_2 发送记录
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            raise serializers.ValidationError("发送短信验证码太频繁，清稍后重试！")

        return attrs

