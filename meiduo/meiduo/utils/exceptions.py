from rest_framework.views import exception_handler as def_exception_handler
from django.db import DatabaseError
from redis.exceptions import RedisError
import logging
from rest_framework.response import Response
from rest_framework import status

# 获取在配置文件中定义的logger，用来记录日志
logger = logging.getLogger('django')


def exception_handler(exc, context):
    """
    自定义异常处理
    :param exc:异常
    :param context: 抛出的异常上下文
    :return: Response响应
    """

    # 调用drf框架原生的异常处理方法
    response = def_exception_handler(exc, context)

    if response is None:
        view = context['view']
        # 判断是否是数据库异常
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            # 记录异常
            logger.error("[%s] %s" % (view, exc))
            response = Response({"message": "服务器内部错误"}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response
