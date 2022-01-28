# Disclaimer!
#
# Because of the reason that I do not fully understand, the adding of a token authorization
# is somehow broke the standart approach of an authorization in tests, which is used to be
# ClientApi.login() method. Now client requires to pass the credentials explicitely.
# I achieve this by using the approach where we provide credentials on every request to the server.
#
# This approach basically looks like this:
# client.get('/some_endpoint_that_use_authorization', **test_data, HTTP_AUTHORIZATION = 'Token' + http_token)
#
# As I made sure further, doing the manual API testing with curl, the standart authorization that use
# login:password is still alive and works, but obstinate APITestCase.client.login() method does not
# trust in this. This is why I add that ugly string to every request a test do.

from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Category, Product
from . import models, serializers

test_data = {
    'valid order':
        {
            'address_to_send': 'Russia, Krasnodar',
            'mobile_number': '+12223334455',
            'first_name': 'Carl',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with no items':
        {
            'items': [],
            'address_to_send': 'Russia, Krasnodar',
            'mobile_number': '+12223334455',
            'first_name': 'Carl',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with no items field':
        {
            'address_to_send': 'Russia, Krasnodar',
            'mobile_number': '+12223334455',
            'first_name': 'Carl',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with no address to send':
        {
            'mobile_number': '+12223334455',
            'first_name': 'Carl',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with no phone number':
        {
            'address_to_send': 'Russia, Krasnodar',
            'first_name': 'Carl',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with no first name':
        {
            'address_to_send': 'Russia, Krasnodar',
            'mobile_number': '+12223334455',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with no last name':
        {
            'address_to_send': 'Russia, Krasnodar',
            'mobile_number': '+12223334455',
            'first_name': 'Carl',
            'email': 'hooba@booba.com'
        },
    'order with no email':
        {
            'address_to_send': 'Russia, Krasnodar',
            'mobile_number': '+12223334455',
            'first_name': 'Carl',
            'last_name': 'Johnson',
        },
    'order with product that does not exist':
        {
            'address_to_send': 'Russia, Krasnodar',
            'mobile_number': '+12223334455',
            'first_name': 'Carl',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with the invalid amount of items':
        {
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
            'name': 't-shirt',
            'price': 6,
            'description': 'abooooooooba',
            'img': 'https://google.com',
            'amount_remaining': 15,
            'size': 'S',
            'color': 'yellow',
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
}

class OrderCreatingTest(APITestCase):
    def setUp(self) -> None:
        self.c1 = Category(**test_data['category'])
        self.c1.save()

        self.p1 = Product(**test_data['product 1'], category=self.c1)
        self.p2 = Product(**test_data['product 2'], category=self.c1)

        self.p1.save()
        self.p2.save()

        self.client.post('/register', test_data['user data 1'], format='json')

        # Generates a token for only one user and stores it in this class
        # to make it accessable from other tests in this class
        self.token_1 = 'Token ' + self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']

    def test_create_order(self):
        '''
        Ensure that we can create the order if a given data is valid
        '''
        response = self.client.post(
            '/order', {
                **test_data['valid order'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        order_model = models.Order.objects.get()
        expected_result = serializers.OrderSerializer(order_model)

        self.assertEqual(response.data, expected_result.data)

    def test_create_order_logged_out(self):
        '''
        Ensure that we can not create the order if we're not authenticated
        '''
        response = self.client.post(
            '/order', {
                **test_data['valid order'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

    def test_create_order_with_no_items(self):
        '''
        Ensure that we can not create the order if a given data has got no items
        '''
        response = self.client.post(
            '/order',
            test_data['order with no items'],
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_with_no_items_field(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "items"
        '''
        response = self.client.post(
            '/order',
            test_data['order with no items field'],
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_address(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "address"
        '''
        response = self.client.post(
            '/order', {
                **test_data['order with no address to send'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_phone_number(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "mobile_number"
        '''
        response = self.client.post(
            '/order', {
                **test_data['order with no phone number'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_first_name(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "mobile_number"
        '''
        response = self.client.post(
            '/order', {
                **test_data['order with no first name'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_last_name(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "mobile_number"
        '''
        response = self.client.post(
            '/order', {
                **test_data['order with no last name'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_email(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "mobile_number"
        '''
        response = self.client.post(
            '/order', {
                **test_data['order with no email'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_with_not_existing_products(self):
        '''
        Ensure that we can not create the order if items in given data do not exist
        '''
        response = self.client.post(
            '/order', {
                **test_data['order with product that does not exist'], 'items':
                    [{
                        'product': {
                            'id': -1,
                        },
                        'amount': 2
                    }, ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')

    def test_create_order_with_invalid_amount_of_products(self):
        '''
        Ensure that we cannot create the order if the user asked for a bigger count of product than exist in the database.
        '''
        response = self.client.post(
            '/order',

            {
                **test_data['order with the invalid amount of items'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 21234341234134
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 312342134
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')


class OrderDetailTest(APITestCase):
    def setUp(self) -> None:
        self.c1 = Category(**test_data['category'])
        self.c1.save()

        self.p1 = Product(**test_data['product 1'], category=self.c1)
        self.p2 = Product(**test_data['product 2'], category=self.c1)

        self.p1.save()
        self.p2.save()

        self.client.post('/register', test_data['user data 1'], format='json')
        self.client.post('/register', test_data['user data 2'], format='json')

        # Generates a token for the first user
        self.token_1 = 'Token ' + self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']

        # Generate a token for the second user
        self.token_2 = 'Token ' + self.client.post(
            '/token', test_data['user data 2'], format='json'
        ).data['token']

        # (!) The tokens need be stored in class since the token authorization is being used in
        # tests and tests do not accept standart ClientApi.login() authorization for some
        # reason that I do not fully understand

        # Creates two orders from first user
        self.o1 = self.client.post(
            '/order', {
                **test_data['valid order'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )
        self.o2 = self.client.post(
            '/order', {
                **test_data['valid order'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        # Creates one order from second user
        self.o3 = self.client.post(
            '/order', {
                **test_data['valid order'], 'items':
                    [
                        {
                            'product': {
                                'id': self.p1.id,
                            },
                            'amount': 2
                        },
                        {
                            'product': {
                                'id': self.p2.id
                            },
                            'amount': 3
                        },
                    ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.token_2
        )

        self.client.logout()

    def test_get_details(self):
        '''
        Ensure that we can get details of an order if we logged in as its owner
        '''
        order_id = self.o1.data['id']
        response = self.client.get(
            f'/order/{order_id}',
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        order_model = models.Order.objects.get(id=order_id)
        expected_result = serializers.OrderSerializer(order_model)

        self.assertEqual(response.data, expected_result.data)

    def test_get_details_logout(self):
        '''
        Ensure that we cannot get details of any order if we logged out
        '''
        order_id = self.o1.data['id']
        response = self.client.get(f'/order/{order_id}', format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

    def test_get_details_logged_in_as_not_owner(self):
        '''
        Ensure that we cannot get details of an order we logged in as not its owner
        '''
        order_id = self.o3.data['id']
        response = self.client.get(
            f'/order/{order_id}',
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'].code, 'permission_denied')

    def test_get_second_details(self):
        '''
        Ensure that we can get any details of an order if we logged in as its owner
        '''
        order_id = self.o2.data['id']
        response = self.client.get(
            f'/order/{order_id}',
            format='json',
            HTTP_AUTHORIZATION=self.token_1
        )

        order_model = models.Order.objects.get(id=order_id)
        expected_result = serializers.OrderSerializer(order_model)

        self.assertEqual(response.data, expected_result.data)
