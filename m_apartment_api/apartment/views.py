from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apartment import serializers, paginators
from apartment.models import User, Payment, Receipt, SecurityCard, Package, Complaint, Survey, QuestionSurvey, AnswerSurvey

class PermissionsViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['get_current_user', 'paid', 'updated_sc', 'add_complaint',
                           'updated_complaint', 'fill_answer']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

class UserViewSet(PermissionsViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                setattr(user, k, v)
            user.save()

        return Response(serializers.UserSerializer(user).data)

class PaymentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = serializers.PaymentSerializer
    pagination_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    @action(methods=['patch'],url_path='paid', detail=True)
    def paid(self, request, pk):
        pay = Payment.objects.get(pk=pk)
        if pay.user != request.user:
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        for k, v in request.data.items():
            setattr(pay, k, v)
        pay.save()

        return Response(serializers.PaymentSerializer(pay).data, status=status.HTTP_200_OK)

class ReceiptViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Receipt.objects.all()
    serializer_class = serializers.ReceiptSerializer
    paginator_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

class SecurityCardViewSet(PermissionsViewSet, generics.ListAPIView):
    queryset = SecurityCard.objects.filter(active=True)
    serializer_class = serializers.SecurityCardSerializer
    paginator_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    @action(methods=['post'], url_path='create-sc', detail=False)
    def add_sc(self, request):
        sc = SecurityCard.objects.create(name=request.data.get('name'),
                                         name_register=request.data.get('name_register'),
                                         vehicle_number=request.data.get('vehicle_number'), user=request.user)
        return Response(serializers.SecurityCardSerializer(sc).data)

    @action(methods=['patch'], url_path='update-sc', detail=True)
    def updated_sc(self, request, pk):
        sc = SecurityCard.objects.get(pk=pk)
        if sc.user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        for k, v in request.data.items():
            setattr(sc, k, v)
        sc.save()

        return Response(serializers.SecurityCardSerializer(sc).data, status=status.HTTP_200_OK)

class PackageViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Package.objects.filter(active=True)
    serializer_class = serializers.PackageSerializer
    pagination_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    @action(methods=['patch'], url_path='update', detail=True)
    def updated_package(self, request, pk):
        p = self.get_object()
        for k, v in request.data.items():
            setattr(p, k, v)
        p.save()

        return Response(serializers.PackageSerializer(p).data, status=status.HTTP_200_OK)

class ComplaintViewSet(PermissionsViewSet, generics.ListAPIView):
    queryset = Complaint.objects.filter(active=True)
    serializer_class = serializers.ComplaintSerializer
    pagination_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    @action(methods=['post'], url_path='create-complaint', detail=False)
    def add_complaint(self, request):
        comp = Complaint.objects.create(name=request.data.get('name'), content=request.data.get('content'),
                                        image=request.data.get('image'), user=request.user)
        return Response(serializers.ComplaintSerializer(comp).data)

    @action(methods=['patch'], url_path='edit-complaint', detail=True)
    def updated_complaint(self, request, pk):
        comp = self.get_object()
        if comp.user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        for k, v in request.data.items():
            setattr(comp, k, v)
        comp.save()

        return Response(serializers.ComplaintSerializer(comp).data, status=status.HTTP_200_OK)

    @action(methods=['patch'], url_path='handle-complaint', detail=True)
    def handle_complaint(self, request, pk):
        comp = self.get_object()
        setattr(comp, 'active', '0')
        comp.save()

        return Response(serializers.ComplaintSerializer(comp).data, status=status.HTTP_200_OK)

class SurveyViewSet(PermissionsViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = serializers.SurveySerializer
    pagination_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        return queryset

    @action(methods=['post'], url_path='questions', detail=True)
    def create_question(self, request, pk):
        question = QuestionSurvey.objects.create(content=request.data.get('content'), survey=self.get_object())
        return Response(serializers.QuestionSurveySerializer(question).data, status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='answers', detail=True)
    def fill_answer(self, request, pk):
        answer = AnswerSurvey.objects.create(content=request.data.get('content'),
                                             question_id=request.data.get('question_id'), user=request.user)
        return Response(serializers.AnswerSurveySerializer(answer).data, status=status.HTTP_200_OK)

class QuestionSurveyViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = QuestionSurvey.objects.all()
    serializer_class = serializers.QuestionSurveySerializer
    pagination_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        survey = self.request.query_params.get('survey')
        if survey:
            queryset = queryset.filter(survey__icontains=survey)

        return queryset

class AnswerSurveyViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = AnswerSurvey.objects.all()
    serializer_class = serializers.AnswerSurveySerializer
    pagination_class = paginators.BasePaginator

    def get_queryset(self):
        queryset = self.queryset

        question = self.request.query_params.get('question')
        if question:
            queryset = queryset.filter(question_icontains=question)

        return queryset
