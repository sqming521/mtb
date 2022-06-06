from rest_framework import serializers

class AuthSerializer(serializers.Serializer):
    username = serializers.CharField(label="用户名",required=True)
    password = serializers.CharField(label="密码",required=True)