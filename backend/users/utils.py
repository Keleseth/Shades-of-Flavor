import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from users.validators import subscription_creatable


class Base64ImageField(serializers.ImageField):
    """Класс поля сериализатора для обработки изображений в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def get_subscription_data(request, kwargs):
    user = request.user
    subscribed_user_id = kwargs['id']
    subscribed_user = subscription_creatable(user, subscribed_user_id)
    return user, subscribed_user
