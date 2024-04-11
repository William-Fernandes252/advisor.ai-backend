# advisor.ai Back-end

Back-end of the advisor.ai project, an article search and recommendation platform focused on promoting collaboration between researchers using AI.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Settings

See the settings specification at [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic commands

### Setting up users for testing

- To create **normal user accounts** for testing, use the command:

```bash
python manage.py createfakeusers
```

- To create a **superuser account**, use this command:

```bash
python manage.py createsuperuser
```

### Type checks

Running type checks with mypy:

```bash
mypy apps
```

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

```bash
coverage run -m pytest
coverage html
open htmlcov/index.html
```

### Running tests

```bash
pytest
```

### Training machine learning models

There are management commands to help testing models training and the generation of papers recommendations.

If you want to test the recommendation system locally,

1. create some fake users (between 50k and 100k should be enough) to hold the reviews with

    ```bash
    docker compose exec -it django python manage.py createfakeusers 50000
    ```

1. export the papers reviews data with

    ```bash
    docker compose exec -it django python manage.py exportdatasets
    ```

1. train a machine learning model with

    ```bash
    docker compose exec -it django python manage.py trainmodel
    ```

1. and finally, create suggestions using the trained model by running

    ```bash
    docker compose exec -it django python src/manage.py createpaperssuggestions --offset=25 --max=250
    ```

    Note that this process can take some time to complete and may fail in machines with slower CPUs and little memory. If that is your case, I recommend you to try to limit the number of users covered by the `batch_create_papers_suggestions` method [here](./apps/papers/tasks.py)

Now, you should be able see the suggestions for your user at the project home page.

## Email Server

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server [Mailpit](https://github.com/axllent/mailpit) with a web interface is available as docker container.

Container mailpit will start automatically when you will run all docker containers.
Please check [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html) for more details how to start all containers.

With Mailpit running, to view messages that are sent by your application, open your browser and go to `http://127.0.0.1:8025`

## Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

The following details how to deploy this application.

### Docker

In order to run the back-end services locally, execute the command

```bash
docker compose -f local.yml up
```

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
