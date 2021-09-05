from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .serializers import OrderSerializer
from .models import Order
from products_data_storage.models import Product

class Order(generics.CreateAPIView):
    '''
    This class is responsible for work with creating of the orders.
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

    def create(self, request):
        try:
            order = OrderSerializer.create(request.data, request.user)
            order_serialized = OrderSerializer(order)

            return Response(data=order_serialized.data, status=status.HTTP_201_CREATED)
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
        except IndexError as e:
            return Response(
                data={'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
