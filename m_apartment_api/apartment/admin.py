import site

from django.contrib import admin
from django import forms
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group, Permission
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe
from apartment.models import (Room, Resident, Payment, Receipt, SecurityCard, Package, Complaint, Survey, QuestionSurvey,
                              AnswerSurvey, ResultSurvey, Notification, MomoLink, MomoPaid, VnpayLink, VnpayPaid)

class MyApartmentAdminSite(admin.AdminSite):
    site_header = 'HỆ THỐNG QUẢN LÝ CHUNG CƯ'

    def get_urls(self):
        return [path('survey-stats/', self.stats_view)] + super().get_urls()

    def stats_view(self, request):
        # Đếm tổng số câu hỏi có trong 1 phiếu khảo sát
        question_stats = (Survey.objects.annotate(question_count = Count('questionsurvey__id')).
                          values('id', 'name', 'question_count'))
        # Đếm tổng số câu trả lời có trong 1 câu hỏi
        answer_stats = (QuestionSurvey.objects.annotate(answer_count = Count('answersurvey__content', distinct=True)).
                        values('id', 'content', 'answer_count'))
        # Đếm tổng số người thực hiện 1 phiếu khảo sát
        resident_stats = (Survey.objects.annotate(resident_count= Count('answered_residents')).
                          values('id', 'name', 'resident_count'))
        return TemplateResponse(request, 'admin/stats.html', {
            'question_stats': question_stats,
            'answer_stats': answer_stats,
            'resident_stats': resident_stats
        })


admin_site = MyApartmentAdminSite(name='MyAdmin')

class MyRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'number', 'description', 'square', 'is_empty']
    search_fields = ['description']
    list_filter = ['square', 'is_empty']
    readonly_fields = ['is_empty']

class MyResidentAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'gender', 'phone', 'room', 'is_active']
    list_filter = ['date_joined', 'is_active']
    search_fields = ['username']
    readonly_fields = ['answered_surveys']

class MyNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_date', 'updated_date', 'active']
    search_fields = ['name', 'content']
    list_filter = ['name']

class MyPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'amount', 'created_date', 'updated_date', 'active', 'resident']
    search_fields = ['name']
    list_filter = ['resident', 'active']

class MyReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_id', 'pay_type', 'name', 'amount', 'created_date', 'payment', 'resident']
    search_fields = ['name']
    list_filter = ['created_date', 'resident']
    readonly_fields = ['name', 'amount', 'payment', 'resident']

class MySecurityCardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_register', 'vehicle_number', 'type_vehicle', 'created_date',
                    'updated_date', 'active', 'resident']
    list_filter = ['created_date', 'active', 'resident']

class MyPackageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'note', 'created_date', 'updated_date', 'active', 'resident']
    search_fields = ['name']
    list_filter = ['created_date', 'active', 'resident']

class ComplaintForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Complaint
        fields = '__all__'

class MyComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'content', 'created_date', 'active', 'resident']
    readonly_fields = ['name', 'content', 'resident']
    search_fields = ['name']
    list_filter = ['resident', 'active']
    form = ComplaintForm

class SurveyForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Survey
        fields = '__all__'

class MySurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'created_date', 'updated_date', 'active']
    list_filter = ['created_date', 'updated_date', 'active']
    search_fields = ['name']
    form = SurveyForm

class MyQuestionSurveyForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = QuestionSurvey
        fields = '__all__'
class MyQuestionSurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'content', 'created_date', 'survey']
    list_filter = ['created_date', 'survey']
    form = MyQuestionSurveyForm

class MyAnswerSurveyForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = AnswerSurvey
        fields = '__all__'

class MyAnswerSurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'content', 'question', 'created_date', 'resident']
    readonly_fields = ['content', 'question', 'resident']
    list_filter = ['resident']
    form = MyAnswerSurveyForm

class MyResultSurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'survey', 'question', 'answer', 'resident']
    readonly_fields = ['survey', 'question', 'answer', 'resident']
    list_filter = ['survey', 'resident']

class MyMomoLinkAdmin(admin.ModelAdmin):
    list_display = ['partner_code', 'order_id', 'amount', 'payment', 'resident', 'pay_url']
    readonly_fields = ['partner_code', 'order_id', 'amount', 'payment', 'resident', 'pay_url']

class MyMomoPaidAdmin(admin.ModelAdmin):
    list_display = ['partner_code', 'order_id', 'amount', 'created_date', 'order_type', 'pay_type']
    readonly_fields = ['partner_code', 'order_id', 'amount', 'created_date', 'order_type', 'pay_type']

class MyVnpayLinkAdmin(admin.ModelAdmin):
    list_display = ['txn_ref', 'amount', 'created_date', 'payment', 'resident', 'payment_url']
    readonly_fields = ['txn_ref', 'amount', 'created_date', 'payment', 'resident', 'payment_url']

class MyVnpayPaidAdmin(admin.ModelAdmin):
    list_display = ['txn_ref', 'amount', 'created_date', 'bank_code', 'card_type']
    readonly_fields = ['txn_ref', 'amount', 'created_date', 'bank_code', 'card_type']

# Register your models here.
admin_site.register(Room, MyRoomAdmin)
admin_site.register(Resident, MyResidentAdmin)
admin_site.register(Payment, MyPaymentAdmin)
admin_site.register(Receipt, MyReceiptAdmin)
admin_site.register(SecurityCard, MySecurityCardAdmin)
admin_site.register(Package, MyPackageAdmin)
admin_site.register(Complaint, MyComplaintAdmin)
admin_site.register(Survey, MySurveyAdmin)
admin_site.register(QuestionSurvey, MyQuestionSurveyAdmin)
admin_site.register(Notification, MyNotificationAdmin)
admin_site.register(AnswerSurvey, MyAnswerSurveyAdmin)
admin_site.register(ResultSurvey, MyResultSurveyAdmin)
admin_site.register(MomoLink, MyMomoLinkAdmin)
admin_site.register(MomoPaid, MyMomoPaidAdmin)
admin_site.register(VnpayLink, MyVnpayLinkAdmin)
admin_site.register(VnpayPaid, MyVnpayPaidAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Permission)