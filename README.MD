Getting Started
---------------

### Setting up the Backend

To set up the Django backend, navigate to the `backend` directory and run the following commands:

```bash
docker-compose run web python manage.py migrate
docker-compose run web python manage.py createsuperuser
docker-compose up -d
```

These commands will start the Docker containers, run the necessary database migrations, and create a superuser for the Django admin interface.

### Accessing the Application

You can access the application by navigating to [http://localhost:8080](http://localhost:8080) in your web browser. You should see a default Vue.js application running.

To access the Django admin interface, navigate to [http://localhost:8000/admin](http://localhost:8000/admin) and log in using the superuser credentials you created earlier.