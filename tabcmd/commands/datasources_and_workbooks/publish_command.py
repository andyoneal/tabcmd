import tableauserverclient as TSC

from tabcmd.execution.global_options import *
from tabcmd.commands.auth.session import Session
from tabcmd.commands.server import Server
from tabcmd.execution.logger_config import log
from .datasources_and_workbooks_command import DatasourcesAndWorkbooks


class PublishCommand(DatasourcesAndWorkbooks):
    """
    This command publishes the specified workbook (.twb(x)), data source
    (.tds(x)), or extract (.hyper) to Tableau Server.
    """

    name: str = "publish"
    description: str = "Publish a workbook, data source, or extract to the server"

    @staticmethod
    def define_args(publish_parser):
        publish_parser.add_argument(
            "filename",
            metavar="filename.twbx|tdsx|hyper",
            # this is not actually a File type because we just pass the path to tsc
            help="Existing local file to publish.",
        )
        set_publish_args(publish_parser)
        set_project_r_arg(publish_parser)
        set_parent_project_arg(publish_parser)

    @staticmethod
    def run_command(args):
        logger = log(__name__, args.logging_level)
        logger.debug("======================= Launching command =======================")
        logger.debug(args)
        session = Session()
        server = session.create_session(args)

        logger.debug("Project details given: {0}, {1}".format(args.parent_project_path, args.project_name))

        if args.project_name:
            try:
                project_id = Server.get_project_by_name_and_parent_path(
                    logger, server, args.project_name, args.parent_project_path
                )
            except Exception as exc:
                Server.exit_with_error(logger, "Error getting project from server", exc)
        else:
            project_id = ""
            args.project_name = "default"
            args.parent_project_path = ""

        publish_mode = PublishCommand.get_publish_mode(args)

        source = PublishCommand.get_filename_extension_if_tableau_type(logger, args.filename)
        logger.info("===== Publishing '{}' to the server. This could take several minutes...".format(args.filename))
        if source in ["twbx", "twb"]:
            new_workbook = TSC.WorkbookItem(project_id, name=args.name, show_tabs=args.tabbed)
            new_workbook = server.workbooks.publish(new_workbook, args.filename, publish_mode)
            PublishCommand.print_success(logger, new_workbook)

        elif source in ["tds", "tdsx", "hyper"]:
            new_datasource = TSC.DatasourceItem(project_id, name=args.name)
            new_datasource = server.datasources.publish(new_datasource, args.filename, publish_mode)
            PublishCommand.print_success(logger, new_datasource)

    @staticmethod
    def print_success(logger, item):
        logger.info(
            "===== File successfully published to the server at the following location:\n===== {}".format(
                item.webpage_url
            )
        )

    @staticmethod
    def get_publish_mode(args):
        if args.overwrite:
            publish_mode = TSC.Server.PublishMode.Overwrite
        else:
            publish_mode = TSC.Server.PublishMode.CreateNew
        return publish_mode
