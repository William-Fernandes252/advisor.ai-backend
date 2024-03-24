# define an alias for the specific python version used in this file.
FROM python:3.12.2-slim-bookworm as python

# Python build stage
FROM python as python-build-stage

ARG buildEnd=production
ARG appHome=/project

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev

# Install PDM
RUN pip install -U pip setuptools wheel Cython
RUN pip install pdm

# Copy files
COPY pyproject.toml pdm.lock README.md /project/

# Install dependencies and project into the local packages directory
WORKDIR ${appHome}
RUN mkdir __pypackages__ && pdm sync --prod --no-editable --no-isolation

# Python 'run' stage
FROM python as python-run-stage

ARG buildEnv=production
ARG appHome=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${buildEnv}

WORKDIR ${appHome}

RUN addgroup --system django \
  && adduser --system --ingroup django django

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Retrieve packages from build stage
ENV PYTHONPATH=${appHome}/pkgs
COPY --from=python-build-stage ${appHome}/__pypackages__/3.12/lib ${appHome}/pkgs

# Retrieve executables
COPY --from=python-build-stage ${appHome}/__pypackages__/3.12/bin/* /bin/

COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
COPY --chown=django:django ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker


COPY --chown=django:django ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

# Copy application code to WORKDIR
COPY --chown=django:django . ${appHome}

# Make django owner of the WORKDIR directory as well.
RUN chown django:django ${appHome}

USER django

RUN DATABASE_URL="" \
  CELERY_BROKER_URL="" \
  DJANGO_SETTINGS_MODULE="config.settings.test" \
  python manage.py compilemessages

ENTRYPOINT ["/entrypoint"]
