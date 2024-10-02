from rest_framework import response, status
from rest_framework.exceptions import ValidationError

from .models import CustomUser


def subscription_creatable(user, subscribed_user_id):

    try:
        subscribed_user = CustomUser.objects.get(id=subscribed_user_id)
    except CustomUser.DoesNotExist:
        raise ValidationError({'detail': 'Пользователь не найден.'})
    if user == subscribed_user:
        raise ValidationError({'detail': 'Нельзя подписываться на себя.'})
    return subscribed_user
