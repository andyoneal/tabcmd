import argparse
import sys
from .global_options import *
from .parent_parser import ParentParser


class DeleteSiteParser:
    @staticmethod
    def delete_site_parser():
        """Method to parse delete site arguments passed by the user"""
        parent_parser = ParentParser()
        parser = parent_parser.parent_parser_with_global_options()
        subparsers = parser.add_subparsers()
        delete_site_parser = subparsers.add_parser('deletesite',
                                                   parents=[parser])
        delete_site_parser.add_argument('--site-name', default=None,
                                        help='name of site to delete')
        args = delete_site_parser.parse_args(sys.argv[3:])
        if args.site_name is None:
            args.site_name = sys.argv[2]
        return args

# TODO: COMPLETE, NO COMPLETE OPTION
