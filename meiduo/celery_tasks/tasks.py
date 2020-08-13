# from celery_tasks.yuntongxun.sms import CCP
# import logging
# from celery_tasks.celery import celery_app
#
# logger = logging.getLogger("django")
#
# # 验证码短信模板
# SMS_CODE_TEMP_ID = 1
#
# @celery_app.task(name='send_sms_code')
# def send_sms_code(mobile, code, expires):
#     """
#     发送短信验证码
#     :param mobile:手机号
#     :param code: 验证码
#     :param expires: 有效期
#     :return:
#     """
#     try:
#         ccp = CCP()
#         result = ccp.send_template_sms(mobile, [code, expires], SMS_CODE_TEMP_ID)
#     except Exception as e:
#         logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
#     else:
#         if result == 0:
#             logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
#         else:
#             logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)


from celery_tasks.celery import celery_app
from django.core.mail import send_mail
from django.conf import settings

@celery_app.task(name='send_sms_code')
def send_sms_code(code):
    """使用celery异步任务发送短信验证码"""
    print("短信验证码：{}".format(code))


@celery_app.task(name='send_verify_email')
def send_verify_email(verify_url, to_email):
    """异步发送验证邮箱激活邮件"""
    # send_mail(subject, message, from_email, recipient_list,
    #           fail_silently=False, auth_user=None, auth_password=None,
    #           connection=None, html_message=None):
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s</a></p>' % (to_email, verify_url, verify_url)
    send_mail(
        subject=subject,
        message=html_message,
        from_email=settings.EMAIL_FROM,
        recipient_list=[to_email]
    )