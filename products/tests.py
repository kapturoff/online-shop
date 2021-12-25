from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Product, Category, Review
from .serializers import CategorySerializer, ProductListSerializer, ProductSerializer, ReviewSerializer

test_data = {
    'category 1': {
        'name': 'top clothes',
    },
    'category 2': {
        'name': 'pants',
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
    'review 1': {
        'liked': True,
        'review_text': 'Awesome t-shirt!'
    },
    'review 2': {
        'liked': False,
        'review_text': 'I hate this t-shirt!'
    },
    'review without liked field': {
        'review_text': 'Awesome t-shirt!'
    },
    'review without caption': {
        'liked': True,
    },
    'user':
        {
            'username': 'john',
            'password': 'johnsstrongpassword',
            'email': 'john@jonny.jo'
        }
}


class CategoriesTest(APITestCase):
    def setUp(self) -> None:
        self.c1 = Category(**test_data['category 1'])
        self.c2 = Category(**test_data['category 2'])
        self.c1.save()
        self.c2.save()

        self.p1 = Product(**test_data['product 1'], category=self.c1)
        self.p2 = Product(**test_data['product 2'], category=self.c1)

        self.p1.save()
        self.p2.save()

    def test_get_list_of_categories(self):
        '''
        Make sure that we can get a list of all saved categories in the database
        '''
        expected_result = CategorySerializer([self.c1, self.c2], many=True)
        response = self.client.get('/categories')

        self.assertEquals(response.data, expected_result.data)

    def test_get_details_of_certain_category(self):
        '''
        Make sure that we can get details of the certain category (including all its products)
        '''
        expected_result = ProductListSerializer(self.c1)
        response = self.client.get('/categories/top%20clothes')

        self.assertEquals(response.data, expected_result.data)

    def test_get_details_of_not_existing_category(self):
        '''
        Make sure that we cannot get details of the category that does not exist
        '''
        response = self.client.get('/categories/category_that_does_not_exist')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')


class ProductsTest(APITestCase):
    def setUp(self) -> None:
        self.c1 = Category(**test_data['category 1'])
        self.c2 = Category(**test_data['category 2'])
        self.c1.save()
        self.c2.save()

        self.p1 = Product(**test_data['product 1'], category=self.c1)
        self.p2 = Product(**test_data['product 2'], category=self.c1)

        self.p1.save()
        self.p2.save()

    def test_get_product(self):
        '''
        Make sure that we can access product details
        '''
        expected_result = ProductSerializer(self.p1)
        response = self.client.get('/categories/top%20clothes/1')

        self.assertEquals(response.data, expected_result.data)

    def test_get_second_product(self):
        '''
        Make sure that we get other result when we asks for another product details
        '''
        expected_result = ProductSerializer(self.p2)
        response = self.client.get('/categories/top%20clothes/2')

        self.assertEquals(response.data, expected_result.data)

    def test_product_has_fields(self):
        '''
        Make sure that a returned product has all important fields
        '''
        response = self.client.get('/categories/top%20clothes/1')
        data = response.data

        self.assertEqual(data['name'], test_data['product 1']['name'])
        self.assertEqual(data['img'], test_data['product 1']['img'])
        self.assertEqual(data['price'], str(test_data['product 1']['price']))
        self.assertEqual(
            data['amount_remaining'], test_data['product 1']['amount_remaining']
        )
        self.assertEqual(data['size'], test_data['product 1']['size'])
        self.assertEqual(data['color'], test_data['product 1']['color'])
        self.assertEqual(
            data['description'], test_data['product 1']['description']
        )

    def test_get_product_that_does_not_exist(self):
        '''
        Make sure that we cannot get details of the product that does not exist
        '''
        response = self.client.get('/categories/top%20clothes/9999')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')


class ReviewListTest(APITestCase):
    def setUp(self) -> None:
        self.c1 = Category(**test_data['category 1'])
        self.c2 = Category(**test_data['category 2'])
        self.c1.save()
        self.c2.save()

        self.p1 = Product(**test_data['product 1'], category=self.c1)
        self.p2 = Product(**test_data['product 2'], category=self.c1)
        self.p1.save()
        self.p2.save()

        self.user = User.objects.create_user(**test_data['user'])
        self.user.save()

        self.r1 = Review(
            **test_data['review 1'], author=self.user, product=self.p1
        )
        self.r2 = Review(
            **test_data['review 2'], author=self.user, product=self.p1
        )
        self.r1.save()
        self.r2.save()

    def test_get_review_list(self):
        '''
        Make sure that API returns list of reviews
        '''
        expected_result = ReviewSerializer([self.r1, self.r2], many=True)
        response = self.client.get('/categories/top%20clothes/1/reviews')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result.data)

    def test_get_empty_review_list(self):
        '''
        API returns empty list if there are no reviews below product
        '''
        expected_result = ReviewSerializer([], many=True)
        response = self.client.get('/categories/top%20clothes/2/reviews')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result.data)

    def test_get_review_invalid_id(self):
        '''
        Ensure that API throws an error if we're trying to get list of reviews from product that does not exist
        '''
        response = self.client.get('/categories/top%20clothes/999999/reviews')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')


class ReviewCreateTest(APITestCase):
    def setUp(self) -> None:
        self.c1 = Category(**test_data['category 1'])
        self.c1.save()

        self.p1 = Product(**test_data['product 1'], category=self.c1)
        self.p1.save()

        self.user = User.objects.create_user(**test_data['user'])
        self.user.save()

        self.user_token = 'Token ' + self.client.post(
            '/token', test_data['user'], format='json'
        ).data['token']

    '''
    [x] product_id, logged in, liked, review_text
    [x] product_id, logged in, liked, review_text (x2)
    [x] product_id is invalid, logged in, liked, review_text
    [] product_id is valid, logged out, liked, review_text
    [x] product_id is valid, logged in, no liked, review_text
    [] product_id, logged in, liked, no review_text
    '''

    def test_create_review(self):
        '''
        Ensure that we can create the new review if we logged in, pass valid 
        product ID and provide fields "liked" and "review_text".
        '''
        review = Review(
            **test_data['review 1'], author=self.user, product=self.p1
        )  # Not saving!

        # Because the ID is not being set automatically
        # if we don't save model to the database, we must set it manually
        review.id = 1
        expected_result = ReviewSerializer(review)
        response = self.client.post(
            '/categories/top%20clothes/1/reviews/create',
            test_data['review 1'],
            format='json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(expected_result.data, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get review from database after request
        saved_review = Review.objects.get(id=1)

        # Test that the review is now saved in database
        self.assertTrue(saved_review)

    def test_create_review_twice(self):
        '''
        Ensure that we can create two new reviews in a row if we logged in, pass valid 
        product IDs and provide fields "liked" and "review_text".
        '''
        self.client.post(
            '/categories/top%20clothes/1/reviews/create',
            test_data['review 1'],
            format='json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.client.post(
            '/categories/top%20clothes/1/reviews/create',
            test_data['review 2'],
            format='json',
            HTTP_AUTHORIZATION=self.user_token
        )

        # Get reviews from database after requests
        saved_review_1 = Review.objects.get(id=1)
        saved_review_2 = Review.objects.get(id=2)

        # Test that the reviews are now saved in database
        self.assertTrue(saved_review_1)
        self.assertTrue(saved_review_2)

    def test_create_review_invalid_id(self):
        '''
        Test that we cannot create new review for product that does not exist
        '''
        response = self.client.post(
            '/categories/top%20clothes/999999999/reviews/create',
            test_data['review 1'],
            format='json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')

        # Get review if any of them exist
        review = Review.objects.filter(id=1).first()

        # Test that nothing was saved in database
        self.assertFalse(review)

    def test_create_review_no_liked(self):
        '''
        Test that we cannot create new review without providing "liked" field
        '''
        response = self.client.post(
            '/categories/top%20clothes/1/reviews/create',
            test_data['review without liked field'],
            format='json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

        # Get review if any of them exist
        review = Review.objects.filter(id=1).first()

        # Test that nothing was saved in database
        self.assertFalse(review)

    def test_create_review_no_liked(self):
        '''
        Test that we cannot create new review without providing "liked" field
        '''
        response = self.client.post(
            '/categories/top%20clothes/1/reviews/create',
            test_data['review without liked field'],
            format='json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

        # Get review if any of them exist
        review = Review.objects.filter(id=1).first()

        # Test that nothing was saved in database
        self.assertFalse(review)

    def test_create_review_no_review_text(self):
        '''
        Test that we cannot create new review without providing "review_text" field
        '''
        response = self.client.post(
            '/categories/top%20clothes/1/reviews/create',
            test_data['review without caption'],
            format='json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0].code, 'invalid')

        # Get review if any of them exist
        review = Review.objects.filter(id=1).first()

        # Test that nothing was saved in database
        self.assertFalse(review)

    def test_create_review_logged_out(self):
        '''
        Test that we cannot create new review without authorization
        '''
        response = self.client.post(
            '/categories/top%20clothes/1/reviews/create',
            test_data['review 1'],
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

        # Get review if any of them exist
        review = Review.objects.filter(id=1).first()

        # Test that nothing was saved in database
        self.assertFalse(review)