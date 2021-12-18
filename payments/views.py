from rest_framework import status, generics
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from .permissions import IsPaymentOwnerOrAdmin
from orders.permissions import IsOrderOwnerOrAdmin
from .models import Order, Payment
from orders.models import OrderStatus
from orders.serializers import OrderSerializer
from .helpers import call_payment_service_api, decrease_products_amount
from rest_framework.authentication import TokenAuthentication, BasicAuthentication


class PaymentURL(generics.RetrieveAPIView):
    '''
    This view is additional since this project does not use any real payment service.
    In reality, it could just return an url with order id on GET request, but goal of this
    view is to emulate a work with real payment service, so here is it.
    '''
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, IsOrderOwnerOrAdmin]
    authentication_classes = [TokenAuthentication, BasicAuthentication]

    def get(self, request, order_id):
        try:
            payment_serialized = call_payment_service_api(order_id)
            return Response(payment_serialized.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                data={'detail': f'Order with {order_id} does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )


class FakePaymentService(generics.RetrieveAPIView):
    '''
    This view is additional since this project does not use any real payment service.
    In reality, instead of this view you are probably going to use a real page which your payment service provided
    to you
    '''
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, IsPaymentOwnerOrAdmin]
    authentication_classes = [TokenAuthentication, BasicAuthentication]

    def get(self, request, payment_service_id):
        try:
            payment = Payment.objects.get(payment_service_id=payment_service_id)
            return Response(
                data={
                    'text':
                        f'Congrats, you are on the payment page! Since we do not use any real payment service, you should send post request to /webhooks by yourself. Use data that you receive when you achieve /order/{payment.order.id}/pay endpoint for it.'
                },
                status=status.HTTP_202_ACCEPTED,
            )
        except Payment.DoesNotExist:
            return Response(
                data={
                    'detail':
                        f'Payment for with ID {payment_service_id} does not exist.'
                },
                status=status.HTTP_404_NOT_FOUND
            )


class PaymentCheck(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        try:
            payment_id = request.data['id']
            payment_status = request.data['status']
            secret_key = request.data['metadata']['secret_key']

            if payment_status != 'successed':
                raise ValidationError('Payment was not successful.')

            payment = Payment.objects.get(payment_service_id=payment_id)

            # Checks the authenticity of request by comparing secret key in the database and in the request
            if (str(payment.secret_key) != secret_key):
                raise ValidationError('Invalid secret key.')

            order = payment.order
            order_items = order.items.all()

            # Reduces the total number of products when user paid for order
            decrease_products_amount(order_items)

            # Removes payment information
            payment.delete()

            # Changes status of order
            order.status = OrderStatus.objects.get(name='Paid')

            order.save()
            order_serialized = OrderSerializer(order)

            return Response(
                data=order_serialized.data,
                status=status.HTTP_202_ACCEPTED,
            )
        except (Payment.DoesNotExist, DjangoValidationError):
            raise NotFound(f'Payment for with ID {payment_id} does not exist.')
        except KeyError as e:
            raise ValidationError(f'Field {e} was not provided.')
