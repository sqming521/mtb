from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .. import models


class ServiceMessageSerializer(serializers.ModelSerializer):
    """ 客服消息 """

    class Meta:
        model = models.Message
        fields = ['title', 'public', 'content', 'img']

    def validate_public(self, obj):
        request = self.context['request']

        if obj.mtb_user_id == request.user.user_id:
            return obj
        raise ValidationError("公众号选择错误")