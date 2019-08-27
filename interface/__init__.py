"""Interface Init."""
from slack import WebClient
import interface.github as github
import interface.github_app as github_app
import interface.slack as slack
import dependency_injector.containers as containers
import dependency_injector.providers as providers


class InterfaceModule(containers.DeclarativeContainer):
    """All interfaces."""

    github = providers.Singleton(github.GithubInterface)
    github_app_auth = providers.Singleton(
        github_app.GithubAppInterface.GithubAppAuth)
    slack = providers.Singleton(slack.Bot)


class Clients(containers.DeclarativeContainer):
    """All third party libraries for the interface."""

    slack = providers.Singleton(WebClient)
