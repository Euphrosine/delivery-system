from rest_framework import serializers
from .models import User,DeliveryRequest,DeliverySentForm




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class DeliveryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRequest
        fields = '__all__'

 

class DeliverySentFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliverySentForm
        fields = '__all__'