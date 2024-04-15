from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers
from apartment import views

r = routers.DefaultRouter()
r.register('users', views.UserViewSet, basename='users')
r.register('payments', views.PaymentViewSet, basename='payments')
r.register('receipts', views.ReceiptViewSet, basename='receipts')
r.register('security_cards', views.SecurityCardViewSet, basename='security_cards')
r.register('packages', views.PackageViewSet, basename='packages')
r.register('complaints', views.ComplaintViewSet, basename='complaints')
r.register('surveys', views.SurveyViewSet, basename='surveys')
r.register('s_questions', views.QuestionSurveyViewSet, basename='s_questions')
r.register('s_answers', views.AnswerSurveyViewSet, basename='s_answers')


urlpatterns = [
    path('', include(r.urls))
]