from rest_framework import serializers
from .. import models

class PublicNumberSerializer(serializers.ModelSerializer):
    service_type_info_text = serializers.CharField(source='get_service_type_info')
    verify_type_info_text = serializers.CharField(source='get_verify_type_info')

    class Meta:
        model = models.PublicNumbers
        fields = ["id","nick_name","avatar","service_type_info_text","verify_type_info_text"]