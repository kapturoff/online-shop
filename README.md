# online-shop
Backend of online shop

## Installation

Before starting the project you need to make sure that you have installed _Python 3.9_, its packet manager _pip_ and _pyvenv_ for working with virtual environments.

Let's start with the installing of this project requirements. This is recommended to create virual environment first, activate it and only then install dependencies.

```
python -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

After this, you need to create a new database for your instance of the online shop, which will store its data.

```shell
python manage.py migrate
```

Create superuser to access the admin site via him.

```
python manage.py createsuperuser
```

And after all, you're finally able to run the server.

```
python manage.py runserver
```

## Testing API

> All the examples use _curl_ to transfer data via terminal. I also assume that you put all the information for the request in the _"request_data.json"_ file in the directory from which you are working with curl.


### Accessing admin site
The admin panel of Django is the HTML page, so you access it from browser. It's placed on _/admin_ endpoint. 

You can use the admin panel to add new products or categories to shop and also manage the users' data.


### Registering new users
You can register new user by sending POST request to _/register_

Request body must contain:
```python
{ 
  "username": string, 
  "password": string, 
  "email": string
}
```

Example of request:
```
curl -d "@request_data.json" -H 'Content-Type: application/json; indent=4' -X POST http://localhost:8000/register
```

Returns: ```User```

After it, you can get data of user by passing his ID as request parameter like this — _/users/<user_id>_

Example of request:
```
curl -d "@request_data.json" -H 'Content-Type: application/json; indent=4' -X POST http://localhost:8000/register
```

Returns: ```User```


### Getting categories
Every product is placed in a category. To get list of all categories, you need to send GET request to _/categories_.

Example of request:
```
curl -H 'Content-Type: application/json; indent=4' -X GET http://localhost:8000/categories
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

Example of request:
```
curl -H 'Content-Type: application/json; indent=4' -X GET http://localhost:8000/categories/pants
```

Returns: ```Product```

Product model contains the following fields:
```python
{
  "id": integer,
  "category": Category,
  "link_to_image": string,
  "name": string,
  "price": float,
  "old-price": float,
  "amount_remaining": integer,
  "description": string,
  "datetime_created": string, # Representing datetime.datetime instance
  "size": string,
  "color": string,
}
```

To get data about a certain product, pass its ID as request parameter like that: _/category/<category_name>/<product_id>_

Example of request:
```
curl -H 'Content-Type: application/json; indent=4' -X GET http://localhost:8000/categories/pants/1
```

Returns: ```Product```


### Working with users' wish lists
You can get your wish list by accessing _/user/<your_user_id>/wishlist_ by GET request. 
If you try access someone else's wish list, you get Permission denied error. For this reason you need be authenticated to access wish list.

Example of request: 
```
curl -u my_username:my_ultra_hard_password -H "Content-Type: application/json; indent=4" -X GET http://localhost:8000/users/1/wishlist
```

Responses with: `WishlistItem[]`

Wishlist item contains the only field:
```python
{
  "product": Product
}
```

To add a new item to your wish list, you need to send ```WishlistItem``` in POST request to _/users/<your_user_id>/wishlist_. Do not forget to be authenticated.

Example of request:
```
curl -u my_username:my_ultra_hard_password -d "@request_data.json" -H "Content-Type: application/json; indent=4" -X POST http://localhost:8000/users/1/wishlist
```

Returns: ```WishlistItem```


### Working with users' carts
Carts are very similar in behavior with the wish lists, but they also have "amount" field in the cart item model. You still need to be authenticated and use only your own ID in request parameters to access it.

Getting list of items in the cart:
```
curl -u my_username:my_ultra_hard_password -H "Content-Type: application/json; indent=4" -X GET http://localhost:8000/users/1/cart
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
curl -u my_username:my_ultra_hard_password -d "@request_data.json" -H "Content-Type: application/json; indent=4" -X POST http://localhost:8000/users/1/cart
```

Returns: ```CartItem```


### Making purchases
To buy some products, you need to send POST request to _/order_ endpoint. Request body of this request should contain Order model data.

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

Example of request:
```
curl -u my_username:my_ultra_hard_password -d "@request_data.json" -H 'Content-Type: application/json; indent=4' -X POST "http://localhost:8000/order"
```

Returns: ```Order```

After it, you need to pay for your order. Since the project does not use any real payment service, I emulated the behavior of online shop as if it were using it. That means that you have to get a link to the third-party payment service page first, then follow this link and, if you paid successfully, the payment service would have to send notification to online shop about successful payment.

The only differences with my implementation of a payment service are that you need send this notification to our API manually and that you do not really need to spend money while testing :)

First of all, get the payment details and link from online shop API. Pass an order ID that you had got from the previous request as a paremeter in _/order/<order_id>/pay_:
```
curl -u my_username:my_ultra_hard_password -H "Content-Type: application/json; indent=4" -X GET http://localhost:8000/order/4/pay
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

Then you have to send notification to API of the shop as if you were a third-party payment service. Since we haven't got a list of IPs of payment service, the shop checks the authenticity of payment by comparing the secret key of order stored in our database and secret key that third-party service sends. That is why you see secret key in the previous request.

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

Returns: ```Order```

After all of these manipulations, order finally gets his status «Paid»!
