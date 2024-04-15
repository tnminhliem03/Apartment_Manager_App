from rest_framework import serializers
from m_apartment_api import settings
from apartment.models import User, Payment, Receipt, SecurityCard, Package, Complaint, Survey

class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'created_date', 'updated_date', 'user']

class ImageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url

        return rep

class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(data['password'])
        user.save()

        return user

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['avatar'] = instance.avatar.url

        return rep

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'password', 'email', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = BaseSerializer.Meta.fields + ['amount', 'deadline_date']

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = BaseSerializer.Meta.fields + ['amount', 'payment']

class SecurityCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityCard
        fields = BaseSerializer.Meta.fields + ['name_register', 'vehicle_number']

class PackageSerializer(ImageSerializer):
    class Meta:
        model = Package
        fields = BaseSerializer.Meta.fields + ['note', 'image']

class ComplaintSerializer(ImageSerializer):
    class Meta:
        model = Complaint
        fields = BaseSerializer.Meta.fields + ['content', 'image']

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = BaseSerializer.Meta.fields + ['content']
