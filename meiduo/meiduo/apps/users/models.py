from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings


# Create your models here.

class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(verbose_name="手机号", max_length=11, unique=True)
    email_active = models.BooleanField(verbose_name="邮箱验证状态", default=False)
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_verify_eamil_url(self):
        """生成邮箱激活链接"""
        serializer = TJWSSerializer(secret_key=settings.SECRET_KEY, expires_in=24 * 60 * 60)  # 邮箱激活链接有效期24h
        data = {
            "user_id": self.id,
            "email": self.email
        }
        token = serializer.dumps(data).decode()
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url

    def verify_email_token(self, token):
        """校验token"""
        serializer = TJWSSerializer(secret_key=settings.SECRET_KEY)

        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            user_id = data.get("id")
            email = data.get("email")

            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user



