from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apartment import serializers, paginators, perms
from django.contrib.auth.hashers import make_password
from apartment.models import (Resident, Room, Payment, Receipt, SecurityCard, Package, Complaint, Survey,
                              QuestionSurvey, AnswerSurvey, ResultSurvey)

class RoomViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Room.objects.filter(is_empty=True)
    serializer_class = serializers.RoomSerializer
    pagination_class = paginators.BasePaginator
    parser_classes = [parsers.MultiPartParser, ]

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        n = self.request.query_params.get('n')
        if n:
            queryset = queryset.filter(number__icontains=n)

        return queryset

    @receiver(post_save, sender=Resident)
    def update_room_on_create_resident(sender, instance, **kwargs):
        if instance.room:
            instance.room.is_empty = False
            instance.room.save()

    @receiver(post_delete, sender=Resident)
    def update_room_on_delete_resident(sender, instance, **kwargs):
        if instance.room:
            instance.room.is_empty = True
            instance.room.save()

class ResidentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView,
                      generics.DestroyAPIView):
    queryset = Resident.objects.filter(is_active=True)
    serializer_class = serializers.ResidentSerializer
    pagination_class = paginators.BasePaginator
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['destroy']:
            return [perms.IsStaff()]
        elif self.action == 'update_profile':
            return [perms.Owner()]
        return [permissions.AllowAny()]

    @action(methods=['patch'], url_path='profile', detail=True)
    def update_profile(self, request, pk):
        print(self.action)
        resident = self.get_object()
        for k, v in request.data.items():
            if k == 'password':
                v = make_password(v)
            setattr(resident, k, v)
        resident.save()

        return Response(serializers.ResidentSerializer(resident).data)

class SecurityCardViewSet(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView):
    queryset = SecurityCard.objects.filter(active=True)
    serializer_class = serializers.SecurityCardSerializer
    pagination_class = paginators.BasePaginator

    def get_permissions(self):
        if self.action in ['create_sc', 'updated_sc', 'destroy']:
            return [perms.Owner()]

        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = self.queryset

        user_id = self.request.query_params.get('resident_id')
        if user_id:
            queryset = queryset.filter(resident_id=user_id)

        return queryset

    @action(methods=['post'], url_path='add-sc', detail=False)
    def create_sc(self, request):
        sc = SecurityCard.objects.create(name=request.data.get('name'), name_register=request.data.get('name_register'),
                                         vehicle_number=request.data.get('vehicle_number'),
                                         resident_id=request.user.id)
        return Response(serializers.SecurityCardSerializer(sc).data, status=status.HTTP_201_CREATED)

    @action(methods=['patch'], url_path='update-sc', detail=True)
    def updated_sc(self, request, pk):
        sc = self.get_object()
        for k, v in request.data.items():
            setattr(sc, k, v)
        sc.save()

        return Response(serializers.SecurityCardSerializer(sc).data, status=status.HTTP_200_OK)

class PaymentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = serializers.PaymentSerializer
    pagination_class = paginators.BasePaginator

    def get_permissions(self):
        if self.action == 'paid':
            return [perms.Owner()]

        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        r_id = self.request.query_params.get('r_id')
        if r_id:
            queryset = queryset.filter(resident_id=r_id)

        return queryset

    @action(methods=['post'], url_path='paid', detail=True)
    def paid(self, request, pk):
        pay = self.get_object()
        setattr(pay, 'active', '0')
        Receipt.objects.create(name=f'Hóa đơn {pay.name}', amount=pay.amount, payment=pay,
                               resident=pay.resident)
        pay.save()

        return Response(serializers.PaymentSerializer(pay).data)

class ReceiptViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Receipt.objects.all()
    serializer_class = serializers.ReceiptSerializer
    paginator_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        r_id = self.request.query_params.get('r_id')
        if r_id:
            queryset = queryset.filter(resident_id=r_id)

        return queryset

class PackageViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Package.objects.filter(active=True)
    serializer_class = serializers.PackageSerializer
    pagination_class = paginators.BasePaginator
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['received_package']:
            return [perms.IsStaff()]

        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        r_id = self.request.query_params.get('r_id')
        if r_id:
            queryset = queryset.filter(resident_id=r_id)

        return queryset

    @action(methods=['post'], url_path='received', detail=True)
    def received_package(self, request, pk):
        p = self.get_object()
        setattr(p, 'active', '0')
        p.save()

        return Response(serializers.PackageSerializer(p).data, status=status.HTTP_202_ACCEPTED)
#
class ComplaintViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Complaint.objects.all()
    serializer_class = serializers.ComplaintSerializer
    pagination_class = paginators.BasePaginator
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action == 'add_complaint':
            return [perms.Owner()]
        elif self.action == 'handle_complaint':
            return [perms.IsStaff()]

        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        r_id = self.request.query_params.get('r_id')
        if r_id:
            queryset = queryset.filter(resident_id=r_id)

        return queryset

    @action(methods=['post'], url_path='create-complaint', detail=False)
    def add_complaint(self, request):
        comp = Complaint.objects.create(name=request.data.get('name'), content=request.data.get('content'),
                                        image=request.data.get('image'), resident_id=request.user.id)
        return Response(serializers.ComplaintSerializer(comp).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], url_path='handle-complaint', detail=True)
    def handle_complaint(self, request, pk):
        comp = self.get_object()
        setattr(comp, 'active', '0')
        comp.save()

        return Response(serializers.ComplaintSerializer(comp).data, status=status.HTTP_202_ACCEPTED)
#
class SurveyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = serializers.SurveySerializer
    pagination_class = paginators.BasePaginator

    def get_permissions(self):
        if self.action == 'fill_answer':
            return [permissions.IsAuthenticated()]
        elif self.action == 'add_question':
            return [perms.IsStaff()]

        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        d = self.request.query_params.get('d')
        if d:
            queryset = queryset.filter(description__icontains=d)

        return queryset
    @action(methods=['post'], url_path='questions', detail=True)
    def add_question(self, request, pk):
        question = QuestionSurvey.objects.create(content=request.data.get('content'),
                                                 survey=self.get_object())
        return Response(serializers.QuestionSurveySerializer(question).data, status=status.HTTP_201_CREATED)

    # Kiểm tra cư dân đã thực hiện khảo sát này chưa
    @staticmethod
    def is_resident_completed_survey(survey, resident):
        return survey in resident.answered_surveys.all()

    # Kiểm tra cư dân đã thực hiện trả lời câu hỏi này chưa này chưa
    @staticmethod
    def is_resident_answered_question(resident_id, question_id):
        return AnswerSurvey.objects.filter(resident_id=resident_id, question_id=question_id).exists()

    # Câu hỏi có tồn tại trong khảo sát, trả về True nếu đúng
    @staticmethod
    def is_question_in_survey(question_id, survey_id):
        return QuestionSurvey.objects.filter(id=question_id, survey_id=survey_id).exists()

    # Các câu hỏi trong khảo sát đã được trả lời hết chưa, trả về True nếu đúng
    @staticmethod
    def is_all_questions_answered(survey, resident_id):
        # tạo biến gồm các câu hỏi chưa được trả lời
        unanswered_questions = (QuestionSurvey.objects.filter(survey_id=survey.id).
                                exclude(answersurvey__resident_id=resident_id))
        return not unanswered_questions.exists()

    # Thêm khảo sát vừa thực hiện vào danh sách các khảo sát đã trả lời của Resident
    @staticmethod
    def add_survey_for_resident(resident, survey):
        resident.answered_surveys.add(survey)
        # resident.answered_surveys.add(resident)

    @action(methods=['post'], url_path='(?P<question_id>[^/.]+)/answers', detail=True)
    def fill_answer(self, request, pk, question_id):
        resident_check = Resident.objects.get(id=request.user.id)
        survey_check = Survey.objects.get(id=pk)

        # Kiểm tra cư dân đã thực hiện khảo sát này chưa
        if self.is_resident_completed_survey(survey_check, resident_check):
            return Response(status=status.HTTP_208_ALREADY_REPORTED)

        # Kiểm tra Câu hỏi có tồn tại trong khảo sát không
        if not self.is_question_in_survey(question_id, pk):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Kiểm tra cư dân đã trả lời câu hỏi này chưa
        if self.is_resident_answered_question(request.user.id, question_id):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Gửi câu trả lời lên hệ thống
        answer = AnswerSurvey.objects.create(content=request.data.get('content'),
                                             question_id=question_id, resident_id=request.user.id)

        # Cập nhật kết quả khảo sát
        self.get_object().resultsurvey_set.create(answer_id=answer.id, question_id=question_id,
                                    resident_id=request.user.id)

        # Kiểm tra Các câu hỏi trong khảo sát đã được trả lời hết chưa, trả về True nếu đúng
        if self.is_all_questions_answered(survey_check, request.user.id):
            # Thêm khảo sát vừa thực hiện vào danh sách các khảo sát đã trả lời của Resident
            self.add_survey_for_resident(resident_check, survey_check)

        return Response(serializers.AnswerSurveySerializer(answer).data, status=status.HTTP_200_OK)

class QuestionSurveyViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = QuestionSurvey.objects.all()
    serializer_class = serializers.QuestionSurveySerializer
    pagination_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        s = self.request.query_params.get('s')
        if s:
            queryset = queryset.filter(survey=s)

        return queryset

class AnswerSurveyViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = AnswerSurvey.objects.all()
    serializer_class = serializers.AnswerSurveySerializer
    pagination_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(question=q)

        return queryset

class ResultSurveyViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = ResultSurvey.objects.all()
    serializer_class = serializers.ResultSurveySerializer
    pagination_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        s = self.request.query_params.get('s')
        if s:
            queryset = queryset.filter(survey=s)

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(question=q)

        r_id = self.request.query_params.get('r_id')
        if r_id:
            queryset = queryset.filter(resident_id=r_id)

        return queryset