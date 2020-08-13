from django.db import models
from users.models import User
from datetime import datetime

# Create your models here.

class Area(models.Model):
    """ 行政区划"""
    name = models.CharField(verbose_name="名称", max_length=20)
    parent = models.ForeignKey(verbose_name='上级行政区划', to='self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True)

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name


class Address(models.Model):
    """用户地址"""
    user = models.ForeignKey(verbose_name="用户", to=User, related_name="addresses", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="地址名称", max_length=20)
    receiver = models.CharField(verbose_name="收货人", max_length=20)
    province = models.CharField(verbose_name="省", max_length=20)
    city = models.CharField(verbose_name="市", max_length=20)
    district = models.CharField(verbose_name="区", max_length=20)
    place = models.CharField(verbose_name="详细地址", max_length=200)
    mobile = models.CharField(verbose_name="手机号", max_length=11)
    telephone = models.CharField(verbose_name="固定电话", max_length=20, null=True, blank=True, default='')
    email = models.CharField(verbose_name="邮箱", max_length=20)
    is_deleted = models.BooleanField(verbose_name="逻辑删除", default=False)
    is_default = models.BooleanField(verbose_name="默认地址", default=False)
    create_time = models.DateTimeField(verbose_name="创建时间", default=datetime.now)
    update_time = models.DateTimeField(verbose_name="更新时间", default=datetime.now)

    class Meta:
        db_table = "tb_address"
        verbose_name= "用户地址"
        verbose_name_plural = verbose_name
        ordering = ["-update_time"]

    def __str__(self):
        return self.title






