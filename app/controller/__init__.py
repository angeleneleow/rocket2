"""Pack the modules contained in the controller directory."""
from typing import Union, Tuple
from flask import Response
from app.controller.webhook.github import GitHubWebhookHandler
from app.controller.webhook.slack import SlackEventsHandler
from interface import InterfaceModule
from db import DBModule
from config import ConfigModule
import dependency_injector.containers as containers
import dependency_injector.providers as providers

ResponseTuple = Tuple[Union[str, Response], int]


class WebhookModule(containers.DeclarativeContainer):
    """Webhook dependency injections."""

    github = providers.Singleton(GitHubWebhookHandler,
                                 db_facade=DBModule.facade.provider,
                                 config=ConfigModule.config.provider)
    slack = providers.Singleton(SlackEventsHandler,
                                db_facade=DBModule.facade.provider,
                                bot=InterfaceModule.slack.provider)
