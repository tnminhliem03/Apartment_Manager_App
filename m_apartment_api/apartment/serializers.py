from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from m_apartment_api import settings
from apartment.models import (Room, Resident, Payment, Receipt, SecurityCard, Package, Complaint, Survey,
                              QuestionSurvey, AnswerSurvey, ResultSurvey, Notification)

class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'created_date', 'updated_date', 'resident']

class ImageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url

        return rep

class RoomSerializer(ImageSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'number', 'description', 'image', 'square', 'created_date',
                  'updated_date', 'is_empty']

class ResidentSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        data = validated_data.copy()
        resident = Resident(**data)
        resident.set_password(data['password'])
        resident.save()

        return resident

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['avatar'] = instance.avatar.url

        return rep

    class Meta:
        model = Resident
        fields = ['id', 'username', 'first_name', 'last_name', 'password', 'birthday', 'gender', 'email',
                  'phone', 'avatar', 'room']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = BaseSerializer.Meta.fields + ['amount']

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = BaseSerializer.Meta.fields + ['amount', 'payment']

class SecurityCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityCard
        fields = BaseSerializer.Meta.fields + ['name_register', 'vehicle_number', 'type_vehicle']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'name', 'created_date', 'updated_date', 'content']

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
        fields = ['id', 'name', 'description', 'created_date', 'updated_date']

class QuestionSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionSurvey
        fields = ['id', 'content', 'created_date', 'survey']

class AnswerSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerSurvey
        fields = ['id', 'content', 'created_date', 'question', 'resident']

class ResultSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultSurvey
        fields = ['id', 'survey', 'question', 'answer', 'resident']

