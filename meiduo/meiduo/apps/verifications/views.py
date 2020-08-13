from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from meiduo.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse
from rest_framework.response import Response
import random
from verifications import serializers
from celery_tasks.tasks import send_sms_code


# Create your views here.

class ImageCodeView(APIView):
    """图片验证码"""

    def get(self, request, image_code_id):
        """获取图片验证码"""
        # 1、生成图片验证码
        text, image = captcha.generate_captcha()

        # 2、保存图片验证码
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" % image_code_id, 5 * 60, text)  # 图片验证码的有效期为5分钟

        # 3、返回图片验证码
        print("图片验证码：{}".format(text))
        return HttpResponse(content=image, content_type='images/jpg')


class SmsCodeView(GenericAPIView):
    """短信验证码"""
    serializer_class = serializers.ImgaeCodeCheckSerializer  # 指定校验参数的序列化器

    def get(self, request, mobile):
        # 1、获取参数
        # param = request.query_params
        # image_code_id = param.get("image_code_id")
        # image_code = param.get("text")

        # 2、校验参数
        # 在提供序列化器对象的时候，REST framework会向对象的context属性补充三个数据：
        # request、format、view，这三个数据对象可以在定义序列化器时使用。
        serializer = self.get_serializer(data=request.query_params)  # 创建序列化器对象
        serializer.is_valid(raise_exception=True)  # 校验参数，失败会抛出异常

        # 3_1、生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        # 3_1、保存短信验证码和发送记录
        redis_conn = get_redis_connection("verify_codes")
        pl = redis_conn.pipeline()  # 创建流水线对象
        pl.setex("%s" % mobile, 60, sms_code)
        pl.setex("send_flag_%s" % mobile, 60, 1)
        pl.execute()

        # 3_1、发送验证码
        # print("短信验证码：{}".format(sms_code))
        send_sms_code.delay(sms_code)  # 使用celery发送短信验证码

        # 4、返回响应
        return Response({"message": "OK"}, status=200)


