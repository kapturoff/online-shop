from rest_framework import status, generics
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .permissions import IsOrderOwnerOrAdmin
from .models import Order
from .serializers import OrderSerializer
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
            # return Response(
            #     data={'detail': f'Field {e} was not provided.'},
            #     status=status.HTTP_400_BAD_REQUEST,
            # )
            raise ValidationError(f'Field {e} was not provided.')
        except Product.DoesNotExist as e:
            # return Response(
            #     data={'detail': str(e)},
            #     status=status.HTTP_404_NOT_FOUND,
            # )
            raise NotFound(e, 'not_found')
        except TypeError:
            # return Response(
            #     data={'detail': 'Field \'items\' must be array of products'},
            #     status=status.HTTP_400_BAD_REQUEST,
            # )
            raise ValidationError('Field \'items\' must be array of products')


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
