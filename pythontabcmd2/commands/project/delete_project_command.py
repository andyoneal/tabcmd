from ..commands import Commands
from .project_command import *
from .. import DeleteProjectParser
import tableauserverclient as TSC
from .. import get_logger


class DeleteProjectCommand(ProjectCommand):
    def __init__(self, args, evaluated_project_path):
        super().__init__(args, evaluated_project_path)

    def log(self):
        logger = get_logger('pythontabcmd2.create_project_command',
                            self.logging_level)
        return logger

    @classmethod
    def parse(cls):
        args, evaluated_project_path = \
            DeleteProjectParser.delete_project_parser()
        return cls(args, evaluated_project_path)

    def run_command(self):
        server_object = Commands.deserialize()
        self.delete_project(server_object)

    def delete_project(self, server):
        """Method to delete project using Tableauserverclient methods"""
        logger = self.log()
        try:
            project_id = ProjectCommand.find_project_id(server, self.name)
            server.projects.delete(project_id)
            logger.info("Successfully deleted project")
        except TSC.ServerResponseError as e:
            logger.error("Server error occurred", e)
        except ValueError as e:
            logger.error("Project does not exist")
