from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Category, Product
from orders.models import Order, OrderStatus
from . import models, serializers

test_data = {
    'valid order':
        {
            'items':
                [
                    {
                        'product': {
                            'id': 1,
                        },
                        'amount': 2
                    }, {
                        'product': {
                            'id': 2,
                        },
                        'amount': 3
                    }
                ],
            'address_to_send': 'Russia, Krasnodar',
            'mobile_number': '+12223334455',
            'first_name': 'Carl',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'category': {
        'name': 'top clothes',
    },
    'product 1':
        {
            'name': 't-shirt',
            'price': 5.28,
            'description': 'abooba',
            'img': 'https://google.com',
            'amount_remaining': 30,
            'size': 'L',
            'color': 'red',
        },
    'product 2':
        {
            'name': 'pants',
            'price': 4,
            'description': 'abooba',
            'img': 'https://google.com',
            'amount_remaining': 10,
            'size': 'L',
            'color': 'red',
        },
    'user data 1':
        {
            'username': 'test1',
            'password': 'testpassword',
            'email': 'test1@test.com'
        },
    'user data 2':
        {
            'username': 'test2',
            'password': 'testpassword',
            'email': 'test2@test.com'
        },
    'successful notification':
        {
            'id': 'pass-here-payment-id',
            'status': 'successed',
            'metadata': {
                'secret_key': 'pass-here-secret-key'
            }
        },
    'unsuccessful notification':
        {
            'id': 'pass-here-payment-id',
            'status': 'freezed',
            'metadata': {
                'secret_key': 'pass-here-secret-key'
            }
        },
    'notification without status':
        {
            'id': 'pass-here-payment-id',
            'metadata': {
                'secret_key': 'pass-here-secret-key'
            }
        },
    'notification without id':
        {
            'status': 'successed',
            'metadata': {
                'secret_key': 'pass-here-secret-key'
            }
        },
    'notification without secret key':
        {
            'id': 'pass-here-payment-id',
            'status': 'successed',
            'metadata': {}
        },
}


class PaymentURLTest(APITestCase):
    def setUp(self) -> None:
        self.c1 = Category(**test_data['category'])
        self.c1.save()

        self.p1 = Product(**test_data['product 1'], category=self.c1)
        self.p2 = Product(**test_data['product 2'], category=self.c1)

        self.p1.save()
        self.p2.save()

        default_order_status = OrderStatus(name='Created')
        default_order_status.save()

        self.client.post('/register', test_data['user data 1'], format='json')
        self.client.post('/register', test_data['user data 2'], format='json')

        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        self.client.post('/order', test_data['valid order'], format='json')

        self.client.logout()

    def test_get_payment_url(self):
        '''
        Ensure that we can get an payment URL of the order we've created
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.get('/order/1/pay', format='json')

        order = models.Payment.objects.get(id=1)
        expected_result = serializers.PaymentSerializer(order)

        self.assertEquals(response.data, expected_result.data)

    def test_get_payment_url_via_not_owner(self):
        '''
        Ensure that we cannot get payment URL if we're not logged in as an order creator
        '''
        self.client.login(
            username=test_data['user data 2']['username'],
            password=test_data['user data 2']['password']
        )

        response = self.client.get('/order/1/pay', format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'].code, 'permission_denied')

    def test_double_get_payment_url(self):
        '''
        Ensure that payment ID does not change if we try to get URL more than one time
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        first_response = self.client.get('/order/1/pay', format='json')
        second_response = self.client.get('/order/1/pay', format='json')
        third_response = self.client.get('/order/1/pay', format='json')

        self.assertEqual(first_response.data, second_response.data)
        self.assertEqual(second_response.data, third_response.data)

    def test_get_payment_url_logout(self):
        '''
        Ensure that payment URL cannot be gotten if we're out logged out
        '''
        response = self.client.get('/order/1/pay', format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

    def test_get_payment_url_of_not_existing_order(self):
        '''
        Ensure that we cannot get payment URL of order that does not exist
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.get('/order/2/pay', format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')


class FakePaymentServiceTest(APITestCase):
    def setUp(self) -> None:
        self.c1 = Category(**test_data['category'])
        self.c1.save()

        self.p1 = Product(**test_data['product 1'], category=self.c1)
        self.p2 = Product(**test_data['product 2'], category=self.c1)

        self.p1.save()
        self.p2.save()

        default_order_status = OrderStatus(name='Created')
        default_order_status.save()

        self.client.post('/register', test_data['user data 1'], format='json')
        self.client.post('/register', test_data['user data 2'], format='json')

        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        self.client.post('/order', test_data['valid order'], format='json')

        self.client.logout()

    def test_get_payment_page(self):
        '''
        Ensure that we can visit payment page for payment that existing
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        # Getting payment ID for this purchase
        purchase = self.client.get('/order/1/pay', format='json').data
        response = self.client.get(purchase['payment_page_url'])

        self.assertEquals(
            response.data['text'],
            'Congrats, you are on the payment page! Since we do not use any real payment service, you should send post request to /webhooks by yourself. Use data that you receive when you achieve /order/1/pay endpoint for it.'
        )

    def test_get_payment_page_for_random_order(self):
        '''
        Ensure that we cannot access the payment page if we provided a wrong payment ID
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.get('/payment/payment-id-that-does-not-exist')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')


class PaymentCheckTest(APITestCase):
    def setUp(self) -> None:
        self.c1 = Category(**test_data['category'])
        self.c1.save()

        self.p1 = Product(**test_data['product 1'], category=self.c1)
        self.p2 = Product(**test_data['product 2'], category=self.c1)

        self.p1.save()
        self.p2.save()

        default_order_status = OrderStatus(name='Created')
        default_order_status.save()

        paid_order_status = OrderStatus(name='Paid')
        paid_order_status.save()

        self.client.post('/register', test_data['user data 1'], format='json')

        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        self.client.post('/order', test_data['valid order'], format='json')

        self.client.logout()

    def get_payment_from_database(self, id):
        return models.Payment.objects.get(id=id)

    def test_order_can_be_paid(self):
        '''
        Ensure that order can be paid
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        # Getting payment service ID for this purchase
        payment = self.client.get('/order/1/pay', format='json').data
        secret_key = payment['secret_key']
        payment_id = payment['payment_service_id']

        # Sending notification to the webhook to notify about the successful payment
        self.client.post(
            '/webhooks', {
                **test_data['successful notification'],
                'metadata': {
                    'secret_key': secret_key,
                },
                'id': payment_id,
            },
            format='json'
        )

        # Gets order details from database for future tests
        order = Order.objects.get(id=1)
        order_items = order.items.all()

        # Checks if order status was changed
        self.assertEquals(order.status.name, 'Paid')

        # Checks that counts of products decreased after payment
        self.assertEquals(
            order_items[0].product.amount_remaining,
            test_data['product 1']['amount_remaining'] -
            test_data['valid order']['items'][0]['amount']
        )
        self.assertEquals(
            order_items[1].product.amount_remaining,
            test_data['product 2']['amount_remaining'] -
            test_data['valid order']['items'][1]['amount']
        )

        # Checks if the payment was deleted
        self.assertRaises(
            models.Payment.DoesNotExist, self.get_payment_from_database, 1
        )

    def test_not_successful_pay(self):
        '''
        Ensure that nothing happens if payment was not successed
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        # Getting payment service ID for this purchase
        payment = self.client.get('/order/1/pay', format='json').data
        secret_key = payment['secret_key']
        payment_id = payment['payment_service_id']

        # Sending notification to the webhook to notify about the successful payment
        response = self.client.post(
            '/webhooks', {
                **test_data['unsuccessful notification'],
                'metadata': {
                    'secret_key': secret_key,
                },
                'id': payment_id,
            },
            format='json'
        )

        # Gets order details from database for future tests
        order = Order.objects.get(id=1)
        order_items = order.items.all()

        # Checks if order status was not changed
        self.assertEquals(order.status.name, 'Created')

        # Checks that counts of products decreased after payment
        self.assertEquals(
            order_items[0].product.amount_remaining,
            test_data['product 1']['amount_remaining']
        )
        self.assertEquals(
            order_items[1].product.amount_remaining,
            test_data['product 2']['amount_remaining']
        )

        # Checks if the payment was not deleted
        self.get_payment_from_database(1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')
        self.assertEqual(str(response.data[0]), 'Payment was not successful.')

    def test_invalid_id_pay(self):
        '''
        Ensure that nothing happens if we provide wrong payment service ID in the request
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        # Getting payment service ID for this purchase
        payment = self.client.get('/order/1/pay', format='json').data
        secret_key = payment['secret_key']

        # Sending notification to the webhook to notify about the successful payment
        response = self.client.post(
            '/webhooks', {
                **test_data['successful notification'],
                'metadata': {
                    'secret_key': secret_key,
                },
                'id': 'random-payment-service-id',
            },
            format='json'
        )

        # Gets order details from database for future tests
        order = Order.objects.get(id=1)
        order_items = order.items.all()

        # Checks if order status was not changed
        self.assertEquals(order.status.name, 'Created')

        # Checks that counts of products decreased after payment
        self.assertEquals(
            order_items[0].product.amount_remaining,
            test_data['product 1']['amount_remaining']
        )
        self.assertEquals(
            order_items[1].product.amount_remaining,
            test_data['product 2']['amount_remaining']
        )

        # Checks if the payment was not deleted
        self.get_payment_from_database(1)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')
        self.assertEqual(
            response.data['detail'],
            'Payment for with ID random-payment-service-id does not exist.'
        )

    def test_invalid_secret_key(self):
        '''
        Ensure that nothing happens if we provide wrong secret key in the request
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        # Getting payment service ID for this purchase
        payment = self.client.get('/order/1/pay', format='json').data
        payment_id = payment['payment_service_id']

        # Sending notification to the webhook to notify about the successful payment
        response = self.client.post(
            '/webhooks', {
                **test_data['successful notification'],
                'metadata': {
                    'secret_key': 'random-secret-key',
                },
                'id': payment_id,
            },
            format='json'
        )

        # Gets order details from database for future tests
        order = Order.objects.get(id=1)
        order_items = order.items.all()

        # Checks if order status was not changed
        self.assertEquals(order.status.name, 'Created')

        # Checks that counts of products decreased after payment
        self.assertEquals(
            order_items[0].product.amount_remaining,
            test_data['product 1']['amount_remaining']
        )
        self.assertEquals(
            order_items[1].product.amount_remaining,
            test_data['product 2']['amount_remaining']
        )

        # Checks if the payment was not deleted
        self.get_payment_from_database(1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')
        self.assertEqual(str(response.data[0]), 'Invalid secret key.')

    def test_payment_without_status(self):
        '''
        Ensure that nothing happens if we do not provide payment status in the request
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        # Getting payment service ID for this purchase
        payment = self.client.get('/order/1/pay', format='json').data
        secret_key = payment['secret_key']
        payment_id = payment['payment_service_id']

        # Sending notification to the webhook to notify about the successful payment
        response = self.client.post(
            '/webhooks', {
                **test_data['notification without status'],
                'metadata': {
                    'secret_key': secret_key,
                },
                'id': payment_id,
            },
            format='json'
        )

        # Gets order details from database for future tests
        order = Order.objects.get(id=1)
        order_items = order.items.all()

        # Checks if order status was not changed
        self.assertEquals(order.status.name, 'Created')

        # Checks that counts of products decreased after payment
        self.assertEquals(
            order_items[0].product.amount_remaining,
            test_data['product 1']['amount_remaining']
        )
        self.assertEquals(
            order_items[1].product.amount_remaining,
            test_data['product 2']['amount_remaining']
        )

        # Checks if the payment was not deleted
        self.get_payment_from_database(1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')
        self.assertEquals(
            str(response.data[0]), 'Field \'status\' was not provided.'
        )

    def test_payment_without_id(self):
        '''
        Ensure that nothing happens if we do not provide payment ID in the request
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        # Getting payment service ID for this purchase
        payment = self.client.get('/order/1/pay', format='json').data
        secret_key = payment['secret_key']

        # Sending notification to the webhook to notify about the successful payment
        response = self.client.post(
            '/webhooks', {
                **test_data['notification without id'],
                'metadata': {
                    'secret_key': secret_key,
                },
            },
            format='json'
        )

        # Gets order details from database for future tests
        order = Order.objects.get(id=1)
        order_items = order.items.all()

        # Checks if order status was not changed
        self.assertEquals(order.status.name, 'Created')

        # Checks that counts of products decreased after payment
        self.assertEquals(
            order_items[0].product.amount_remaining,
            test_data['product 1']['amount_remaining']
        )
        self.assertEquals(
            order_items[1].product.amount_remaining,
            test_data['product 2']['amount_remaining']
        )

        # Checks if the payment was not deleted
        self.get_payment_from_database(1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')
        self.assertEquals(
            str(response.data[0]), 'Field \'id\' was not provided.'
        )

    def test_payment_without_secret_key(self):
        '''
        Ensure that nothing happens if we do not provide payment status in the request
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        # Getting payment service ID for this purchase
        payment = self.client.get('/order/1/pay', format='json').data
        payment_id = payment['payment_service_id']

        # Sending notification to the webhook to notify about the successful payment
        response = self.client.post(
            '/webhooks', {
                **test_data['notification without secret key'],
                'id':
                    payment_id,
            },
            format='json'
        )

        # Gets order details from database for future tests
        order = Order.objects.get(id=1)
        order_items = order.items.all()

        # Checks if order status was not changed
        self.assertEquals(order.status.name, 'Created')

        # Checks that counts of products decreased after payment
        self.assertEquals(
            order_items[0].product.amount_remaining,
            test_data['product 1']['amount_remaining']
        )
        self.assertEquals(
            order_items[1].product.amount_remaining,
            test_data['product 2']['amount_remaining']
        )

        # Checks if the payment was not deleted
        self.get_payment_from_database(1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')
        self.assertEquals(
            str(response.data[0]), 'Field \'secret_key\' was not provided.'
        )

    def test_two_payments(self):
        '''
        Ensure that we can not pay for order more than one time
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        # Getting payment service ID for this purchase
        payment = self.client.get('/order/1/pay', format='json').data
        secret_key = payment['secret_key']
        payment_id = payment['payment_service_id']

        # Sending notification to the webhook to notify about the successful payment
        self.client.post(
            '/webhooks', {
                **test_data['successful notification'],
                'metadata': {
                    'secret_key': secret_key,
                },
                'id': payment_id,
            },
            format='json'
        )

        response1 = self.client.get('/order/1/pay', format='json')
        self.assertEqual(
            response1.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertEqual(response1.data['detail'].code, 'error')
        self.assertEqual(
            response1.data['detail'], 'This order is already paid.'
        )

        response2 = self.client.post(
            '/webhooks', {
                **test_data['successful notification'],
                'metadata': {
                    'secret_key': secret_key,
                },
                'id': payment_id,
            },
            format='json'
        )

        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response2.data['detail'].code, 'not_found')
        self.assertEqual(
            response2.data['detail'],
            f'Payment for with ID {payment_id} does not exist.'
        )
