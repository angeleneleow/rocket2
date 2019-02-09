"""DynamoDB."""
import boto3
import logging
import toml
from functools import reduce
from boto3.dynamodb.conditions import Attr
from model.user import User
from model.team import Team
from model.project import Project
from model.permissions import Permissions


class DynamoDB:
    """
    Handles calls to database through API.

    Please do not use this class, and instead use :class:`db.facade.DBFacade`.
    This class only works on DynamoDB, and should not be used outside of the
    facade class.
    """

    def __init__(self, config):
        """Initialize facade using DynamoDB settings.

        To avoid local tests failure when the DynamoDb server is used,
        a testing environment variable is set.
        When testing environmental variable is true,
        the local dynamodb is run.
        When testing environmental variable is true,
        the server dynamodb is run.

        boto3.resource() takes in a service_name, region_name, and endpoint_url
        (only for local dynamodb).
        service_name: The name of a service, "dynamodb" in this case.
        region_name:  The name of the region associated with the client.
        A list of different regions can be obtained online.
        endpoint_url: The complete URL to use for the constructed client.

        Boto3 server require environmental variables for credentials:
        AWS_ACCESS_KEY_ID: The access key for your AWS account.
        AWS_SECRET_ACCESS_KEY: The secret key for the AWS account
        AWS_SESSION_TOKEN: The session key for your AWS account.
        This is only needed when you are using temporary credentials.
        """
        logging.info("Initializing DynamoDb")
        self.users_table = config['aws']['users_table']
        self.teams_table = config['aws']['teams_table']
        self.projects_table = config['aws']['projects_table']
        testing = config['testing']

        if testing:
            logging.info("Connecting to local DynamoDb")
            self.ddb = boto3.resource(service_name="dynamodb",
                                      region_name="",
                                      aws_access_key_id="",
                                      aws_secret_access_key="",
                                      endpoint_url="http://localhost:8000")
        else:
            logging.info("Connecting to remote DynamoDb")
            region_name = config['aws']['region']
            credentials = toml.load(config['aws']['creds_path'])
            access_key_id = credentials['access_key_id']
            secret_access_key = credentials['secret_access_key']
            self.ddb = boto3.resource(service_name='dynamodb',
                                      region_name=region_name,
                                      aws_access_key_id=access_key_id,
                                      aws_secret_access_key=secret_access_key)

        # Check for missing tables
        if not self.check_valid_table(self.users_table):
            self.__create_table(self.users_table, 'slack_id')
        if not self.check_valid_table(self.teams_table):
            self.__create_table(self.teams_table, 'github_team_id')
        if not self.check_valid_table(self.projects_table):
            self.__create_table(self.projects_table, 'project_id')

    def __str__(self):
        """Return a string representing this class."""
        return "DynamoDB"

    def __create_table(self, table_name, primary_key, key_type='S'):
        """
        Creates a table.

        **Note**: This function should **not** be called externally, and should
        only be called on initialization.

        :param table_name: name of the table to create
        :param primary_key: name of the primary key for the table
        :param key_type: type of primary key (S, 
        """
        logging.info("Creating table '{}'".format(table_name))
        self.ddb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': primary_key,
                    'AttributeType': key_type
                },
            ],
            KeySchema=[
                {
                    'AttributeName': primary_key,
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )

    def check_valid_table(self, table_name):
        """
        Check if table with ``table_name`` exists.

        :param table_name: table identifier
        :return: boolean value, true if table exists, false otherwise
        """
        existing_tables = self.ddb.tables.all()
        return any(map(lambda t: t.name == table_name, existing_tables))

    def store_user(self, user):
        """
        Store user into users table.

        :param user: A user model to store
        :returns: Returns true if the user was stored, and false otherwise
        """
        # Check that there are no blank fields in the user
        if User.is_valid(user):
            user_table = self.ddb.Table(self.users_table)
            udict = User.to_dict(user)

            logging.info("Storing user {} in table {}".
                         format(user.get_slack_id(), self.users_table))
            user_table.put_item(Item=udict)
            return True
        return False

    def store_team(self, team):
        """
        Store team into teams table.

        :param team: A team model to store
        :return: Returns true if stored succesfully; false otherwise
        """
        # Check that there are no blank fields in the team
        if Team.is_valid(team):
            teams_table = self.ddb.Table(self.teams_table)
            tdict = Team.to_dict(team)

            logging.info("Storing team {} in table {}".
                         format(team.get_github_team_name(), self.teams_table))
            teams_table.put_item(Item=tdict)
            return True
        return False

    def retrieve_user(self, slack_id):
        """
        Retrieve user from users table.

        :param slack_id: retrieve based on this slack id
        :raise: LookupError if slack id is not found.
        :return: returns a user model if slack id is found.
        """
        user_table = self.ddb.Table(self.users_table)
        response = user_table.get_item(
            TableName=self.users_table,
            Key={
                'slack_id': slack_id
            }
        )

        if 'Item' in response.keys():
            return User.from_dict(response['Item'])
        else:
            raise LookupError('User "{}" not found'.format(slack_id))

    def retrieve_team(self, team_id):
        """
        Retrieve team from teams table.

        :param team_name: used as key for retrieving team objects.
        :raise: LookupError if team id is not found.
        :return: the team object if team_name is found.
        """
        team_table = self.ddb.Table(self.teams_table)
        response = team_table.get_item(
            TableName=self.teams_table,
            Key={
                'github_team_id': team_id
            }
        )

        if 'Item' in response.keys():
            return Team.from_dict(response['Item'])
        else:
            raise LookupError('Team "{}" not found'.format(team_id))

    def query_user(self, parameters):
        """
        Query for specific users by parameter.

        Returns list of users that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the user attribute, and the second is the value.

        Example: ``[('permission_level', 'admin')]``

        If parameters is an empty list, returns all the users.

        :param parameters: list of parameters (tuples)
        :return: returns a list of user models that fit the query parameters.
        """
        users = self.ddb.Table(self.users_table)
        if len(parameters) > 0:
            # There are 1 or more parameters that we should care about
            filter_expr = reduce(lambda a,x: a & x,
                                 map(lambda x: Attr(x[0]).eq(x[1]),
                                     parameters))

            response = users.scan(
                FilterExpression=filter_expr
            )
        else:
            # No parameters; return all users in table
            response = users.scan()

        return list(map(User.from_dict, response['Items']))

    def query_team(self, parameters):
        """
        Query for teams using list of parameters.

        Returns list of teams that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the user attribute, and the second is the value.

        Example: ``[('platform', 'slack')]``

        Special attribute: member
        The member attribute describes a set, so this function would check to
        see if an entry **contains** a certain member slack_id. You can specify
        multiple slack_id, but they must be in different parameters (one
        slack_id per tuple).

        :param parameters:
        :return: returns a list of team models that fit the query parameters.
        """
        teams = self.ddb.Table(self.teams_table)
        if len(parameters) > 0:
            # There are 1 or more parameters that we should care about
            def f(x):
                if x[0] == 'members':
                    return Attr(x[0]).contains(x[1])
                else:
                    return Attr(x[0]).eq(x[1])

            filter_expr = reduce(lambda a,x: a & x, map(f, parameters))
            response = teams.scan(
                FilterExpression=filter_expr
            )
        else:
            # No parameters; return all users in table
            response = teams.scan()

        return list(map(Team.from_dict, response['Items']))

    def delete_user(self, slack_id):
        """
        Remove a user from the users table.

        :param slack_id: the slack_id of the user to be removed
        """
        logging.info("Deleting user {} from table {}".
                     format(slack_id, self.users_table))
        user_table = self.ddb.Table(self.users_table)
        user_table.delete_item(
            Key={
                'slack_id': slack_id
            }
        )

    def delete_team(self, team_id):
        """
        Remove a team from the teams table.

        To obtain the team github id, you have to retrieve the team first.

        :param team_id: the team_id of the team to be removed
        """
        logging.info("Deleting team {} from table {}".
                     format(team_id, self.teams_table))
        team_table = self.ddb.Table(self.teams_table)
        team_table.delete_item(
            Key={
                'github_team_id': team_id
            }
        )

    def store_project(self, project):
        """
        Store project into projects table.

        :param project: A project model to store
        :return: True if project is valid, False otherwise
        """
        # Check that there are no required blank fields in the project
        if Project.is_valid(project):
            project_table = self.ddb.Table(self.projects_table)
            udict = Project.to_dict(project)

            logging.info("Storing project {} in table {}".
                         format(project.get_project_id(), self.projects_table))
            project_table.put_item(Item=udict)
            return True
        return False

    def retrieve_project(self, project_id):
        """
        Retrieve project from projects table.

        :param project_id: used as key for retrieving project objects.
        :raise: LookupError if project id is not found.
        :return: returns a project model if slack id is found.
        """
        project_table = self.ddb.Table(self.projects_table)
        response = project_table.get_item(
            TableName=self.projects_table,
            Key={
                'project_id': project_id
            }
        )

        if 'Item' in response.keys():
            return Project.from_dict(response['Item'])
        else:
            raise LookupError('Project "{}" not found'.format(project_id))

    def query_project(self, parameters):
        """
        Query for specific projects by parameter.

        Returns list of teams that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the project attribute, and the second is the value.

        Example: ``[('tags', 'c++')]`` would get all projects with ``c++``
        (case sensitive) in their tags.

        :param parameters: list of parameters (tuples)
        :return: returns a list of project models that fit the query parameters
        """
        projects = self.ddb.Table(self.projects_table)
        if len(parameters) > 0:
            # There are 1 or more parameters that we should care about
            def f(x):
                if x[0] in ['tags', 'github_urls']:
                    return Attr(x[0]).contains(x[1])
                else:
                    return Attr(x[0]).eq(x[1])

            filter_expr = reduce(lambda a,x: a & x, map(f, parameters))
            response = projects.scan(
                FilterExpression=filter_expr
            )
        else:
            # No parameters; return all users in table
            response = projects.scan()

        return list(map(Project.from_dict, response['Items']))

    def delete_project(self, project_id):
        """
        Remove a project from the projects table.

        :param project_id: the project ID of the project to be removed
        """
        logging.info("Deleting project {} from table {}".
                     format(project_id, self.projects_table))
        project_table = self.ddb.Table(self.projects_table)
        project_table.delete_item(
            Key={
                'project_id': project_id
            }
        )
