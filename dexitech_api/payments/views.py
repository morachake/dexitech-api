from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.urls import reverse
from .models import MpesaPayment
from dexitech_api.orders.models import Order
from .mpesa import MpesaClient
import uuid

class InitiatePaymentView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            order_id = request.data.get('order_id')
            phone_number = request.data.get('phone_number')
            
            if not phone_number:
                return Response({
                    'status': 'error',
                    'message': 'Phone number is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Format phone number (remove leading 0 or +254)
            phone_number = phone_number.replace('+', '')
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            order = Order.objects.get(
                id=order_id,
                user=request.user,
                status='pending',
                payment_status='pending'
            )
            
            # Generate unique reference
            reference = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Initialize M-Pesa client
            mpesa = MpesaClient()
            
            # Get callback URL
            callback_url = request.build_absolute_uri(
                reverse('mpesa-callback')
            )
            
            # Initiate STK push
            result, error = mpesa.initiate_stk_push(
                phone_number=phone_number,
                amount=order.amount,
                reference=reference,
                callback_url=callback_url
            )
            
            if error:
                return Response({
                    'status': 'error',
                    'message': error
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create payment record
            payment = MpesaPayment.objects.create(
                order=order,
                phone_number=phone_number,
                amount=order.amount,
                reference=reference,
                checkout_request_id=result['CheckoutRequestID'],
                merchant_request_id=result['MerchantRequestID'],
                status='processing'
            )
            
            return Response({
                'status': 'success',
                'message': 'Payment initiated successfully',
                'data': {
                    'checkout_request_id': payment.checkout_request_id,
                    'merchant_request_id': payment.merchant_request_id,
                    'reference': payment.reference
                }
            })
            
        except Order.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)

class VerifyPaymentView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            checkout_request_id = request.data.get('checkout_request_id')
            payment = MpesaPayment.objects.get(
                checkout_request_id=checkout_request_id,
                order__user=request.user
            )
            
            # Initialize M-Pesa client
            mpesa = MpesaClient()
            
            # Verify transaction
            result, error = mpesa.verify_transaction(checkout_request_id)
            
            if error:
                return Response({
                    'status': 'error',
                    'message': error
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update payment status based on result
            result_code = result.get('ResultCode')
            if result_code == '0':
                payment.status = 'completed'
                payment.mpesa_receipt_number = result.get('MpesaReceiptNumber')
                payment.save()
                
                # Update order status
                order = payment.order
                order.payment_status = 'paid'
                order.status = 'confirmed'
                order.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Payment completed successfully',
                    'data': {
                        'receipt_number': payment.mpesa_receipt_number,
                        'amount': payment.amount
                    }
                })
            else:
                payment.status = 'failed'
                payment.result_code = result_code
                payment.result_description = result.get('ResultDesc')
                payment.save()
                
                return Response({
                    'status': 'error',
                    'message': result.get('ResultDesc')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except MpesaPayment.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)

class MpesaCallbackView(generics.CreateAPIView):
    """Handle M-Pesa callback"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = request.data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = data.get('CheckoutRequestID')
            
            payment = MpesaPayment.objects.get(checkout_request_id=checkout_request_id)
            
            result_code = data.get('ResultCode')
            if result_code == 0:
                # Payment successful
                payment.status = 'completed'
                payment.mpesa_receipt_number = data.get('CallbackMetadata', {}).get('Item', [{}])[1].get('Value')
                payment.save()
                
                # Update order status
                order = payment.order
                order.payment_status = 'paid'
                order.status = 'confirmed'
                order.save()
            else:
                # Payment failed
                payment.status = 'failed'
                payment.result_code = result_code
                payment.result_description = data.get('ResultDesc')
                payment.save()
            
            return Response({'status': 'success'})
            
        except MpesaPayment.DoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)