# How to run the app?

> First of all, you need to make sure that you have installed [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) (clickable if you need them to install).

1. Download the app using your git CLI and then move into the downloaded repository:
```
> git clone https://github.com/kapturoff/online-shop
> cd online-shop/
```

2. Edit your example.env file with your variables or create another .env file. **This is important to change SECRET_KEY value and SQL_\* variables because they're vulnerable and the app security depends on them.**

3. Edit your [docker-compose.yml](https://github.com/kapturoff/online-shop/blob/main/docker-compose.yml) depending on what you wrote in example.env file in the previous step. Don't forget to change env-file variable in the web_service if you created another .env file.

4. Run the following command to run the app:
```
> docker-compose up --build
```
It will build all necessary images and run containers. Because the -d argument for `docker-compose up --build` command was not set, all of the data from stdout of containers will be outputed into your stdout.

5. Wait until web_1 service will output message "MySQL started" ([screenshot of how it'll look in terminal](https://user-images.githubusercontent.com/56651670/151373662-5f6192e9-fdbd-44b0-b67f-2b74a4a208e0.png))

6. Open another terminal, move into the repository directory, clean the databse and then run a migration for creating database schemas:
```
> cd online-shop/
> docker-compose exec web python manage.py flush --no-input
> docker-compose exec web python manage.py migrate
```
This step is going to look like [this](https://user-images.githubusercontent.com/56651670/151375786-26246728-17a2-47b9-85b1-45bf445bfbd2.png) in your terminal.

7. Create superuser to interact with the Django admin page:
```
> docker-compose exec web python manage.py createsuperuser
```

8. Check if the building went well by visiting admin page via your browser: http://localhost:8000

Now you can access the online shop API, for example, using curl.