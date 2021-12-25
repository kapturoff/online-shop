from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from products.models import Category, Product

test_data = {
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
    'user data without a password':
        {
            'username': 'test1',
            'email': 'test1@test.com'
        },
    'user data without an email':
        {
            'username': 'test1',
            'password': 'testpassword',
        },
    'product data':
        {
            'name': 't-shirt',
            'price': 5.28,
            'description': 'abooba',
            'img': 'https://google.com',
            'amount_remaining': 30,
            'size': 'L',
            'color': 'red',
        }
}


class RegistrationTests(APITestCase):
    def test_create_user(self):
        '''
        Ensure we can create a new user
        '''
        response = self.client.post(
            '/register', test_data['user data 1'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'test1')

    def test_create_user_without_password(self):
        '''
        Ensure we cannot create a new user without a password
        '''
        response = self.client.post(
            '/register',
            test_data['user data without a password'],
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0].code, 'required')

    def test_create_user_without_email(self):
        '''
        Ensure we cannot create a new user without an email
        '''
        response = self.client.post(
            '/register', test_data['user data without an email'], format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0].code, 'required')

    def test_create_user_with_existing_username(self):
        '''
        Ensure we cannot create a new user if he chose an existing username
        '''

        # Using same data for registering the one user twice
        self.client.post('/register', test_data['user data 1'], format='json')
        response2 = self.client.post(
            '/register', test_data['user data 1'], format='json'
        )

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['username'][0].code, 'invalid')


class UserDetailsTest(APITestCase):
    def setUp(self):
        self.client.post('/register', test_data['user data 1'], format='json')
        self.client.post('/register', test_data['user data 2'], format='json')

    def test_get_user_details(self):
        '''
        Ensure we can get details of an user's bio
        '''
        response = self.client.get('/users/1', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['username'], 'test1')


class WishlistTest(APITestCase):
    def setUp(self):
        category = Category(name='top clothes')
        category.save()
        product = Product(**test_data['product data'], category=category)
        product.save()

        self.client.post('/register', test_data['user data 1'], format='json')
        self.token_1 = self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']
        self.client.post('/register', test_data['user data 2'], format='json')
        self.token_2 = self.client.post(
            '/token', test_data['user data 2'], format='json'
        ).data['token']

    def test_get_user_wishlist(self):
        '''
        Ensure we can get user's wish list if we logged in as its owner
        '''
        response = self.client.get(
            '/users/1/wishlist',
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_other_user_wishlist(self):
        '''
        Ensure we cannot get user's wish list if we logged in as not its owner
        '''
        response = self.client.get(
            '/users/2/wishlist',
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'].code, 'permission_denied')

    def test_add_item_to_wishlist(self):
        '''
        Ensure we can add item to a user's wish list if we logged in as its owner
        '''
        response = self.client.post(
            '/users/1/wishlist', {'product_id': 1},
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['product'])

    def test_add_not_existing_item_to_wishlist(self):
        '''
        Ensure we cannot add a not existing item to an user's wish list
        '''
        response = self.client.post(
            '/users/1/wishlist', {'product_id': 999999},
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')

    def test_add_item_to_wishlist_without_providing_product_id(self):
        '''
        Ensure we get an error if we not provide product_id
        '''
        response = self.client.post(
            '/users/1/wishlist', {},
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'].code, 'invalid_data')


class CartsTest(APITestCase):
    def setUp(self):
        category = Category(name='top clothes')
        category.save()
        product = Product(**test_data['product data'], category=category)
        product.save()

        self.client.post('/register', test_data['user data 1'], format='json')
        self.token_1 = self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']
        self.client.post('/register', test_data['user data 2'], format='json')
        self.token_2 = self.client.post(
            '/token', test_data['user data 2'], format='json'
        ).data['token']

    def test_get_user_cart(self):
        '''
        Ensure we can get user's cart if we logged in as its owner
        '''
        response = self.client.get(
            '/users/1/cart',
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_other_user_cart(self):
        '''
        Ensure we cannot get user's cart if we logged in as not its owner
        '''
        response = self.client.get(
            '/users/2/cart',
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'].code, 'permission_denied')

    def test_add_item_to_cart(self):
        '''
        Ensure we can add item to a user's cart if we logged in as its owner
        '''
        response = self.client.post(
            '/users/1/cart', {
                'product_id': 1,
                'amount': 5
            },
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['product'])
        self.assertTrue(response.data['amount'])

    def test_add_not_existing_item_to_cart(self):
        '''
        Ensure we cannot add a not existing item to an user's cart
        '''
        response = self.client.post(
            '/users/1/cart', {
                'product_id': 999999,
                'amount': 5
            },
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')

    def test_add_item_to_cart_without_providing_product_id(self):
        '''
        Ensure we get an error if we not provide product_id
        '''
        response = self.client.post(
            '/users/1/cart', {'amount': 5},
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'].code, 'invalid_data')

    def test_add_item_to_cart_without_providing_amount(self):
        '''
        Ensure we get an error if we not provide amount
        '''

        response = self.client.post(
            '/users/1/cart', {'product_id': 1},
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'].code, 'invalid_data')


class WishlistItemDeleteTest(APITestCase):
    def setUp(self):
        category = Category(name='top clothes')
        category.save()
        product = Product(**test_data['product data'], category=category)
        product.save()

        self.client.post('/register', test_data['user data 1'], format='json')
        self.token_1 = self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']

        self.client.post('/register', test_data['user data 2'], format='json')
        self.token_2 = self.client.post(
            '/token', test_data['user data 2'], format='json'
        ).data['token']

    def test_delete_one_item(self):
        '''
        Test that we can delete one item from wishlist
        '''
        self.client.post(
            '/users/1/wishlist', {'product_id': 1},
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )  # Adding item to wish list

        response = self.client.delete(
            '/users/1/wishlist/1/delete',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        user = User.objects.get(id=1)

        self.assertFalse(response.data)  # Because it responses with None
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(user.wishlist.all()), [])

    def test_delete_multiple_item(self):
        '''
        Test that we can delete one item from wishlist
        '''
        # Add item three times
        for i in range(0, 3):
            self.client.post(
                '/users/1/wishlist', {'product_id': 1},
                format='json',
                HTTP_AUTHORIZATION='Token ' + self.token_1
            )

        response_1 = self.client.delete(
            '/users/1/wishlist/1/delete',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )
        response_2 = self.client.delete(
            '/users/1/wishlist/2/delete',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )
        response_3 = self.client.delete(
            '/users/1/wishlist/3/delete',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        user = User.objects.get(id=1)

        self.assertFalse(response_1.data)
        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertFalse(response_2.data)
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertFalse(response_3.data)
        self.assertEqual(response_3.status_code, status.HTTP_200_OK)
        self.assertEqual(list(user.wishlist.all()), [])

    def test_delete_one_item_logged_out(self):
        '''
        Test that we cannot delete anything if we're not authorized
        '''
        # Adding item to wish list
        self.client.post(
            '/users/1/wishlist', {'product_id': 1},
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        response = self.client.delete('/users/1/wishlist/1/delete')

        user = User.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')
        self.assertEqual(
            len(user.wishlist.all()), 1
        )  # Because there's only one item remained not deleted

    def test_delete_item_that_does_not_exist(self):
        '''
        Test that we cannot delete items that does not exist
        '''
        response = self.client.delete(
            '/users/1/wishlist/9999/delete',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        user = User.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')