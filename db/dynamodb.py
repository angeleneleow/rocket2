"""DynamoDB."""
import boto3
from boto3.dynamodb.conditions import Attr
from model.user import User
from model.team import Team


class DynamoDB:
    """DynamoDB."""

    def __init__(self):
        """Initialize facade using DynamoDB settings (for now)."""
        # TODO change this to production and not localhost
        self.ddb = boto3.resource("dynamodb", region_name="",
                                  endpoint_url="http://localhost:8000")

        if not self.check_valid_table('users'):
            self.create_user_tables()

        if not self.check_valid_table('teams'):
            self.create_team_tables()

    def __str__(self):
        """Return a string representing this class."""
        return "DynamoDB"

    def create_user_tables(self):
        """Create the user table, for testing."""
        self.ddb.create_table(
            TableName='users',
            AttributeDefinitions=[
                {
                    'AttributeName': 'slack_id',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'slack_id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 50,
                'WriteCapacityUnits': 50
            }
        )

    def create_team_tables(self):
        """Create the team table, for testing."""
        self.ddb.create_table(
            TableName='teams',
            AttributeDefinitions=[
                {
                    'AttributeName': 'github_team_name',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'github_team_name',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 50,
                'WriteCapacityUnits': 50
            }
        )

    def check_valid_table(self, table_name):
        """
        Check if table with table_name exists.

        :param table_name: table identifier
        :return: boolean value, true if table exists, false otherwise
        """
        existing_tables = self.ddb.tables.all()
        return any(map(lambda t: t.name == table_name, existing_tables))

    def store_user(self, user):
        """
        Store user into users table.

        :param user: A user model to store
        """
        # Assume that the tables are already set up this way
        user_table = self.ddb.Table('users')
        user_table.put_item(
            Item={
                'slack_id': user.get_slack_id(),
                'email': user.get_email(),
                'github': user.get_github_username(),
                'major': user.get_major(),
                'position': user.get_position(),
                'bio': user.get_biography(),
                'image_url': user.get_image_url(),
                'permission_level': user.get_permissions_level().name
            }
        )

    def store_team(self, team):
        """
        //TODO: Store team into teams table.

        :param team: A team model to store
        """
        pass

    def retrieve_user(self, slack_id):
        """
        Retrieve user from users table.

        :return: returns a user model if slack id is found.
        """
        user = User(slack_id)
        user_table = self.ddb.Table('users')
        response = user_table.get_item(
            TableName='users',
            Key={
                'slack_id': slack_id
            }
        )
        response = response['Item']

        user.set_email(response['email'])
        user.set_github_username(response['github'])
        user.set_major(response['major'])
        user.set_position(response['position'])
        user.set_biography(response['bio'])
        user.set_image_url(response['image_url'])
        user.set_permissions_level(response['permission_level'])

        return user

    def retrieve_team(self, team_name):
        """
        //TODO: Retrieve team from teams table.

        :param team_name:
        :return:
        """
        return Team(team_name, '')

    def query_user(self, parameters):
        """
        Query for user using list of parameters.

        Returns list of users that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the user attribute, and the second is the value.

        Example: [('permission_level', 'admin')]

        :param parameters: list of parameters (tuples)
        :return: returns a list of user models that fit the query parameters.
        """
        user_list = []
        response = self.ddb.Table('users')
        for p in parameters:
            response = response.scan(
                FilterExpression=Attr(p[0]).eq(p[1])
            )
        response = response['Items']
        for r in response:
            slack_id = r['slack_id']
            user = User(slack_id)

            user.set_email(r['email'])
            user.set_github_username(r['github'])
            user.set_major(r['major'])
            user.set_position(r['position'])
            user.set_biography(r['bio'])
            user.set_image_url(r['image_url'])
            user.set_permissions_level(r['permission_level'])

            user_list.append(user)
        return user_list

    def query_team(self, parameters):
        """
        Query for teams using list of parameters.

        Returns list of teams that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the user attribute, and the second is the value.

        //TODO write team param example
        Example: [('permission_level', 'admin')]

        :param parameters:
        :return: returns a list of user models that fit the query parameters.
        """
        return []

    def delete_user(self, slack_id):
        """
        //TODO: Removes a user from the users table.

        :param slack_id: the slack_id of the user to be removed
        """
        user_table = self.ddb.Table('users')

        user_table.delete_item(
            Key={
                'slack_id': slack_id
            }
        )

    def delete_team(self, team_name):
        """
        //TODO: Removes a team from the teams table.

        :param team_name: the team_name of the team to be removed
        """
        pass
