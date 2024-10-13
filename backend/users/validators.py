from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import CustomUser


def subscription_creatable(user, subscribed_user_id):
    """
    Валидатор, проверяющий, что пользователь на которого подписываются -
    существует и это не автор запроса.
    """

    subscribed_user = get_object_or_404(
        CustomUser,
        id=subscribed_user_id,
    )
    if user == subscribed_user:
        raise ValidationError({'detail': 'Нельзя подписываться на себя.'})
    return subscribed_user
