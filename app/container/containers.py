"""Containers module."""

import logging.config

import boto3
import sentry_sdk
from botocore.client import BaseClient
from dependency_injector import containers, providers
from dependency_injector.providers import Resource
from app.infrastructure.aws.s3 import S3Service
from app.infrastructure.db.database import Database
from app.infrastructure.meta.instagram_platform.graph_api import InstagramGraphApiClient


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.routes.api_v1.endpoints.image",
            "app.routes.api_v1.endpoints.auth",
            "app.routes.api_v1.endpoints.instagram",
        ]
    )

    config = providers.Configuration(yaml_files=["config.yml"])

    env_name = providers.Resource(config.core.app.env)

    logging = providers.Resource(
        logging.config.fileConfig,
        fname=config.core.app.logger.config_file[env_name],
    )

    sentry_sdk = providers.Resource(  # type: ignore [var-annotated]
        sentry_sdk.init,
        dsn=config.infrastructures.sentry.dsn[env_name],
        # TODO: traces_sample_rate may have to update when the app up and running on prod
        traces_sample_rate=1.0,
        environment=env_name,
    )

    db = providers.Singleton(Database, db_url=config.infrastructures.db.url)

    sts_client: Resource[BaseClient] = providers.Resource(
        boto3.client,
        "sts",
        aws_access_key_id=config.infrastructures.aws.aws_access_key_id,
        aws_secret_access_key=config.infrastructures.aws.aws_secret_access_key,
    )

    temp_credentials = providers.Resource(sts_client.provided.get_session_token.call())

    session: Resource[boto3.session.Session] = providers.Resource(
        boto3.session.Session,
        aws_access_key_id=temp_credentials.provided["Credentials"]["AccessKeyId"],
        aws_secret_access_key=temp_credentials.provided["Credentials"][
            "SecretAccessKey"
        ],
        aws_session_token=temp_credentials.provided["Credentials"]["SessionToken"],
    )

    s3_client = providers.Resource(
        session.provided.client.call(),
        service_name="s3",
    )

    instagram_graph_api_client = providers.Singleton(
        InstagramGraphApiClient,
        environment=env_name,
    )

    s3_service = providers.Factory(
        S3Service,
        s3_client=s3_client,
    )

    s3_image_bucket = providers.Resource(
        config.infrastructures.aws.s3_image_bucket[env_name]
    )