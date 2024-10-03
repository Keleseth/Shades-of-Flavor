from rest_framework import response, status
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import CustomUser


def subscription_creatable(user, subscribed_user_id):

    subscribed_user = get_object_or_404(
        CustomUser,
        id=subscribed_user_id,
    )
    if user == subscribed_user:
        raise ValidationError({'detail': 'Нельзя подписываться на себя.'})
    return subscribed_user
