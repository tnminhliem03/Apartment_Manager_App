import re

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from vnpay.utils import VnPay
from apartment import serializers, paginators, perms
from m_apartment_api import settings
from django.contrib.auth.hashers import make_password
from apartment.models import (Resident, User, Room, Payment, Receipt, SecurityCard, Package, Complaint, Survey,
                              QuestionSurvey, AnswerSurvey, ResultSurvey, Notification, PaymentForm, MomoPaid,
                              MomoLink, VnpayLink, VnpayPaid)
# momo
import uuid

# vnpay
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import random
import requests
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpRequest
from django.shortcuts import render, redirect
from django.utils.http import unquote
from apartment.vnpay import vnpay

vnp = vnpay()

def check_active_payment(payment):
    if (payment.active == 1):
        return 1

def check_receipt(order_id):
    if Receipt.objects.filter(order_id=order_id).exists():
        return 0
    return 1

def update_active_payment(payment):
    if check_active_payment(payment):
        setattr(payment, 'active', '0')
        payment.save()

def create_receipt(payment, order_id, pay_type):
    Receipt.objects.create(name=f'Hóa đơn {payment.name}', amount=payment.amount, payment=payment,
                           resident=payment.resident, order_id=order_id, pay_type=pay_type)

# momo
def create_signature(rawSignature):
    h = hmac.new(bytes(settings.MOMO_SECRET_KEY, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()
    return signature

def create_link_momo(payment):
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    orderInfo = "Thanh toan hoa don bang Momo"
    redirectUrl = settings.MOMO_RETURN_URL
    ipnUrl = settings.MOMO_RETURN_URL
    amount = payment.amount
    orderId = "MOMO" + ''.join(filter(str.isdigit, str(uuid.uuid4())))
    requestId = "MOMO" + ''.join(filter(str.isdigit, str(uuid.uuid4())))
    extraData = ""  # pass empty value or Encode base64 JsonString
    partnerName = "Chung cu LK"
    requestType = "payWithMethod"
    storeId = "LK Payment"
    orderGroupId = ""
    autoCapture = True
    lang = "vi"
    orderGroupId = ""

    # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
    # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
    # &requestType=$requestType
    rawSignature = "accessKey=" + settings.MOMO_ACCESS_KEY + "&amount=" + str(amount) + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId \
                   + "&orderInfo=" + orderInfo + "&partnerCode=" + settings.MOMO_PARTNER_CODE + "&redirectUrl=" + redirectUrl \
                   + "&requestId=" + requestId + "&requestType=" + requestType
    # signature
    signature = create_signature(rawSignature)

    # json object send to MoMo endpoint

    data = {
        'partnerCode': settings.MOMO_PARTNER_CODE,
        'orderId': orderId,
        'partnerName': partnerName,
        'storeId': storeId,
        'ipnUrl': ipnUrl,
        'amount': amount,
        'lang': lang,
        'requestType': requestType,
        'redirectUrl': redirectUrl,
        'autoCapture': autoCapture,
        'orderInfo': orderInfo,
        'requestId': requestId,
        'extraData': extraData,
        'signature': signature,
        'orderGroupId': orderGroupId
    }
    data = json.dumps(data)
    clen = len(data)
    response = requests.post(endpoint, data=data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

    print(response.json())

    return response.json()

def save_payment(request):
    # momo
    check_momo = request.GET.get('partnerCode', None)
    order_id = request.GET.get('orderId')

    # vnpay
    check_vnp = request.GET.get('vnp_Amount', None)
    txn_ref = request.GET.get('vnp_TxnRef')

    if check_momo is not None and not MomoPaid.objects.filter(order_id=order_id):
        momo_link = MomoLink.objects.get(order_id=order_id)
        payment_momo = momo_link.payment
        MomoPaid.objects.create(partner_code=request.GET.get('partnerCode'), order_id=order_id,
                            request_id=request.GET.get('requestId'), amount=request.GET.get('amount'),
                            order_info=request.GET.get('orderInfo'), order_type=request.GET.get('orderType'),
                            trans_id=request.GET.get('transId'), pay_type=request.GET.get('payType'),
                            signature=request.GET.get('signature'))

        if check_receipt(order_id) and check_active_payment(payment_momo):
            create_receipt(payment_momo, order_id, "momo")
            update_active_payment(payment_momo)

    elif check_vnp is not None and not VnpayPaid.objects.filter(txn_ref=txn_ref):
        vnpay_link = VnpayLink.objects.get(txn_ref=txn_ref)
        payment_vnp = vnpay_link.payment
        VnpayPaid.objects.create(txn_ref=txn_ref, amount=request.GET.get('vnp_Amount'),
                                 order_info=request.GET.get('vnp_OrderInfo'),
                                 bank_code=request.GET.get('vnp_BankCode'),
                                 bank_tran_no=request.GET.get('vnp_BankTranNo'),
                                 card_type=request.GET.get('vnp_CardType'),
                                 pay_date=request.GET.get('vnp_PayDate'),
                                 response_code=request.GET.get('vnp_ResponseCode'),
                                 tmn_code=request.GET.get('vnp_TmnCode'),
                                 transaction_no=request.GET.get('vnp_TransactionNo'),
                                 transaction_status=request.GET.get('vnp_TransactionStatus'),
                                 secure_hash=request.GET.get('vnp_SecureHash'))

        if check_receipt(txn_ref) and check_active_payment(payment_vnp):
            create_receipt(payment_vnp, txn_ref, "vnpay")
            update_active_payment(payment_vnp)

    return render(request, "payment/paid.html")

def transaction_status(orderId, requestId):
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/query"
    rawSignature = "accessKey=" + settings.MOMO_ACCESS_KEY + "&orderId=" + orderId + "&partnerCode=" + settings.MOMO_PARTNER_CODE + "&requestId=" + requestId

    signature = create_signature(rawSignature)

    data = {
        'partnerCode': settings.MOMO_PARTNER_CODE,
        'orderId': orderId,
        'lang': 'vi',
        'requestId': requestId,
        'signature': signature,
    }
    data = json.dumps(data)
    clen = len(data)
    response = requests.post(endpoint, data=data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    return response.json()

# vnpay
def create_link_vnpay(request, payment):
    order_type = "billpayment"
    order_id = "VNP" + ''.join(filter(str.isdigit, str(uuid.uuid4())))
    amount = payment.amount
    order_desc = "Thanh toan hoa don bang VnPay"
    bank_code = request.data.get('bank_code')
    language = "vn"
    ipaddr = get_client_ip(request)
    # Build URL Payment
    vnp.requestData['vnp_Version'] = '2.1.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
    vnp.requestData['vnp_Amount'] = int(amount) * 100
    vnp.requestData['vnp_CurrCode'] = 'VND'
    vnp.requestData['vnp_TxnRef'] = order_id
    vnp.requestData['vnp_OrderInfo'] = order_desc
    vnp.requestData['vnp_OrderType'] = order_type
    # Check language, default: vn
    if language and language != '':
        vnp.requestData['vnp_Locale'] = language
    else:
        vnp.requestData['vnp_Locale'] = 'vn'
        # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
    if bank_code and bank_code != "":
        vnp.requestData['vnp_BankCode'] = bank_code

    vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp.requestData['vnp_IpAddr'] = ipaddr
    vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
    vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
    payment_data = {
        'vnp_TxnRef': order_id,
        'vnp_Amount': amount,
        'vnp_OrderInfo': order_desc,
        'vnp_OrderType': order_type,
        'language': language,
        'vnp_IpAddr': ipaddr,
        'payment_url': vnpay_payment_url
    }

    return payment_data

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

n = random.randint(10**11, 10**12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str

# Myapp
def create_payment(name, amount, resident_id):
    Payment.objects.create(name=name, amount=amount, resident_id=resident_id)

def type_vehicle_create_pay(sc):
    if sc.type_vehicle == 'bike':
        create_payment('Phí gửi xe đạp tháng', '900000', sc.resident.id)
    elif sc.type_vehicle == 'motorbike':
        create_payment('Phí gửi xe máy tháng', '150000', sc.resident.id)
    elif sc.type_vehicle == 'car':
        create_payment('Phí gửi xe hơi tháng', '1600000', sc.resident.id)

class RoomViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Room.objects.all()
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

class UserViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = serializers.UserSerializer
    pagination_class = paginators.BasePaginator
    parser_classes = [parsers.MultiPartParser, ]

class ResidentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Resident.objects.filter(is_active=True)
    serializer_class = serializers.ResidentSerializer
    pagination_class = paginators.BasePaginator
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action == 'update_profile':
            return [perms.Owner()]
        elif self.action == 'get_current_resident':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get'], url_path='current', detail=False)
    def get_current_resident(self, request):
        return Response(serializers.ResidentSerializer(request.user.resident).data)

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

class SecurityCardViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = SecurityCard.objects.filter(active=True)
    serializer_class = serializers.SecurityCardSerializer
    pagination_class = paginators.BasePaginator

    def get_permissions(self):
        if self.action in ['create_sc', 'updated_sc']:
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
        sc = SecurityCard.objects.create(name=request.data.get('name'),
                                         name_register=request.data.get('name_register'),
                                         vehicle_number=request.data.get('vehicle_number'),
                                         type_vehicle = request.data.get('type_vehicle'),
                                         resident_id=request.user.id)
        type_vehicle_create_pay(sc)

        return Response(serializers.SecurityCardSerializer(sc).data, status=status.HTTP_201_CREATED)

    @action(methods=['patch'], url_path='update-sc', detail=True)
    def updated_sc(self, request, pk):
        sc = self.get_object()
        for k, v in request.data.items():
            setattr(sc, k, v)
        sc.save()

        return Response(serializers.SecurityCardSerializer(sc).data, status=status.HTTP_200_OK)

class NotificationViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    pagination_class = paginators.BasePaginator

class MomoLinkViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = MomoLink.objects.all()
    serializer_class = serializers.MomoLinkSerializer
    pagination_class = paginators.BasePaginator

class MomoPaidViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = MomoPaid.objects.all()
    serializer_class = serializers.MomoPaidSerializer
    pagination_class = paginators.BasePaginator

class VnpayLinkViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = VnpayLink.objects.all()
    serializer_class = serializers.VnpayLinkSerializer
    pagination_class = paginators.BasePaginator

class VnpayPaidViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = VnpayPaid.objects.all()
    serializer_class = serializers.VnpayPaidSerializer
    pagination_class = paginators.BasePaginator

class PaymentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = serializers.PaymentSerializer
    pagination_class = paginators.BasePaginator

    def get_permissions(self):
        if self.action in ['get_current_payment', 'create_link_momo', 'create_link_vnp']:
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

    @action(methods=['get'], url_path='current', detail=True)
    def get_current_payment(self, request, pk):
        current_pay = serializers.PaymentSerializer(self.get_object()).data
        return Response(current_pay)

    # momo
    @action(methods=['post'], url_path='paid-momo', detail=True)
    def create_link_momo(self, request, pk):
        pay_momo_view = self.get_object()
        if check_active_payment(pay_momo_view):
            pay_momo_data = create_link_momo(pay_momo_view)
            if MomoLink.objects.filter(payment=pay_momo_view):
                return Response({"error": "Đã tồn tại link thanh toán"}, status=status.HTTP_200_OK)
            else:
                MomoLink.objects.create(partner_code=pay_momo_data['partnerCode'], order_id=pay_momo_data['orderId'],
                                        request_id=pay_momo_data['requestId'], amount=pay_momo_data['amount'],
                                        pay_url=pay_momo_data['payUrl'], short_link=pay_momo_data['shortLink'],
                                        resident_id=request.user.id, payment=pay_momo_view)
        else:
            return Response({"error": "Hóa đơn đã được thanh toán trước đó!"}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK, data=pay_momo_data)

    @action(methods=['post'], url_path='transaction-status', detail=False)
    def check_transaction_status(self, request):
        order_id = request.data.get('order_id')
        request_id = request.data.get('request_id')
        status_momo_data = transaction_status(order_id, request_id)
        return Response(status=status.HTTP_200_OK, data=status_momo_data)

    # vnpay
    @action(methods=['post'], url_path='paid-vnp', detail=True)
    def create_link_vnp(self, request, pk):
        pay_vnp_view = self.get_object()
        if check_active_payment(pay_vnp_view):
            pay_vnp_data = create_link_vnpay(request, pay_vnp_view)
            if VnpayLink.objects.filter(payment=pay_vnp_view):
                return Response({"error": "Đã tồn tại link thanh toán"}, status=status.HTTP_200_OK)
            else:
                VnpayLink.objects.create(txn_ref=pay_vnp_data['vnp_TxnRef'], amount=pay_vnp_data['vnp_Amount'],
                                         order_info=pay_vnp_data['vnp_OrderInfo'], order_type=pay_vnp_data['vnp_OrderType'],
                                         ip_addr=pay_vnp_data['vnp_IpAddr'], payment=pay_vnp_view,
                                         resident_id=request.user.id, payment_url=pay_vnp_data['payment_url'])
        else:
            return Response({"error": "Hóa đơn đã được thanh toán trước đó!"}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK, data = pay_vnp_data)

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

    @action(methods=['get'], url_path='current', detail=True)
    def get_current_receipt(self, request, pk):
        current_receipt = serializers.ReceiptSerializer(self.get_object()).data
        return Response(current_receipt)

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
    def is_resident_completed_survey(survey_id, resident_id):
        return survey_id in resident_id.answered_surveys.all()

    # Kiểm tra cư dân đã trả lời câu hỏi này chưa
    @staticmethod
    def is_resident_answered_question(resident_id, question_id):
        return ResultSurvey.objects.filter(resident_id=resident_id, question_id=question_id).exists()

    # Câu hỏi có tồn tại trong khảo sát, trả về True nếu đúng
    @staticmethod
    def is_question_in_survey(question_id, survey_id):
        return QuestionSurvey.objects.filter(id=question_id, survey_id=survey_id).exists()

    # Các câu hỏi trong khảo sát đã được trả lời hết chưa, trả về True nếu đúng
    @staticmethod
    def is_all_questions_answered(survey_id, resident_id):
        # tạo biến gồm các câu hỏi chưa được trả lời
        unanswered_questions = (QuestionSurvey.objects.filter(survey_id=survey_id).
                                exclude(answersurvey__resident_id=resident_id))
        return not unanswered_questions.exists()

    # Thêm khảo sát vừa thực hiện vào danh sách các khảo sát đã trả lời của Resident
    @staticmethod
    def add_survey_for_resident(resident, survey):
        resident.answered_surveys.add(survey)

    @action(methods=['post'], url_path='(?P<question_id>[^/.]+)/answers', detail=True)
    def fill_answer(self, request, pk, question_id):
        resident_check = Resident.objects.get(id=request.user.id)
        survey_check = Survey.objects.get(id=pk)

        # 409 Conflict: Phản hồi này được gửi khi 1 yêu cầu xung đột với trạng thái hiện tại của máy chủ.
        # Kiểm tra cư dân đã thực hiện khảo sát này chưa
        if self.is_resident_completed_survey(survey_check, resident_check):
            return Response({"error": "Khảo sát đã được trả lời"}, status=status.HTTP_409_CONFLICT)

        # Kiểm tra Câu hỏi có tồn tại trong khảo sát không
        if not self.is_question_in_survey(question_id, survey_check):
            return Response({"error": "Câu hỏi không tồn tại trong khảo sát"},
                            status=status.HTTP_409_CONFLICT)

        # Kiểm tra cư dân đã trả lời câu hỏi này chưa
        if self.is_resident_answered_question(resident_check, question_id):
            return Response({"error": "Câu hỏi đã được trả lời"}, status=status.HTTP_409_CONFLICT)

        # Gửi câu trả lời lên hệ thống
        answer = AnswerSurvey.objects.create(content=request.data.get('content'),
                                             question_id=question_id, resident_id=request.user.id)

        # Cập nhật kết quả khảo sát
        self.get_object().resultsurvey_set.create(answer_id=answer.id, question_id=question_id,
                                                  resident_id=request.user.id)

        # Kiểm tra Các câu hỏi trong khảo sát đã được trả lời hết chưa, nếu đúng sẽ tiến hành thêm vào
        if self.is_all_questions_answered(survey_check, resident_check):
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