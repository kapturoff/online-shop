from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from .permissions import IsOrderOwnerOrAdmin, IsPaymentOwnerOrAdmin
from .models import Order, Payment, OrderStatus
from .serializers import OrderSerializer
from .helpers import call_payment_service_api, decrease_products_amount
from products.models import Product


class OrderCreator(generics.CreateAPIView):
    '''
    This class is responsible for working with creating of the orders.
    To create order, you need to send POST request to /order endpoint with following schema in request body:

    {
        "items": <CartItem[] | OrderItem[]>,
        "address_to_send": <str>,
        "mobile_number": <str>,
        "first_name": <str>,
        "last_name": <str>,
        "email": <str>,
    }

    ---

    This class does not implement handlers for any GET methods because there's only two ways
    for use them as far as I see:
    1. Getting data about one particular order.
    It isn't a right way to do this because user can access data about his order using /order/<order_id> endpoint (if he is
    a customer of this order, of course).
    2. Getting list of all orders.
    This still be not a right way to get it on this URL endpoint because it looks like this is an admin information and it
    actually could be gotten from admin page.
    '''
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            order = OrderSerializer.create(request.data, request.user)
            order_serialized = OrderSerializer(order)

            return Response(
                data=order_serialized.data, status=status.HTTP_201_CREATED
            )
        except KeyError as e:
            return Response(
                data={'detail': f'Field {e} was not provided.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Product.DoesNotExist as e:
            return Response(
                data={'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except TypeError:
            return Response(
                data={'detail': 'Field \'items\' must be array of products'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrderDetail(generics.RetrieveAPIView):
    '''
    This class is responsible for /order/<order_id> endpoint. It responses with order details on GET requests.
    To get these details you must be logged in as customer of this order or as an admin.
    '''
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    lookup_url_kwarg = 'order_id'
    permission_classes = [IsAuthenticated, IsOrderOwnerOrAdmin]


class PaymentURL(generics.RetrieveAPIView):
    '''
    This view is additional since this project does not use any real payment service.
    In reality, it could just return an url with order id on GET request, but goal of this
    view is to emulate a work with real payment service, so here is it.
    '''
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, IsOrderOwnerOrAdmin]

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

            # TODO: Create handlers for other types of the payments statuses
            if payment_status != "successed":
                return Response(
                    data={'detail': 'Payment is not successed.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payment = Payment.objects.get(payment_service_id=payment_id)

            # Checks the authenticity of request by comparing secret key in the database and in the request
            if (str(payment.secret_key) != secret_key):
                return Response(
                    data={'detail': 'Invalid secret key.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

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
        except Payment.DoesNotExist:
            return Response(
                data={
                    'detail':
                        f'Payment for with ID {payment_id} does not exist.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except KeyError as e:
            return Response(
                data={'detail': f'Field {e} was not provided.'},
                status=status.HTTP_404_NOT_FOUND
            )
