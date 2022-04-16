import tableauserverclient as TSC

from tabcmd.commands.auth.session import Session
from tabcmd.execution.logger_config import log
from .datasources_and_workbooks_command import DatasourcesAndWorkbooks
from tabcmd.execution.global_options import *
from tabcmd.commands.constants import Errors

class GetUrl(DatasourcesAndWorkbooks):
    """
    This command gets the resource from Tableau Server that's represented
    by the specified (partial) URL. The result is returned as a file.
    """

    name: str = "get"
    description: str = "Get a file from the server"

    @staticmethod
    def define_args(get_url_parser):
        get_url_parser.add_argument("url", help="url that identifies the view or workbook to export")
        set_filename_arg(get_url_parser)
        # these don't need arguments, although that would be a good future addition
        # tabcmd get "/views/Finance/InvestmentGrowth.png?:size=640,480" -f growth.png
        # tabcmd get "/views/Finance/InvestmentGrowth.png?:refresh=yes" -f growth.png

    @staticmethod
    def run_command(args):
        # A view can be returned in PDF, PNG, or CSV (summary data only) format.
        # A Tableau workbook is returned as a TWB if it connects to a datasource/live connection,
        # or a TWBX if it uses an extract.
        logger = log(__name__, args.logging_level)
        logger.debug("======================= Launching command =======================")
        session = Session()
        server = session.create_session(args)
        file_type = GetUrl.get_file_type_from_filename(logger, args.filename, args.url)
        content_type = GetUrl.evaluate_content_type(logger, args.url)
        if content_type == "workbook":
            if file_type == "twbx" or file_type == "twb":
                GetUrl.generate_twb(logger, server, args)
            else:
                Errors.exit_with_error(logger, message="A workbook can only be exported as twb or twbx")
        else:  # content type = view
            if file_type == "pdf":
                GetUrl.generate_pdf(logger, server, args)
            elif file_type == "png":
                GetUrl.generate_png(logger, server, args)
            elif file_type == "csv":
                GetUrl.generate_csv(logger, server, args)
            else:
                Errors.exit_with_error(logger, message="No valid file extension found in url or filename")


    @staticmethod
    def evaluate_content_type(logger, url):
        # specify a view to get using "/views/<workbookname>/<viewname>.<extension>"
        # specify a workbook to get using "/workbooks/<workbookname>.<extension>".
        if url.find("/views/") == 0:
            return "view"
        elif url.find("/workbooks/") == 0:
            return "workbook"
        else:
            Errors.exit_with_error(logger, message="Content requested must be a view or workbook")


    @staticmethod
    def get_file_type_from_filename(logger, file_name, url):
        type_of_file = None
        if file_name is not None:
            logger.debug("Get file type from filename: {}".format(file_name))
            type_of_file = GetUrl.get_file_extension(file_name)
        elif url.index(".") > 0:  # file_name is None, grab from url
            logger.debug("Get file type from url: {}".format(url))
            type_of_file = GetUrl.get_file_extension(url)
        if not type_of_file:
            Errors.exit_with_error(logger, "The url must include a file extension")

        if type_of_file in ["pdf", "csv", "png", "twb", "twbx"]:
            return type_of_file

        Errors.exit_with_error(logger, "The file type {} is invalid".format(type_of_file))

    @staticmethod
    def get_file_extension(filename):
        parts = filename.split(".")
        if len(parts) < 2:
            return None
        extension = parts[1]
        extension = GetUrl.strip_query_params(extension)
        return extension

    @staticmethod
    def strip_query_params(filename):
        if filename.find("?") > 0:
            filename = filename.split("?")[0]
        return filename

    @staticmethod
    def strip_extension(filename):
        if filename.find(".") > 0:
            filename = filename.split(".")[0]
        return filename

    @staticmethod
    def get_workbook_name(logger, url):  # /workbooks/wb-name" -> "wb-name"
        name_parts = url.split("/")
        workbook_name = name_parts[::-1][0]  # last part
        workbook_name = GetUrl.strip_query_params(workbook_name)
        workbook_name = GetUrl.strip_extension(workbook_name)
        return workbook_name

    @staticmethod
    def get_view_url(url):  # "/views/wb-name/view-name" -> wb-name/sheets/view-name
        name_parts = url.split("/")  # ['', 'views', 'wb-name', 'view-name']
        if len(name_parts) != 4:
            raise ValueError(
                "The url given did not match the expected format: 'views/workbook-name/view-name'")
        view_name = name_parts[::-1][0]
        view_name = GetUrl.strip_query_params(view_name)
        view_name = GetUrl.strip_extension(view_name)

        workbook_name = name_parts[2]
        return "{}/sheets/{}".format(workbook_name, view_name)

    @staticmethod
    def generate_pdf(logger, server, args):
        view = GetUrl.get_view_url(args.url)
        try:
            views_from_list = GetUrl.get_view_by_content_url(logger, server, view)
            req_option_pdf = TSC.PDFRequestOptions(maxage=1)
            server.views.populate_pdf(views_from_list, req_option_pdf)
            if args.filename is None:
                file_name_with_path = "{}.pdf".format(views_from_list.name)
            else:
                file_name_with_path = args.filename
            formatted_file_name = file_name_with_path
            with open(formatted_file_name, "wb") as f:
                f.write(views_from_list.pdf)
                logger.info("Exported successfully")
        except TSC.ServerResponseError as e:
            Errors.exit_with_error(logger, "Server error:", e)

    @staticmethod
    def generate_png(logger, server, args):
        view = GetUrl.get_view_url(args.url)
        try:
            views_from_list = GetUrl.get_view_by_content_url(logger, server, view)
            req_option_csv = TSC.CSVRequestOptions(maxage=1)
            server.views.populate_csv(views_from_list, req_option_csv)
            if args.filename is None:
                file_name_with_path = "{}.png".format(view)
            else:
                file_name_with_path = args.filename
            formatted_file_name = file_name_with_path
            with open(formatted_file_name, "wb") as f:
                f.write(views_from_list.png)
                logger.info("Exported successfully")
        except TSC.ServerResponseError as e:
            Errors.exit_with_error(logger, "Server error:", e)

    @staticmethod
    def generate_csv(logger, server, args):
        view = GetUrl.get_view_url(args.url)
        try:
            views_from_list = GetUrl.get_view_by_content_url(logger, server, view)
            req_option_csv = TSC.CSVRequestOptions(maxage=1)
            server.views.populate_csv(views_from_list, req_option_csv)
            if args.filename is None:
                file_name_with_path = "{}.csv".format(view)
            else:
                file_name_with_path = args.filename
            formatted_file_name = file_name_with_path
            with open(formatted_file_name, "wb") as f:
                f.write(views_from_list.csv)
                logger.info("Exported successfully")
        except TSC.ServerResponseError as e:
            Errors.exit_with_error(logger, "Server error:", e)

    @staticmethod
    def generate_twb(logger, server, args):
        workbook = GetUrl.get_workbook_name(logger, args.url)
        try:
            target_workbook = GetUrl.get_view_by_content_url(logger, server, workbook)
            server.workbooks.download(target_workbook.id, filepath=None, no_extract=False)
            logger.info("Workbook {} exported".format(target_workbook.name))
        except TSC.ServerResponseError as e:
            Errors.exit_with_error(logger, "Server error:", e)
