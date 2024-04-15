from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField

# Create your models here.

# class Room(models.Model):
#     name = models.CharField(max_length=10)
#     created_date =models.DateTimeField(auto_now_add=True, null=True)
#     updated_date =models.DateTimeField(auto_now=True, null=True)
#     active = models.BooleanField(default=True)
#     is_hired = models.BooleanField(default=False)
#     description = RichTextField()
#     amount = models.DecimalField(max_digits=9, decimal_places=7)
#     number_of_people = models.DecimalField(max_digits=2, decimal_places=1)

class User(AbstractUser):
    avatar = CloudinaryField(null=True)
    # room = models.ForeignKey(Room, on_delete=models.CASCADE)

class BaseModel(models.Model):
    name = models.CharField(max_length=255)
    created_date =models.DateTimeField(auto_now_add=True)
    updated_date =models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

class ItemModel(BaseModel):
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

# class Furniture(BaseModel):
#     status_choices = (('good', 'Good'), ('bad', 'Bad'))
#     status = models.CharField(max_length=4, choices=status_choices, default='Good')
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)

class Payment(ItemModel):
    amount = models.DecimalField(max_digits=13, decimal_places=4)
    deadline_date = models.DateTimeField()

class Receipt(BaseModel):
    amount = models.DecimalField(max_digits=13, decimal_places=4)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class SecurityCard(ItemModel):
    name_register = models.CharField(max_length=255)
    vehicle_number = models.CharField(max_length=15)

class Package(ItemModel):
    note = models.CharField(max_length=255)
    image = CloudinaryField(null=True)

class Complaint(ItemModel):
    content = RichTextField()
    image = CloudinaryField(null=True)

class Survey(BaseModel):
    description = RichTextField()

class QuestionSurvey(models.Model):
    content = RichTextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

class AnswerSurvey(models.Model):
    content = RichTextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    question = models.ForeignKey(QuestionSurvey, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
