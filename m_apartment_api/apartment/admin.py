from django.contrib import admin
from django import forms
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe

from apartment.models import (Room, Resident, Payment, Receipt, SecurityCard, Package, Complaint,
                              Survey, QuestionSurvey, AnswerSurvey, ResultSurvey)

class MyApartmentAdminSite(admin.AdminSite):
    site_header = 'Apartment Administation'

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
    list_display = ['id', 'username', 'first_name', 'last_name', 'phone', 'room', 'is_active']
    list_filter = ['date_joined', 'is_active']
    search_fields = ['username']

class MyPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'amount', 'created_date', 'updated_date', 'active', 'resident']
    search_fields = ['name']
    list_filter = ['resident', 'active']

class MyReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'amount', 'created_date', 'payment', 'resident']
    search_fields = ['name']
    list_filter = ['created_date', 'resident']
    readonly_fields = ['name', 'amount', 'payment', 'resident']

class MySecurityCardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_register', 'vehicle_number', 'created_date', 'updated_date',
                    'active', 'resident']
    list_filter = ['created_date', 'active', 'resident']
    readonly_fields = ['name', 'name_register', 'vehicle_number', 'active', 'resident']

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
    readonly_fields = ['content', 'resident']
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
admin_site.register(AnswerSurvey, MyAnswerSurveyAdmin)
admin_site.register(ResultSurvey, MyResultSurveyAdmin)