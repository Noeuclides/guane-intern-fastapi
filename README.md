# Dogs

A RESTful API developed in python's web framework FastAPI.

## Requirements
In order to run the application you have to run the container, so it is important to have docker install in your machine
```sh
$ sudo apt-get install docker.io
$ sudo apt-get install docker-compose
```

## Run the App

Simply run the following command
```sh
$ sudo docker-compose up
```
You will see something like this the first time you run that command, while docker build the container from the Dockerfile (This process might take a while).
```sh
Creating network "guane-intern-fastapi_default" with the default driver
pulling db (postgres:11)...
11: Pulling from library/postgres
e50c3c9ef5a2: Pull complete
....
Creating guane-intern-fastapi_db_1 ... done
Creating guane-intern-fastapi_web_1 ... done
Creaging pgadmin                    ... done
Attaching to guane-intern-fastapi_db_1, guane-intern-fastapi_web_1, pgadmin
...
web_1     | INFO:     Started server process [10]
web_1     | INFO:     Waiting for application startup.
web_1     | INFO:     Application startup complete.
```

Then, go to your browser and write "http://127.0.0.1:8000/docs", to view the endpoints available, and create, edit, get, and delete entities. Or go to "http://127.0.0.1:8000/redoc" to see the documentation.

