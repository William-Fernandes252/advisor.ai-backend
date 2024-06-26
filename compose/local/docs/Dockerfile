# define an alias for the specific python version used in this file.
FROM python:3.12.2-slim-bookworm as python

# Python build stage
FROM python as python-build-stage

ARG buildEnv=local
ARG appHome=/project

# Install apt packages
RUN apt update && apt install --no-install-recommends -y \
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
RUN mkdir __pypackages__ && pdm sync --no-editable --prod

# Python 'run' stage
FROM python as python-run-stage

ARG buildEnv=local
ARG appHome=/project

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${buildEnv}

# Devcontainer dependencies and utils
RUN apt update && apt install --no-install-recommends -y \
  sudo git bash-completion nano ssh

# Create devcontainer user and add it to sudoers
RUN groupadd --gid 1000 dev-user \
  && useradd --uid 1000 --gid dev-user --shell /bin/bash --create-home dev-user \
  && echo dev-user ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/dev-user \
  && chmod 0440 /etc/sudoers.d/dev-user

# Install required system dependencies
RUN apt update && apt install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev \
  # Build dependencies
  build-essential \
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

COPY ./compose/local/docs/start /start-docs
RUN sed -i 's/\r$//g' /start-docs
RUN chmod +x /start-docs

WORKDIR /docs
