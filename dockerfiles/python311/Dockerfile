FROM python:3.11-slim-bullseye

# Set environment variables.
ENV PYTHONWRITEBYTECODE=1 \
    PYTHONBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.6.1

# System deps:
RUN pip install "poetry==$POETRY_VERSION"


# Set working directory.
WORKDIR /code

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$ENV_NAME" == production && echo "--no-dev") --no-interaction --no-ansi


# Copy project.
COPY . /code/

EXPOSE 5000

ENTRYPOINT ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", \
        "uvicorn.workers.UvicornWorker",  "-b", "0.0.0.0:5000" ]
