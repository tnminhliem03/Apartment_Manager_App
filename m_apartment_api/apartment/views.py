from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
# from vnpay.utils import VnPay

from apartment import serializers, paginators, perms
from django.contrib.auth.hashers import make_password
from apartment.models import (Resident, Room, Payment, Receipt, SecurityCard, Package, Complaint, Survey,
                              QuestionSurvey, AnswerSurvey, ResultSurvey, Notification, PaymentForm)
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

# vnpay
def index(request):
    return render(request, "payment/index.html", {"title": "Danh sách demo"})


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def payment(request):
    if request.method == 'POST':
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
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

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            print(vnpay_payment_url)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
    else:
        return render(request, "payment/payment.html", {"title": "Thanh toán"})


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result


def payment_return(request):
    # inputData = request.GET
    inputData = request.POST
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']

        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                # return JsonResponse({"title": "Kết quả thanh toán",
                #                                                "result": "Thành công", "order_id": order_id,
                #                                                "amount": amount,
                #                                                "order_desc": order_desc,
                #                                                "vnp_TransactionNo": vnp_TransactionNo,
                #                                                "vnp_ResponseCode": vnp_ResponseCode})
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Thành công", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
            else:
                # return JsonResponse({"title": "Kết quả thanh toán",
                #                                                "result": "Lỗi", "order_id": order_id,
                #                                                "amount": amount,
                #                                                "order_desc": order_desc,
                #                                                "vnp_TransactionNo": vnp_TransactionNo,
                #                                                "vnp_ResponseCode": vnp_ResponseCode})
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Lỗi", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
        else:
            # return JsonResponse({"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
            #                "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
            #                "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
            return render(request, "payment/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})


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


def query(request):
    if request.method == 'GET':
        return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_Version = '2.1.0'

    vnp_RequestId = n_str
    vnp_Command = 'querydr'
    vnp_TxnRef = request.POST['order_id']
    vnp_OrderInfo = 'kiem tra gd'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
        vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})

def refund(request):
    if request.method == 'GET':
        return render(request, "payment/refund.html", {"title": "Hoàn tiền giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_RequestId = n_str
    vnp_Version = '2.1.0'
    vnp_Command = 'refund'
    vnp_TransactionType = request.POST['TransactionType']
    vnp_TxnRef = request.POST['order_id']
    vnp_Amount = request.POST['amount']
    vnp_OrderInfo = request.POST['order_desc']
    vnp_TransactionNo = '0'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_CreateBy = 'user01'
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
        vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/refund.html", {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})


# Myapp
def create_payment(name, amount, resident_id):
    Payment.objects.create(name=name, amount=amount, resident_id=resident_id)

def type_vehicle_create_pay(obj):
    if obj.type_vehicle == 'bike':
        create_payment('Phí gửi xe đạp tháng', '900000', obj.resident.id)
    elif obj.type_vehicle == 'motorbike':
        create_payment('Phí gửi xe máy tháng', '150000', obj.resident.id)
    elif obj.type_vehicle == 'car':
        create_payment('Phí gửi xe hơi tháng', '1600000', obj.resident.id)


# @receiver(post_save, sender=SecurityCard)
# def add_pay_on_create_sc(sender, instance, created, **kwargs):
#     if created:
#         type_vehicle_create_pay(instance)
#         # if instance.type_vehicle == 'bike':
#         #     create_payment('Phí gửi xe đạp tháng', '900000', instance.resident.id)
#         # elif instance.type_vehicle == 'motorbike':
#         #     create_payment('Phí gửi xe máy tháng', '150000', instance.resident.id)
#         # elif instance.type_vehicle == 'car':
#         #     create_payment('Phí gửi xe hơi tháng', '1600000', instance.resident.id)
#
# def create_notif(name, content, resident_id):
#     Notification.objects.create(name=name, content=content, resident_id=resident_id)
#
# @receiver(post_save, sender=Package)
# @receiver(post_save, sender=Payment)
# def add_notif_on_created(sender, instance, created, **kwargs):
#     if created:
#         if isinstance(instance, Payment):
#             create_notif('THÔNG BÁO THANH TOÁN','Bạn có một phiếu thanh toán cần chi trả',
#                          instance.resident.id)
#         elif isinstance(instance, Package):
#             create_notif('THÔNG BÁO TỦ ĐỒ', 'Bạn có một món hàng trong tủ đồ cần nhận',
#                          instance.resident.id)
#
# @receiver(post_save, sender=Resident)
# @receiver(post_save, sender=Complaint)
# def add_notif_on_changed(sender, instance, **kwargs):
#     if isinstance(instance, Complaint):
#         if instance.active == 0:
#             create_notif('XỬ LÝ PHẢN ÁNH', 'Phản ảnh của bạn đã được giải quyết',
#                          instance.resident.id)
#     elif isinstance(instance, Resident):
#         if check_password('123456', instance.password) or instance.password == '123456':
#             create_notif('CẢNH BÁO BẢO MẬT', 'Vui lòng thay đổi mật khẩu và cập nhật'
#                                              ' ảnh đại diện', instance.id)

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
        type_vehicle_create_pay(self)
        # if sc.type_vehicle == 'bike':
        #     create_payment('Phí gửi xe đạp tháng', '900000', request.user.id)
        # elif sc.type_vehicle == 'motorbike':
        #     create_payment('Phí gửi xe máy tháng', '150000', request.user.id)
        # elif sc.type_vehicle == 'car':
        #     create_payment('Phí gửi xe hơi tháng', '1600000', request.user.id)

        return Response(serializers.SecurityCardSerializer(sc).data, status=status.HTTP_201_CREATED)

    @action(methods=['patch'], url_path='update-sc', detail=True)
    def updated_sc(self, request, pk):
        sc = self.get_object()
        for k, v in request.data.items():
            setattr(sc, k, v)
        sc.save()

        return Response(serializers.SecurityCardSerializer(sc).data, status=status.HTTP_200_OK)

class NotificationViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    pagination_class = paginators.BasePaginator

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
        if (pay.active == 1):
            setattr(pay, 'active', '0')
            Receipt.objects.create(name=f'Hóa đơn {pay.name}', amount=pay.amount, payment=pay,
                                   resident=pay.resident)
            pay.save()
        else:
            return Response({"error": "Hóa đơn đã được thanh toán"})

        return Response(serializers.PaymentSerializer(pay).data)

    # @staticmethod
    # def update(pay):
    #     transaction_data = {
    #         'order_id': '1',
    #         'amount': '12345',
    #         'order_desc': 'acb',
    #         'order_type': '250000',
    #         'language': 'VN',
    #         'bank_code': 'VNBANK'
    #     }
    #
    #     response = requests.post('https://sandbox.vnpayment.vn/merchantv2/Home/Dashboard.htm', data=transaction_data)
    #
    #     if response.status_code == 200:
    #         print("Cập nhật giao dịch thành công trên trang quản lý giao dịch của VNPAY")
    #     else:
    #         print("Cập nhật giao dịch không thành công. Mã lỗi:", response.status_code)

    # def update(order_id, amount, order_desc, vnp_TransactionNo, vnp_ResponseCode):
    #     # Tạo dữ liệu giao dịch cần cập nhật
    #     transaction_data = {
    #         'order_id': order_id,
    #         'amount': amount,
    #         'order_desc': order_desc,
    #         'vnp_TransactionNo': vnp_TransactionNo,
    #         'vnp_ResponseCode': vnp_ResponseCode
    #     }
    #
    #     login_data = {
    #         'vnp_TmnCode': 'BBJDENSU',
    #         'vnp_HashSecret': '1S8CJ30B6CNNK2G4I2A0GJ6RYKEQN966',
    #         'email': 'trannguyenminhliem181203@gmail.com',
    #         'password': 'Liemkute03'
    #     }
    #     login_url = 'https://sandbox.vnpayment.vn/merchantv2/Users/Login.htm?ReturnUrl=%2fmerchantv2%2fUsers%2fLogout.htm'
    #     # login_url = 'https://sandbox.vnpayment.vn/login'
    #     with requests.Session() as session:
    #         login_response = session.post(login_url, data=login_data)
    #
    #         if login_response.status_code == 200:
    #             print("Đăng nhập thành công!")
    #
    #             # Tiếp tục gửi các yêu cầu khác trong phiên đăng nhập
    #             # Ví dụ: gửi yêu cầu cập nhật giao dịch
    #             response = session.post('https://sandbox.vnpayment.vn/merchantv2/Home/Dashboard.htm',
    #                                     data=transaction_data)
    #             # print(response.text)  # In ra phản hồi từ trang web
    #         else:
    #             print("Đăng nhập thất bại!")
    #
    #     # Gửi yêu cầu cập nhật giao dịch đến API của VNPAY
    #     response = requests.post('https://sandbox.vnpayment.vn/merchantv2/Home/Dashboard.htm', data=transaction_data)
    #
    #     print(response)
    #     # Kiểm tra kết quả của yêu cầu cập nhật giao dịch
    #     if response.status_code == 200:
    #         # Nếu thành công, in ra thông báo
    #         print("Cập nhật giao dịch thành công trên trang quản lý giao dịch của VNPAY")
    #         return True
    #     else:
    #         # Nếu không thành công, in ra mã lỗi và trả về False
    #         print("Cập nhật giao dịch không thành công. Mã lỗi:", response.status_code)
    #         return False
    #
    # @action(methods=['post'], url_path='vnpay', detail=True)
    # def paid_vnpay(self, request, pk):
    #     pay = self.get_object()
    #     amount_vnpay = pay.amount
    #     payment_id = pay.id
    #
    #     # order_id = inputData['vnp_TxnRef']
    #     # amount = int(inputData['vnp_Amount']) / 100
    #     # order_desc = inputData['vnp_OrderInfo']
    #     # vnp_TransactionNo = inputData['vnp_TransactionNo']
    #     # vnp_ResponseCode = inputData['vnp_ResponseCode']
    #     # vnp_TmnCode = inputData['vnp_TmnCode']
    #     # vnp_PayDate = inputData['vnp_PayDate']
    #     # vnp_BankCode = inputData['vnp_BankCode']
    #     # vnp_CardType = inputData['vnp_CardType']
    #
    #     order_id = '123'
    #     amount = '3456'
    #     order_desc = request.data.get('order_desc')
    #     vnp_TransactionNo = request.data.get('vnp_TransactionNo')
    #     vnp_ResponseCode = request.data.get('vnp_ResponseCode')
    #
    #     payment_result = payment_return(request)
    #     if payment_result is not None:
    #         # Nếu thanh toán thành công
    #         if payment_result.status_code == 200:
    #             # Cập nhật giao dịch trên trang quản lý giao dịch của VNPAY
    #             update_transaction_success = self.update(order_id, amount, order_desc, vnp_TransactionNo, vnp_ResponseCode)
    #             if update_transaction_success:
    #                 return Response("Thanh toán thành công và cập nhật giao dịch thành công", status=status.HTTP_200_OK)
    #             else:
    #                 return Response("Có lỗi xảy ra khi cập nhật giao dịch",
    #                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         else:
    #             # Xử lý khi thanh toán không thành công
    #             return Response("Thanh toán không thành công", status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         # Xử lý khi có lỗi xảy ra trong quá trình gửi thanh toán
    #         return Response("Có lỗi xảy ra khi gửi thanh toán", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # test_request = HttpRequest()
        # test_request.method = 'POST'
        # test_request.POST['order_id'] = '1'
        # test_request.POST['amount'] = '12345'
        # test_request.POST['order_desc'] = 'acb'
        # test_request.POST['order_type'] = '250000'
        # test_request.POST['language'] = 'VN'
        # test_request.POST['bank_code'] = 'VNBANK'

        # payment_result = payment_return(test_request)
        # print(payment_result.status_code)
        #
        # if payment_result is not None:
        #     # Nếu thanh toán thành công, cập nhật giao dịch trên trang quản lý giao dịch của VNPAY
        #     if payment_result.status_code == 200:
        #         self.update(pay)
        #         return Response(payment_result, status=status.HTTP_200_OK)
        #     else:
        #         return Response("Thanh toán không thành công", status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response("Có lỗi xảy ra khi gửi thanh toán", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    def is_resident_completed_survey(survey_id, resident_id):
        return ResultSurvey.objects.filter(survey_id=survey_id, resident_id=resident_id).exists()
        # return survey in resident.answered_surveys.all()

    # Kiểm tra cư dân đã trả lời câu hỏi này chưa
    @staticmethod
    def is_resident_answered_question(resident_id, question_id):
        return ResultSurvey.objects.filter(resident_id=resident_id, question_id=question_id).exists()
        # return AnswerSurvey.objects.filter(resident_id=resident_id, question_id=question_id).exists()

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