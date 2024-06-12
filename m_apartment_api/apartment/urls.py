from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers
from apartment import views

r = routers.DefaultRouter()
r.register('rooms', views.RoomViewSet, basename='rooms')
r.register('residents', views.ResidentViewSet, basename='residents')
r.register('users', views.UserViewSet, basename='users')
r.register('payments', views.PaymentViewSet, basename='payments')
r.register('momo_links', views.MomoLinkViewSet, basename='momo_links')
r.register('momo_paids', views.MomoPaidViewSet, basename='momo_paids')
r.register('vnpay_links', views.VnpayLinkViewSet, basename='vnpay_links')
r.register('vnpay_paids', views.VnpayPaidViewSet, basename='vnpay_paids')
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
    path('paid', views.save_payment, name='paid')
    # path('admin/', admin.site.urls),
]