from io import BytesIO

import qrcode
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from common.models import AppName


class Qrcode(object):

    def generate_url(self, obj, type):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        app = AppName.objects.filter(type=AppName.PRODUCTION).first()
        name = app.host_name
        if settings.DEBUG:
            app = AppName.objects.filter(type=AppName.DEVELOPMENT).first()
            name = app.host_name
        data = f"{name}/post_detail?id={obj.id}"
        if type == 'user':
            data = f"{name}/my_profile?id={obj.id}"
        qr.add_data(data)
        qr.make(fit=True)
        qrcode_img = qr.make_image()
        buffer = BytesIO()
        qrcode_img.save(buffer, format='PNG')
        filename = f'{str(obj.id)}.png'
        filebuffer = InMemoryUploadedFile(buffer, None, filename, 'image/png', 100, None)
        return filename, filebuffer, qrcode_img

    def save_user_qrcode(self, user):
        filename, file_buffer, qrcode_img = self.generate_url(user, 'user')
        user.profile_qr.save(filename, file_buffer)
        user.save()
        qrcode_img.close()
        return user

    def save_post_qrcode(self, post):
        filename, file_buffer, qrcode_img = self.generate_url(post, 'post')
        post.post_qr.save(filename, file_buffer)
        post.save()
        qrcode_img.close()
        return post
