from django import test
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Category, Product
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
            'mobile_number': '+12223334455',
            'first_name': 'Carl',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with no phone number':
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
            'first_name': 'Carl',
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with no first name':
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
            'last_name': 'Johnson',
            'email': 'hooba@booba.com'
        },
    'order with no last name':
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
            'email': 'hooba@booba.com'
        },
    'order with no email':
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
        },
    'order with product that does not exist':
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
                            'id': 9999,
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
    'order with the invalid amount of items':
        {
            'items':
                [
                    {
                        'product': {
                            'id': 1,
                        },
                        'amount': 9999
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

        default_order_status = models.OrderStatus(name="Created")
        default_order_status.save()

        self.client.post('/register', test_data['user data 1'], format='json')
        self.client.post('/register', test_data['user data 2'], format='json')

    def test_create_order(self):
        '''
        Ensure that we can create the order if a given data is valid
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order', test_data['valid order'], format='json'
        )

        order_model = models.Order.objects.get()
        expected_result = serializers.OrderSerializer(order_model)

        self.assertEqual(response.data, expected_result.data)

    def test_create_order_logged_out(self):
        '''
        Ensure that we can not create the order if we're not authenticated
        '''
        response = self.client.post(
            '/order', test_data['valid order'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

    def test_create_order_with_no_items(self):
        '''
        Ensure that we can not create the order if a given data has got no items
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order', test_data['order with no items'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_with_no_items_field(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "items"
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order', test_data['order with no items field'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_address(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "address"
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order', test_data['order with no address to send'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_phone_number(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "mobile_number"
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order', test_data['order with no phone number'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_first_name(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "mobile_number"
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order', test_data['order with no first name'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_last_name(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "mobile_number"
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order', test_data['order with no last name'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_without_email(self):
        '''
        Ensure that we can not create the order if a given data has got no field named "mobile_number"
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order', test_data['order with no email'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

    def test_create_order_with_not_existing_products(self):
        '''
        Ensure that we can not create the order if items in given data do not exist
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order',
            test_data['order with product that does not exist'],
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')

    def test_create_order_with_invalid_amount_of_products(self):
        '''
        Ensure that we cannot create the order if the user asked for a bigger count of product than exist in the database.
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.post(
            '/order',
            test_data['order with the invalid amount of items'],
            format='json'
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

        default_order_status = models.OrderStatus(name="Created")
        default_order_status.save()

        self.client.post('/register', test_data['user data 1'], format='json')
        self.client.post('/register', test_data['user data 2'], format='json')

        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        self.client.post('/order', test_data['valid order'], format='json')
        self.client.post('/order', test_data['valid order'], format='json')

        self.client.logout()
        self.client.login(
            username=test_data['user data 2']['username'],
            password=test_data['user data 2']['password']
        )
        self.client.post('/order', test_data['valid order'], format='json')

        self.o1 = models.Order.objects.get(id=1)
        self.o2 = models.Order.objects.get(id=2)
        self.o3 = models.Order.objects.get(id=3)

        self.client.logout()

    def test_get_details(self):
        '''
        Ensure that we can get details of an order if we logged in as its owner
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.get(
            '/order/1', format='json'
        )

        order_model = models.Order.objects.get(id=1)
        expected_result = serializers.OrderSerializer(order_model)

        self.assertEqual(response.data, expected_result.data)

    def test_get_details_logout(self):
        '''
        Ensure that we cannot get details of any order if we logged out
        '''
        response = self.client.get(
            '/order/1', format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

    def test_get_details_logged_in_as_not_owner(self):
        '''
        Ensure that we cannot get details of an order we logged in as not its owner
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.get(
            '/order/3', format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'].code, 'permission_denied')

    def test_get_second_details(self):
        '''
        Ensure that we can get any details of an order if we logged in as its owner
        '''
        self.client.login(
            username=test_data['user data 1']['username'],
            password=test_data['user data 1']['password']
        )

        response = self.client.get(
            '/order/2', format='json'
        )

        order_model = models.Order.objects.get(id=2)
        expected_result = serializers.OrderSerializer(order_model)

        self.assertEqual(response.data, expected_result.data)
