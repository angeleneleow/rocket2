"""Pack the modules contained in the commands directory."""
from typing import Union
from app.controller.command.commands.team import TeamCommand
from app.controller.command.commands.user import UserCommand
from app.controller.command.commands.token import TokenCommand, TokenCommandConfig
from datetime import timedelta
import dependency_injector.containers as containers
import dependency_injector.providers as providers
from db import DBModule
from interface import InterfaceModule

UnionCommands = Union[TeamCommand, UserCommand, TokenCommand]


class TokenModule(containers.DeclarativeContainer):
    """Token dependency injection."""

    config = providers.Singleton(TokenCommandConfig,
                                 expiry=timedelta(days=7),
                                 signing_key="")


class CommandsModule(containers.DeclarativeContainer):
    """Commands dependency injection."""

    user = providers.Singleton(UserCommand,
                               db_facade=DBModule.facade.provider,
                               gh=InterfaceModule.github.provider)
    team = providers.Singleton(TeamCommand,
                               db_facade=DBModule.facade.provider,
                               gh=InterfaceModule.github.provider)
    token = providers.Singleton(TokenCommand,
                                db_facade=DBModule.facade.provider,
                                config=TokenModule.config.provider)
