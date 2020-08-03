from ..commands import Commands
from .. import Constants
from .user_command import UserCommand
from .. import DeleteUserParser
import tableauserverclient as TSC
from .. import get_logger
#logger = get_logger('pythontabcmd2.delete_user_command')


class DeleteUserCommand(UserCommand):
    def __init__(self, csv_lines, args):
        super().__init__(csv_lines)
        self.logging_level = args.logging_level

    def log(self):
        logger = get_logger('pythontabcmd2.delete_user_command', self.logging_level)
        return logger

    @classmethod
    def parse(cls):
        csv_lines, args = DeleteUserParser.delete_user_parser()
        return cls(csv_lines)

    def run_command(self):
        signed_in_object, server_object = Commands.deserialize()
        self.delete_users(server_object, self.csv_lines)

    def delete_users(self, server_object, csv_lines):
        self.delete_user_command(server_object, csv_lines)

    def delete_user_command(self, server, csv_lines):
        """Method to delete users using Tableauserverclient methods"""
        logger = self.log()
        command = Commands()
        user_obj_list = command.get_user(csv_lines)
        for user_obj in user_obj_list:
            username = user_obj.username
            user_id = UserCommand.find_user_id(server, username)
            try:
                server.users.remove(user_id)
                logger.info("Successfully removed")
            except TSC.ServerResponseError as e:
                logger.error("Error: Server error occurred", e)
                # TODO Map Error code
            except ValueError:
                logger.error("Error user for ", username, "not found")
