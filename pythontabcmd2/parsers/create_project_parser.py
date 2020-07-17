import argparse
import sys
try:
    from .global_options import *
except ModuleNotFoundError:
    from parsers.global_options import *


class CreateProjectParser:
    def create_project_parser(self):
        """Method to parse create project arguments passed by the user"""
        parser = argparse.ArgumentParser(description='create project command')
        parser.add_argument('--name','-n', required=True, help='name of project')
        parser.add_argument('--parent-project-path','-p', default=None, help='path of parent project')
        parser.add_argument('--description','-d', default=None, help='description of project')
        parser.add_argument('--content-permission','-c', default=None, help='content permission of project')
        args = parser.parse_args(sys.argv[2:])
        if args.parent_project_path is not None:
            evaluated_project_path = GlobalOptions.evaluate_project_path(args.parent_project_path)
        else:
            evaluated_project_path = args.parent_project_path
        return args.name, args.description, args.content_permission, evaluated_project_path

