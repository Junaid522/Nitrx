from django.conf import settings
from django.core.mail import send_mail as main_email_send
from django.template.loader import get_template


class Email(object):

    def send_email(self, subject, content, user_email, html_content=None):
        # print(subject, content, settings.EMAIL_HOST_USER, [user_email], html_content)
        main_email_send(subject, content, settings.EMAIL_HOST_USER, [user_email], fail_silently=False,
                        html_message=html_content)

    def send_otp_email(self, user, otp):
        htmly = get_template('otp_email.html')
        content = 'Code: {}'.format(otp)
        d = {'email_body': content,
             "email_type": 'Nitrx OTP', "user": user}
        html_content = htmly.render(d)
        self.send_email('Nitrx', '', user.email, html_content=html_content)
