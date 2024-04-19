from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
# Create your models here.

class User(AbstractUser):
    pass

class BaseModel(models.Model):
    name = models.CharField(max_length=255)
    created_date =models.DateTimeField(auto_now_add=True)
    updated_date =models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

class Room(BaseModel):
    number = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=255)
    image = CloudinaryField()
    square = models.DecimalField(max_digits=5, decimal_places=2)
    is_empty = models.BooleanField(default=True)

    def __str__(self):
        return self.number

phone_validator = RegexValidator(regex=r'^\d+$', message="Số điện thoại chỉ được chứa các số.")

class Resident(User):
    room = models.OneToOneField(Room, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=11, validators=[phone_validator], unique=True)
    avatar = CloudinaryField()
    answered_surveys = models.ManyToManyField('Survey', related_name='answered_residents')

class ItemModel(BaseModel):
    active = models.BooleanField(default=True)
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Payment(ItemModel):
    amount = models.DecimalField(max_digits=11, decimal_places=2)

class Receipt(BaseModel):
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)

class SecurityCard(ItemModel):
    name_register = models.CharField(max_length=255)
    vehicle_number = models.CharField(max_length=15)

class Package(ItemModel):
    note = models.CharField(max_length=255)
    image = CloudinaryField()

class Complaint(ItemModel):
    content = RichTextField()
    image = CloudinaryField()

class Survey(BaseModel):
    description = RichTextField()
    active = models.BooleanField(default=True)

class QuestionSurvey(models.Model):
    content = RichTextField()
    created_date = models.DateTimeField(auto_now_add=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class AnswerSurvey(models.Model):
    content = RichTextField()
    created_date = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(QuestionSurvey, on_delete=models.CASCADE)
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class ResultSurvey(models.Model):
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionSurvey, on_delete=models.CASCADE)
    answer = models.ForeignKey(AnswerSurvey, on_delete=models.CASCADE)
