"""Command parsing for user events."""
import argparse
import shlex
from db.facade import DBFacade
from db.dynamodb import DynamoDB
from model.permissions import Permissions


class UserCommand:
    """Represent User Command Parser."""

    command_name = "user"
    help = "User Command Reference:\n\n @rocket user" \
           "\n\n Options:\n\n" \
           " edit \n --name NAME\n" \
           " --email ADDRESS\n --pos YOURPOSITION\n" \
           " --major YOURMAJOR\n --bio YOURBIO\n" \
           " 'edit properties of your Launch Pad profile\n" \
           " surround arguments with spaces with single quotes'" \
           "\n ADMIN/TEAM LEAD ONLY option: --member MEMBER_ID\n" \
           " 'edit properties of another " \
           "user's Launch Pad profile'\n\n" \
           " view MEMBER_ID\n 'view information about a user'" \
           "\n\n " \
           "help\n 'outputs options for user commands'\n\n " \
           "ADMIN ONLY\n\n delete MEMBER_ID\n" \
           " 'permanently delete member's Launch Pad profile'"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"

    def __init__(self, DBfacade, bot):
        """Initialize user command."""
        self.parser = argparse.ArgumentParser(prog="user")
        self.parser.add_argument("user")
        self.init_subparsers()
        self.facade = DBfacade
        self.bot = bot

    def init_subparsers(self):
        """Initialize subparsers for user command."""
        subparsers = self.parser.add_subparsers(dest="which")

        """Parser for view command."""
        parser_view = subparsers.add_parser("view")
        parser_view.set_defaults(which="view")
        parser_view.add_argument("--slack_id", type=str, action='store')

        """Parser for help command."""
        parser_help = subparsers.add_parser("help")
        parser_help.set_defaults(which="help")

        """Parser for delete command."""
        parser_delete = subparsers.add_parser("delete")
        parser_delete.set_defaults(which="delete")
        parser_delete.add_argument("slack_id", type=str, action='store')

        """Parser for edit command."""
        parser_edit = subparsers.add_parser("edit")
        parser_edit.set_defaults(which='edit')
        parser_edit.add_argument("--name", type=str, action='store')
        parser_edit.add_argument("--email", type=str, action='store')
        parser_edit.add_argument("--pos", type=str, action='store')
        parser_edit.add_argument("--github", type=str, action='store')
        parser_edit.add_argument("--major", type=str, action='store')
        parser_edit.add_argument("--bio", type=str, action='store')
        parser_edit.add_argument("--member", type=str, action='store')

    def get_name(self):
        """Return the command type."""
        return self.command_name

    def get_help(self):
        """Return command options for user events."""
        return self.help

    def handle(self, command, user_id, channel):
        """Handle command by splitting into substrings and giving to parser."""
        command_arg = shlex.split(command)
        args = None

        try:
            # Going for the nuclear option
            args = self.parser.parse_args(command_arg)
        except SystemExit:
            return self.help

        if args.which is None:
            return self.help

        elif args.which == "view":
            # stub
            if args.slack_id is not None:
                return args.slack_id
            else:
                return user_id

        elif args.which == "help":
            # stub
            return self.help

        elif args.which == "delete":
            # stub
            # return "deleting " + args.slack_id
            return self.delete_helper(user_id, args.slack_id, channel)

        elif args.which == "edit":
            # stub
            msg = "user edited: "
            if args.member is not None:
                msg += "member: {}, ".format(args.member)
            if args.name is not None:
                msg += "name: {}, ".format(args.name)
            if args.email is not None:
                msg += "email: {}, ".format(args.email)
            if args.pos is not None:
                msg += "position: {}, ".format(args.pos)
            if args.github is not None:
                msg += "github: {}, ".format(args.github)
            if args.major is not None:
                msg += "major: {}, ".format(args.major)
            if args.bio is not None:
                msg += "bio: {}".format(args.bio)
            return msg

    def delete_helper(self, user_id, slack_id, channel):
        """
        Delete user from database.

        Delete user with slack_id from database if user with user_id has
        admin permission level.

        :param user_id: Slack ID of user who is calling the command
        :param slack_id: Slack ID of user who is being deleted
        :param channel: ID of Slack channel that called command
        :return: returns permission error message if not admin,
                 returns deletion message if user is deleted.
        """
        message = "Deleted user with Slack ID: " + slack_id
        lookup_error = "User not found!"
        try:
            user_command = self.facade.retrieve_user(user_id)
            if user_command.get_permissions_level() == Permissions.admin:
                self.facade.delete_user(slack_id)
                self.bot.send_to_channel(message, channel)
            else:
                self.bot.send_to_channel(self.permission_error, channel)
        except LookupError:
                self.bot.send_to_channel(lookup_error, channel)
