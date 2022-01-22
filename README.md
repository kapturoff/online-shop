# online-shop
Basic backend for an online shop

## Installation

Before starting the project you need to make sure that you have installed _Python 3.9_, its package manager _pip_ and _pyvenv_ for working with the virtual environments.

Let's start with the installing of this project requirements. This is recommended to create virual environment first, then activate it and only then install dependencies of project.

```
python -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

After this, you need to create a new database for your instance of the online shop, which will store shop data.

```shell
python manage.py migrate
```

Then create superuser to access the admin site via him.

```
python manage.py createsuperuser
```

And after all, you're finally able to run the server.

```
python manage.py runserver
```

## Testing API

> All the examples use _curl_ to transfer data via terminal. I also assume that you put all the data for the request body in the _"request_data.json"_ file that is in the directory from which you are working with curl.


### Accessing admin site
The admin panel of Django is the HTML page, so you access it using the browser. It's placed on _/admin_ endpoint. 

You can use the admin panel to add new products or categories to shop and also manage the users' data.


### Registering of the new users
You can register new user by sending POST request to _/register_ endpoint.

Request body must contain:
```python
{ 
  "username": string, 
  "password": string, 
  "email": string
}
```

Example:
```
curl -d "@request_data.json" -H 'Content-Type: application/json; indent=4' -H "Accept: application/json; indent=4" -X POST http://localhost:8000/register
```

Returns: ```User```

After user registered, you can get data of his profile by passing his ID as request parameter like this — _/users/<user_id>_

Example:
```
curl -d "@request_data.json" -H 'Content-Type: application/json; indent=4' -H "Accept: application/json; indent=4" -X POST http://localhost:8000/register
```

Returns: ```User```


### Getting categories
Every product is placed in a category. To get list of all categories, you need to send GET request to _/categories_.

Example:
```
curl -H "Accept: application/json; indent=4" -X GET http://localhost:8000/categories
```

Returns: ```Category[]```

Category model contains these two fields:
```python
{ 
  "id": integer,
  "name": string
}
```


### Getting list of the products in a category and the product details
To get list of the products in a certain category, you need to send GET request to _/categories/<category_name>_.

Example:
```
curl -H "Accept: application/json; indent=4" -X GET http://localhost:8000/categories/pants
```

Returns: ```Product[]```

Product model contains the following fields:
```python
{
  "id": integer,
  "category": Category,
  "img": string,
  "name": string,
  "price": float,
  "old-price": float,
  "amount_remaining": integer,
  "description": string,
  "datetime_created": string, # Representing datetime.datetime instance
  "size": string,
  "color": string,
  "reviews_count": integer,
  "likes_count": integer,
  "dislikes_count": integer,
  "in_stock": boolean,
}
```

To get data about a certain product, pass its ID as request parameter like that: _/categories/<category_name>/<product_id>_

Example:
```
curl -H "Accept: application/json; indent=4" -X GET http://localhost:8000/categories/pants/1
```

Returns: ```Product```


### Working with users' wish lists
You can get your wish list by accessing _/user/<your_user_id>/wishlist_ by GET request. 
If you try to access someone else's wish list, you get Permission denied error. For this reason you need be authenticated to access wish list.

Example: 
```
curl -u my_username:my_ultra_hard_password -H "Accept: application/json; indent=4" -X GET http://localhost:8000/users/1/wishlist
```

Responses with: `WishlistItem[]`

Wishlist item contains the only field:
```python
{
  "product": Product
}
```

To add a new item to your wish list, you need to send ```WishlistItem``` in POST request to _/users/<your_user_id>/wishlist_. Do not forget to be authenticated.

Example:
```
curl -u my_username:my_ultra_hard_password -d "@request_data.json" -H "Content-Type: application/json; indent=4" -H "Accept: application/json; indent=4" -X POST http://localhost:8000/users/1/wishlist
```

Returns: ```WishlistItem```


### Working with users' carts
Carts are very similar in behavior with the wish lists, but they also have "amount" field in the cart item model. You still need to be authenticated and use only your own ID in request parameters to access it.

Getting list of items in the cart:
```
curl -u my_username:my_ultra_hard_password -H "Accept: application/json; indent=4" -X GET http://localhost:8000/users/1/cart
```

Returns: ```CartItem[]```

Cart item model has the following fields:
```python
{
  "product": Product,
  "amount": integer
}
```

Adding a new item to the cart is available by sending POST request with the cart item model in the request body:
```
curl -u my_username:my_ultra_hard_password -d "@request_data.json" -H "Content-Type: application/json; indent=4" -H "Accept: application/json; indent=4" -X POST http://localhost:8000/users/1/cart
```

Returns: ```CartItem```


### Making purchases
To create an order, you need to send the POST request to _/order_ endpoint. Request body of this request should contain Order model data.

Order model contains these fields:
```python
{
    "status": OrderStatus, # You don't have to pass this field if you're creating a new order. It assignes automatically when creating an order.
    "items": CartItem[],
    "address_to_send": string,
    "mobile_number": string,
    "first_name": string,
    "last_name": string,
    "email": string
}
```

Example:
```
curl -u my_username:my_ultra_hard_password -d "@request_data.json" -H 'Content-Type: application/json; indent=4' -H "Accept: application/json; indent=4" -X POST "http://localhost:8000/order"
```

Returns: ```Order```

After it, you need to pay for your order. Since the project does not use any real payment service, I imitated a behavior of online shop as if it were using it. That means that you still have to get a link to the third-party payment service page first, then follow this link and, if you paid successfully, the payment service would have to send notification to online shop about a successful payment.

The only differences with my implementation of a payment service are that you need to send this notification to our API manually and that you do not really need to spend money while testing it :)

First of all, get the payment details and link from online shop API. Pass an order ID that you had got from the previous request as a parameter in _/order/<order_id>/pay_:
```
curl -u my_username:my_ultra_hard_password -H "Accept: application/json; indent=4" -X GET http://localhost:8000/order/4/pay
```

Returns: `Payment`

Payment fields are:
```python
{
  "order": Order,
  "payment_page_url": string,
  "payment_service_id": string, # Payment services usually set their own ID for orders so we need to store them too
  "secret_key": string # In real online shop you do not get this field due the security reasons, but it will be used in my approach of implementation of a pseudo payment service
}
```

You actually can visit the payment page URL, but you will not see anything but a placeholder

Then you have to send notification to API of the shop as if you were a third-party payment service. Since we haven't got a list of IPs of payment service, the shop checks the authenticity of payment by the comparing of the secret key of order stored in our database and secret key that third-party service sends. This is why you see secret key in the previous request.

Body of the next request must contain:
```python
{
  "id": payment_service_id,
  "status": "successed" | "waiting_for_capture" | "cancelled",
  "metadata": {
    "secret_key": secret_key
  }
}
```

Example:
```
curl -d "@request_data.json" -H 'Content-Type: application/json; indent=4' -H "Accept: application/json; indent=4" -X POST "http://localhost:8000/webhooks"
```

Returns: ```Order```

After all of these manipulations, order finally gets his status «Paid»! You can verify that by visiting the admin site.

### Writing reviews for products
After you bought a product, you may want to send a review about it. This can be accomplished by sending POST request here: `categories/<category_name>/<product_id>/reviews/create`.

Body of this request must include:
```python
{
  "review_text": string,
  "liked": boolean,
}
```

More than that, you need to be authenticated to send this kind of the request.

Example of creating a review:
```
curl -u my_username:my_ultra_hard_password -d "@review.json" -H "Content-Type: application/json" -H "Accept: application/json; indent=4" -X POST http://localhost:8000/categories/t_shirts/1/reviews/create
```

Returns: ```Review```

Review schema:
```python
{
  "author": User,
  "liked": boolean,
  "review_text": string,
  "product": Product,
}
```


### Getting the list of reviews
You also may be interested in getting all of the reviews (comments) about a certain product. To get them, you need to access the following endpoint `categories/<category_name>/<product_id>/reviews`.

Example of request:
```
curl -H "Accept: application/json; indent=4" -X GET http://localhost:8000/categories/top%20clothes/2/reviews
```

Returns: ```Review[]```

You also can get the list of reviews made by a certain user accessing the following endpoint: `users/<int:user_id>/reviews`.

Example:
```
curl -H "Accept: application/json; indent=4" -X GET http://localhost:8000/users/1/reviews
```

Returns: ```Review[]```

### Deleting reviews
You can delete a review of yours by sending DELETE request here: `users/<int:user_id>/reviews/<int:review_id>`. You have to be authenticated as a this review creator.

Example of request:
```
curl -u my_username:my_ultra_hard_password -H "Accept: application/json; indent=4" -X DELETE http://localhost:8000/users/1/reviews/3
```

Returns: ```None```

### Deleting items from the cart or the wish list
You can delete an item from these lists by accessing `users/<int:user_id>/wishlist/<int:wishlist_item_id>` for deleting wish list item and accessing `users/<int:user_id>/cart/<int:cart_item_id>` if you want to delete item from the cart. You need to be the owner of a wish list / a cart if you want to delete from it and you need to be sending a DELETE method in both cases.

Example:
```
curl -u my_username:my_ultra_hard_password -H "Accept: application/json; indent=4" -X DELETE http://localhost:8000/users/1/wishlist/1
```

Returns: ```None```

### Using tokens in the request authentication
You can get a token and authenticate your requests with it, instead of using the standard login:pass authentication. To get it, you need to be registered and then access `/token` endpoint using standart authentication. This is going be look like:

```
curl -u my_username:my_ultra_hard_password -H "Accept: application/json; indent=4" -X GET http://localhost:8000/token
```

Returns: ```{ "token": string }```

Value of the field "token" is your token itself. You can now authenticate all of your requests using it. To do it, you must additionally include _Authorization header_ in your requests. Let's make a request via curl using this header:

```
curl -H "Authorization: Token d084de71184336f57d3b673b9cc3713209eb7860" -H "Content-Type: application/json" -H "Accept: application/json; indent=4" -X GET http://localhost:8000/users/2/cart
```

### Search for a certain product
If you're not sure what are you looking for in the online shop, you can search for products using `/search` endpoint. It works via query parameters, so you need to pass them into requests. 

Example of using:
```
curl -H "Accept: application/json; indent=4" -X GET "http://localhost:8000/products/search?q=t-s&lte=3&gte=2.2"
```

Returns: `Product[]`

Parameter `q=<str>` is responsible for searching by name and it searches the products that starts with the value of this property. For example, `/search?q=pa` will find all the _pajamas_, _panties_, _parachute pants_ in the shop. This is the only required parameter out of three.

Parameter `lte=<float>` is responsible for searching by cost. It filters all of products that does not cost less than value of the parameter. `/search?q=pa&lte=10.5` will keep only those products whose price is less then 10.5$.

Parameter `gte=<float>` is antipod of parameter `lte=` and it searchs for only those products whose price is more than value of the parameter.
