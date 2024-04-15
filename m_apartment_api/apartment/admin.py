from django.contrib import admin
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe

from apartment.models import User, Payment, Receipt, SecurityCard, Package, Complaint, Survey, QuestionSurvey, AnswerSurvey

class MyUserAdmin(admin.ModelAdmin):
    list_display =['username', 'first_name', 'last_name', 'email', 'is_active']

class MyPaymentAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'active', 'user']

class MyReceiptAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'payment', 'user']

class MySecurityCardAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_register', 'vehicle_number', 'active', 'user']

class MyPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'note', 'active', 'user']

class ComplaintForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Complaint
        fields = '__all__'

class MyComplaintAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_date', 'active', 'user']
    form = ComplaintForm

class SurveyForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Survey
        fields = '__all__'

class MySurveyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_date']
    form = SurveyForm

class MyQuestionSurveyForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = QuestionSurvey
        fields = '__all__'
class MyQuestionSurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_date', 'updated_date', 'survey']
    form = MyQuestionSurveyForm

class MyAnswerSurveyForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = AnswerSurvey
        fields = '__all__'

class MyAnswerSurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_date', 'updated_date', 'question', 'user']
    form = MyAnswerSurveyForm


# Register your models here.
admin.site.register(User, MyUserAdmin)
admin.site.register(Payment, MyPaymentAdmin)
admin.site.register(Receipt, MyReceiptAdmin)
admin.site.register(SecurityCard, MySecurityCardAdmin)
admin.site.register(Package, MyPackageAdmin)
admin.site.register(Complaint, MyComplaintAdmin)
admin.site.register(Survey, MySurveyAdmin)
admin.site.register(QuestionSurvey, MyQuestionSurveyAdmin)
admin.site.register(AnswerSurvey, MyAnswerSurveyAdmin)
