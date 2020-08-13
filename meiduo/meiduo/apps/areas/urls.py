from django.conf.urls import url
from areas import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'areas', views.AreaViewSet, basename='area')

urlpatterns = []

urlpatterns += router.urls