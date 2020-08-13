from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ReadOnlyModelViewSet
from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class AreaViewSet(ReadOnlyModelViewSet, CacheResponseMixin):  # CacheResponseMixin缓存list和retrieve
    """行政区划视图集"""
    pagination_class = None  # 区划信息不分页

    def get_queryset(self):
        """查询数据集是列表视图与详情视图获取数据的基础"""
        if self.action == "list":
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """返回序列化器类，默认返回serializer_class"""
        if self.action == "list":
            return AreaSerializer
        else:
            return SubAreaSerializer

