from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers
from apartment import views

r = routers.DefaultRouter()
r.register('rooms', views.RoomViewSet, basename='rooms')
r.register('residents', views.ResidentViewSet, basename='residents')
r.register('payments', views.PaymentViewSet, basename='payments')
r.register('receipts', views.ReceiptViewSet, basename='receipts')
r.register('security_cards', views.SecurityCardViewSet, basename='security_cards')
r.register('packages', views.PackageViewSet, basename='packages')
r.register('complaints', views.ComplaintViewSet, basename='complaints')
r.register('surveys', views.SurveyViewSet, basename='surveys')
r.register('survey_questions', views.QuestionSurveyViewSet, basename='questions')
r.register('survey_answers', views.AnswerSurveyViewSet, basename='answers')
r.register('survey_results', views.ResultSurveyViewSet, basename='results')
r.register('notifications', views.NotificationViewSet, basename='notifs')

urlpatterns = [
    path('', include(r.urls)),
    # vn pay
    path('pay', views.index, name='index'),
    path('payment', views.payment, name='payment'),
    path('payment_ipn', views.payment_ipn, name='payment_ipn'),
    path('payment_return', views.payment_return, name='payment_return'),
    path('query', views.query, name='query'),
    path('refund', views.refund, name='refund'),
    # path('admin/', admin.site.urls),
]