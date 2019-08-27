"""Pack the modules contained in the command directory."""
import app.controller.command.parser as psr
import dependency_injector.containers as containers
import dependency_injector.providers as providers
from db import DBModule
from interface import InterfaceModule

CommandParser = psr.CommandParser


class ParserModule(containers.DeclarativeContainer):
    """Parser dependency injection."""

    parser = providers.Singleton(
        psr.CommandParser,
        db_facade=DBModule.facade.provider,
        bot=InterfaceModule.slack.provider,
        github_interface=InterfaceModule.github.provider)
