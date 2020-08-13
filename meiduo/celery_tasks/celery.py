from celery import Celery

# 为celery使用django配置文件进行设置（告诉celery django的配置文件的位置）
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo.settings.dev'

# 第一个参数为当前模块的名称， 第二个参数为中间人（Broker）的链接 URL，不过本项目中把配置防盗一个单独的文件中
celery_app = Celery('celery')  # 创建celery应用

celery_app.config_from_object('celery_tasks.celeryconfig')  # 导入celery配置

celery_app.autodiscover_tasks(['celery_tasks'])  # 自动搜索celery任务（task所在模块）
