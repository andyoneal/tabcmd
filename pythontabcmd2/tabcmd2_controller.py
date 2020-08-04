import argparse
import sys
from .parsers.parent_parser import ParentParser
from .logger_config import get_logger


logger = get_logger('pythontabcmd2.tabcmd2_controller', 'info')


class Tabcmd2Controller:
    def __init__(self):
        pass

    def get_command_strategy(self):
        # parser = argparse.ArgumentParser()
        # parser.add_argument('command', help='tabcmd commands to run')
        parent_parser = ParentParser()
        parser = parent_parser.parent_parser_with_global_options()
        subparsers = parser.add_subparsers()
        main_parser = subparsers.add_parser('command parser', parents=[parser])
        main_parser.add_argument('command', help='tabcmd commands to run')
        args = parser.parse_args(sys.argv[1:2])
        if args.command is None:
            logger.info('Unrecognized command please try again')
            parser.print_help()
        else:
            return args.command
