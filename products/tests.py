from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product, Category
from .serializers import CategorySerializer, ProductListSerializer, ProductSerializer

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

    def test_product_has_fields(self):
        '''
        Make sure that a returned product has all important fields
        '''
        response = self.client.get('/categories/top%20clothes/1')
        data = response.data

        self.assertEqual(data['name'], test_data['product 1']['name'])
        self.assertEqual(data['img'], test_data['product 1']['img'])
        self.assertEqual(data['price'], str(test_data['product 1']['price']))
        self.assertEqual(data['amount_remaining'], test_data['product 1']['amount_remaining'])
        self.assertEqual(data['size'], test_data['product 1']['size'])
        self.assertEqual(data['color'], test_data['product 1']['color'])
        self.assertEqual(data['description'], test_data['product 1']['description'])

    def test_get_product_that_does_not_exist(self):
        '''
        Make sure that we cannot get details of the product that does not exist
        '''
        response = self.client.get('/categories/top%20clothes/9999')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'].code, 'not_found')
