"""Pack the modules contained in the db directory."""
import db.dynamodb
import db.facade
import dependency_injector.containers as containers
import dependency_injector.providers as providers
import config


class DBModule(containers.DeclarativeContainer):
    """DB dependency injections."""

    dynamodb = providers.Singleton(db.dynamodb.DynamoDB,
                                   config=config.ConfigModule.config.provider)
    facade = providers.Singleton(db.facade.DBFacade,
                                 ddb=dynamodb.provider)
