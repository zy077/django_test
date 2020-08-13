from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.response import JsonResponse

from users.serializers import RegisterSerializer, UserDetailSerializer, EmailSerializer
from rest_framework.permissions import IsAuthenticated
from users.models import User
from areas.models import Address, Area
from users.serializers import UserAddressSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
import logging
import datetime
import json

logger = logging.getLogger("django")


class RegisterView(CreateAPIView):
    """注册"""
    serializer_class = RegisterSerializer  # 指定序列化器


class UserDetailView(RetrieveAPIView):
    """用户详情"""
    serializer_class = UserDetailSerializer  # 用户详情序列化器
    permission_classes = [IsAuthenticated]  # 只有登录用户才有访问权限

    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """保存邮箱信息、发送邮箱验证码"""
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, *args, **kwargs):
        return self.request.user


class VerifyEmailView(APIView):
    """验证邮箱"""

    def get(self, request):
        # 获取token
        token = request.query_params.get("token")
        if not token:
            error_data = {
                "message": "缺少token"
            }
            return Response(data=error_data, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.verify_email_token(token)
        if user is None:
            error_data = {
                "message": "链接信息无效"
            }
            return Response(data=error_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 修改用户邮箱激活状态
            user.email_active = True
            user.save()
            data = {
                "message": "OK"
            }
            return Response(data=data, status=status.HTTP_200_OK)


class AddressView(GenericAPIView):
    """用户地址管理——新增和查询"""
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    # queryset = Address.objects.filter(is_delected=False)

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def get(self, request, user_id):
        # print("用户id:{}".format(user_id))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print(serializer.data)
        return JsonResponse({
            "addresses": serializer.data,
            "limit": 20
        })

    def post(self, request, user_id):
        # 检查用户的收获地址数量是否已达上限
        # 获取提交的数据
        param_dict = request.data
        print(param_dict)
        if request.user.addresses.count() > 20:
            logger.error("查询数据失败！")
            error_data = {"message": "收获地址数量已经达到上限！"}
            return JsonResponse(data=error_data, status=status.HTTP_400_BAD_REQUEST)
        # 保存数据
        # return super().create(request, *args, **kwargs)
        # 对提交的数据做简单的处理
        province = Area.objects.get(id=param_dict.get("province_id")).name
        city = Area.objects.get(id=param_dict.get("city_id")).name
        district = Area.objects.get(id=param_dict.get("district_id")).name
        del param_dict["province_id"]
        del param_dict["city_id"]
        del param_dict["district_id"]
        param_dict["province"] = province
        param_dict["city"] = city
        param_dict["district"] = district
        param_dict["user_id"] = user_id
        # 校验提交的数据
        # serializer = self.get_serializer(param_dict)
        # serializer.is_valid(raise_exception=True)
        # 保存数据
        address = Address.objects.create(
            user_id=param_dict["user_id"],
            title=param_dict["title"],
            receiver=param_dict["receiver"],
            province=param_dict["province"],
            city=param_dict["city"],
            district=param_dict["district"],
            place=param_dict["place"],
            mobile=param_dict["mobile"],
            telephone=param_dict["telephone"],
            email=param_dict["email"]
        )
        # 返回相应
        data = {
            "user_id": address.user_id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province,
            "city": address.city,
            "district": address.district,
            "place": address.place,
            "mobile": address.mobile,
            "telephone": address.telephone,
            "email": address.email
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)


class AddressView2(GenericAPIView):
    """用户地址管理——修改、删除、设置默认收获地址"""

    def put(self, request, user_id, address_id):
        """修改用户收获地址"""
        param_dict = request.data
        print(param_dict)
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            logger.error("查询数据失败！")
            error_data = {
                "message": "查询数据失败！"
            }
            return JsonResponse(data=error_data, status=status.HTTP_400_BAD_REQUEST)
        # serializer = self.get_serializer(isinstance=address, data=param_dict)
        address.user_id = user_id
        address.title = param_dict["title"]
        address.receiver = param_dict["receiver"]
        province = Area.objects.get(id=param_dict["province_id"]).name
        address.province = province
        city = Area.objects.get(id=param_dict["city_id"]).name
        address.city = city
        district = Area.objects.get(id=param_dict["district_id"]).name
        address.district = district
        address.place = param_dict["place"]
        address.mobile = param_dict["mobile"]
        address.telephone = param_dict.get("tel") if param_dict.get("tel") else param_dict["telephone"]
        address.email = param_dict["email"]
        address.update_time = datetime.datetime.now()
        # print(datetime.datetime.now())
        address.save()
        # Address.objects.filter(id=address_id).update()  批量更新
        return JsonResponse({"message": "OK"}, status=status.HTTP_200_OK)

    def delete(self, request, user_id, address_id):
        """删除用户收获地址"""
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            logger.error("查询数据失败！")
            error_data = {
                "message": "查询数据失败！"
            }
            return JsonResponse(data=error_data, status=status.HTTP_400_BAD_REQUEST)
        address.delete()
        # Address.objects.filter(id=address_id).delete() 批量删除
        return JsonResponse(data={"message": "删除成功！"}, status=status.HTTP_200_OK)


def set_address_title(request, user_id, address_id):
    """设置用户收获地址标题"""
    # 获取参数
    str_bytes = request.body
    json_str = str_bytes.decode()  # python3.6 无需执行此步
    param_dict = json.loads(json_str)  # 反序列化
    addredd_title = param_dict.get("title", "")
    # 查询要修改的地址对象
    Address.objects.filter(id=address_id).update(title=addredd_title)


def set_default_address(request, user_id, address_id):
    """设置默认收获地址"""
    Address.objects.filter(id=address_id).update(is_default=True)

@csrf_exempt
def reset_password(request, user_id):
    """修改密码"""
    # 1、获取参数
    str_bytes = request.body
    json_str = str_bytes.decode()
    param_dict = json.loads(json_str)
    # 2、查询要修改的用户对象
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("查询数据失败！")
        error_data = {
            "message": "查询数据失败！"
        }
        return JsonResponse(data=error_data, status=status.HTTP_400_BAD_REQUEST)
    # 3、校验两次密码是否一致
    if param_dict["new_pwd"] != param_dict["confirm_pwd"]:
        return JsonResponse({"message": "两次输入的新密码不一致！"}, status=status.HTTP_400_BAD_REQUEST)
    # 4、校验密码是否正确
    if not user.check_password(param_dict["current_pwd"]):
        return JsonResponse(data={"message": "密码错误！"}, status=status.HTTP_400_BAD_REQUEST)
    # 5、修改并保存新密码
    user.set_password(param_dict["new_pwd"])
    user.save()
    return JsonResponse({"message": "OK!"}, status=status.HTTP_200_OK)
