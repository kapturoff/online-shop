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
        },
    'review data': {
        'liked': True,
        'review_text': 'Awesome t-shirt!'
    }
}


class RegistrationTest(APITestCase):
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
        self.user = self.client.post(
            '/register', test_data['user data 1'], format='json'
        ).data

    def test_get_user_details(self):
        '''
        Ensure we can get details of an user's bio
        '''
        response = self.client.get(f'/users/{self.user["id"]}', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'test1')


class WishlistTest(APITestCase):
    def setUp(self):
        category = Category(name='top clothes')
        category.save()

        self.p1 = Product(**test_data['product data'], category=category)
        self.p1.save()

        self.user_1 = self.client.post(
            '/register', test_data['user data 1'], format='json'
        ).data
        self.token_1 = self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']

        self.user_2 = self.client.post(
            '/register', test_data['user data 2'], format='json'
        ).data
        self.token_2 = self.client.post(
            '/token', test_data['user data 2'], format='json'
        ).data['token']

    def test_get_user_wishlist(self):
        '''
        Ensure we can get user's wish list if we logged in as its owner
        '''
        response = self.client.get(
            f'/users/{self.user_1["id"]}/wishlist',
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
            f'/users/{self.user_2["id"]}/wishlist',
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
            f'/users/{self.user_1["id"]}/wishlist', {'product_id': self.p1.id},
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
            f'/users/{self.user_1["id"]}/wishlist', {'product_id': 999999},
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
            f'/users/{self.user_1["id"]}/wishlist', {},
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'].code, 'invalid_data')


class CartsTest(APITestCase):
    def setUp(self):
        category = Category(name='top clothes')
        category.save()

        self.p1 = Product(**test_data['product data'], category=category)
        self.p1.save()

        self.user_1 = self.client.post(
            '/register', test_data['user data 1'], format='json'
        ).data
        self.token_1 = self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']

        self.user_2 = self.client.post(
            '/register', test_data['user data 2'], format='json'
        ).data
        self.token_2 = self.client.post(
            '/token', test_data['user data 2'], format='json'
        ).data['token']

    def test_get_user_cart(self):
        '''
        Ensure we can get user's cart if we logged in as its owner
        '''
        response = self.client.get(
            f'/users/{self.user_1["id"]}/cart',
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
            f'/users/{self.user_2["id"]}/cart',
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
            f'/users/{self.user_1["id"]}/cart', {
                'product_id': self.p1.id,
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
            f'/users/{self.user_1["id"]}/cart', {
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
            f'/users/{self.user_1["id"]}/cart', {'amount': 5},
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
            f'/users/{self.user_1["id"]}/cart', {'product_id': self.p1.id},
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'].code, 'invalid_data')


class WishlistItemDeleteTest(APITestCase):
    def setUp(self):
        category = Category(name='top clothes')
        category.save()

        self.p1 = Product(**test_data['product data'], category=category)
        self.p1.save()

        self.user_1 = self.client.post(
            '/register', test_data['user data 1'], format='json'
        ).data
        self.token_1 = self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']

        self.user_2 = self.client.post(
            '/register', test_data['user data 2'], format='json'
        ).data
        self.token_2 = self.client.post(
            '/token', test_data['user data 2'], format='json'
        ).data['token']

    def test_delete_one_item(self):
        '''
        Test that we can delete one item from wishlist
        '''
        wishlist_item = self.client.post(
            f'/users/{self.user_1["id"]}/wishlist', {
                'product_id': self.p1.id
            },
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data  # Adding item to the wish list

        response = self.client.delete(
            f'/users/{self.user_1["id"]}/wishlist/{wishlist_item["id"]}',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        # We need to get user from database and not use already
        # gotten user from self.user_1, because it has no wish list
        # (because this list is unnecessary right after registration)
        user = User.objects.get(id=self.user_1['id'])

        self.assertFalse(response.data)  # Because it responses with None
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(user.wishlist.all()), [])

    def test_delete_multiple_items(self):
        '''
        Test that we can delete one item from wishlist
        '''
        # Add item to the wish list tree times
        for i in range(0, 3):
            self.client.post(
                f'/users/{self.user_1["id"]}/wishlist', {
                    'product_id': self.p1.id
                },
                format='json',
                HTTP_AUTHORIZATION='Token ' + self.token_1
            ).data

        wishlist = self.client.get(
            f'/users/{self.user_1["id"]}/wishlist',
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data

        for wishlist_item in wishlist:
            response = self.client.delete(
                f'/users/{self.user_1["id"]}/wishlist/{wishlist_item["id"]}',
                format='json',
                HTTP_AUTHORIZATION='Token ' + self.token_1
            )

            self.assertFalse(response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # We need to get user from database and not use already
        # gotten user from self.user_1, because it has no wish list
        # (because this list is unnecessary right after registration)
        user = User.objects.get(id=self.user_1['id'])

        self.assertEqual(list(user.wishlist.all()), [])

    def test_delete_one_item_logged_out(self):
        '''
        Test that we cannot delete anything if we're not authorized
        '''
        wishlist_item = self.client.post(
            f'/users/{self.user_1["id"]}/wishlist', {
                'product_id': self.p1.id
            },
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data  # Adding item to the wish list

        response = self.client.delete(
            f'/users/{self.user_1["id"]}/wishlist/{wishlist_item["id"]}'
        )

        # We need to get user from database and not use already
        # gotten user from self.user_1, because it has no wish list
        # (because this list is unnecessary right after registration)
        user = User.objects.get(id=self.user_1['id'])

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
            f'/users/{self.user_1["id"]}/wishlist/9999',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')


class CartItemDeleteTest(APITestCase):
    def setUp(self):
        category = Category(name='top clothes')
        category.save()

        self.p1 = Product(**test_data['product data'], category=category)
        self.p1.save()

        self.user_1 = self.client.post(
            '/register', test_data['user data 1'], format='json'
        ).data
        self.token_1 = self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']

        self.user_2 = self.client.post(
            '/register', test_data['user data 2'], format='json'
        ).data
        self.token_2 = self.client.post(
            '/token', test_data['user data 2'], format='json'
        ).data['token']

    def test_delete_one_item(self):
        '''
        Test that we can delete one item from cart
        '''
        cart_item = self.client.post(
            f'/users/{self.user_1["id"]}/cart', {
                'product_id': self.p1.id,
                'amount': 1
            },
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data  # Adding items to the cart

        response = self.client.delete(
            f'/users/{self.user_1["id"]}/cart/{cart_item["id"]}',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        # We need to get user from database and not use already
        # gotten user from self.user_1, because it has no cart
        # (because this list is unnecessary right after registration)
        user = User.objects.get(id=self.user_1['id'])

        self.assertFalse(response.data)  # Because it responses with None
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(user.cart.all()), [])

    def test_delete_multiple_items(self):
        '''
        Test that we can delete one item from cart
        '''
        # Add item to the cart three times
        for i in range(0, 3):
            self.client.post(
                f'/users/{self.user_1["id"]}/cart', {
                    'product_id': self.p1.id,
                    'amount': 1
                },
                format='json',
                HTTP_AUTHORIZATION='Token ' + self.token_1
            ).data

        cart = self.client.get(
            f'/users/{self.user_1["id"]}/cart',
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data

        for cart_item in cart:
            response = self.client.delete(
                f'/users/{self.user_1["id"]}/cart/{cart_item["id"]}',
                format='json',
                HTTP_AUTHORIZATION='Token ' + self.token_1
            )

            self.assertFalse(response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # We need to get user from database and not use already
        # gotten user from self.user_1, because it has no cart
        # (because this list is unnecessary right after registration)
        user = User.objects.get(id=self.user_1['id'])

        self.assertEqual(list(user.cart.all()), [])

    def test_delete_one_item_logged_out(self):
        '''
        Test that we cannot delete anything if we're not authorized
        '''
        # Adding item to the cart
        cart_item = self.client.post(
            f'/users/{self.user_1["id"]}/cart', {
                'product_id': self.p1.id,
                'amount': 1,
            },
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data

        response = self.client.delete(
            f'/users/{self.user_1["id"]}/cart/{cart_item["id"]}'
        )

        # We need to get user from database and not use already
        # gotten user from self.user_1, because it has no cart
        # (because this list is unnecessary right after registration)
        user = User.objects.get(id=self.user_1['id'])

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')
        self.assertEqual(
            len(user.cart.all()), 1
        )  # Because there's only one item remained not deleted

    def test_delete_item_that_does_not_exist(self):
        '''
        Test that we cannot delete items that does not exist
        '''
        response = self.client.delete(
            f'/users/{self.user_1["id"]}/cart/9999',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')


class ReviewDelete(APITestCase):
    def setUp(self):
        self.category = Category(name='top clothes')
        self.category.save()

        self.p1 = Product(**test_data['product data'], category=self.category)
        self.p1.save()

        self.user_1 = self.client.post(
            '/register', test_data['user data 1'], format='json'
        ).data
        self.token_1 = self.client.post(
            '/token', test_data['user data 1'], format='json'
        ).data['token']

        self.user_2 = self.client.post(
            '/register', test_data['user data 2'], format='json'
        ).data
        self.token_2 = self.client.post(
            '/token', test_data['user data 2'], format='json'
        ).data['token']

    def test_delete_one_review(self):
        '''
        Test that we can delete one review
        '''
        # Add a new review
        review = self.client.post(
            f'/categories/{self.category.name}/{self.p1.id}/reviews/create',
            test_data['review data'],
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data

        # Delete a just created review
        response = self.client.delete(
            f'/users/{self.user_1["id"]}/reviews/{review["id"]}',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertFalse(response.data)  # Because it responses with None
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that there's no review left made by this user
        reviews = self.client.get(f'/users/{self.user_1["id"]}/reviews').data
        self.assertEqual(reviews, [])

    def test_delete_multiple_reviews(self):
        '''
        Test that we can delete multiple reviews
        '''
        # Add review three times
        for _ in range(0, 3):
            self.client.post(
                f'/categories/{self.category.name}/{self.p1.id}/reviews/create',
                test_data['review data'],
                format='json',
                HTTP_AUTHORIZATION='Token ' + self.token_1
            )

        # Delete all the created reviews
        reviews = self.client.get(
            f'/users/{self.user_1["id"]}/reviews',
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data

        for review in reviews:
            response = self.client.delete(
                f'/users/{self.user_1["id"]}/reviews/{review["id"]}',
                format='json',
                HTTP_AUTHORIZATION='Token ' + self.token_1
            )

            self.assertFalse(response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that there's no review left made by this user
        reviews = self.client.get(f'/users/{self.user_1["id"]}/reviews').data
        self.assertEqual(reviews, [])

    def test_delete_one_review_logged_out(self):
        '''
        Test that we cannot delete anything if we're not authorized
        '''
        # Add a new review
        review = self.client.post(
            f'/categories/{self.category.name}/{self.p1.id}/reviews/create',
            test_data['review data'],
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data

        # Remove it
        response = self.client.delete(
            f'/users/{self.user_1["id"]}/reviews/{review["id"]}'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

        # Check that there's only one review left made by this user
        reviews = self.client.get(f'/users/{self.user_1["id"]}/reviews').data
        self.assertEqual(len(reviews), 1)

    def test_delete_review_that_does_not_exist(self):
        '''
        Test that we cannot delete reviews that does not exist
        '''
        response = self.client.delete(
            f'/users/{self.user_1["id"]}/cart/9999',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')

    def test_delete_review_by_other_user(self):
        '''
        Test that we cannot delete reviews that were made by other user
        '''
        # Add a new review
        review = self.client.post(
            f'/categories/{self.category.name}/{self.p1.id}/reviews/create',
            test_data['review data'],
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token_1
        ).data

        # Trying to delete a just created review
        response = self.client.delete(
            f'/users/{self.user_1["id"]}/reviews/{review["id"]}',
            HTTP_AUTHORIZATION='Token ' + self.token_2
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'].code, 'permission_denied')

        # Check that there's only one review left made by this user
        reviews = self.client.get(f'/users/{self.user_1["id"]}/reviews').data
        self.assertEqual(len(reviews), 1)
