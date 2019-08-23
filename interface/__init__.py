"""Interface Init."""
from slack import WebClient
import interface.github as github
import interface.github_app as github_app
import interface.slack as slack
import dependency_injector.containers as containers
import dependency_injector.providers as providers


class Interfaces(containers.DeclarativeContainer):
    """All interfaces."""

    github = providers.Factory(github.GithubInterface)
    github_app_auth = providers.Factory(
        github_app.GithubAppInterface.GithubAppAuth)
    slack = providers.Factory(slack.Bot)


class Clients(containers.DeclarativeContainer):
    """All third party libraries for the interface."""

    slack = providers.Factory(WebClient)
