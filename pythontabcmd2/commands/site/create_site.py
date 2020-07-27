from .. import CreateProjectParser
from ..commands import Commands
from ... import tableauserverclient as TSC
from .. import get_logger
from ...parsers.create_site_parser import CreateSiteParser

logger = get_logger('pythontabcmd2.create_site_command')


class CreateSiteCommand:
    def __init__(self, args, admin_mode):
        self.site_name = args.site_name
        self.admin_mode = admin_mode
        self.url = args.url
        self.user_quota = args.user_quota
        self.storage_quota = args.storage_quota

    @classmethod
    def parse(cls):
        args, admin_mode = CreateSiteParser.create_site_parser()
        return cls(args, admin_mode)

    def run_command(self):
        signed_in_object, server_object = Commands.deserialize()
        self.create_site(server_object)

    def create_site(self, server):
        """Method to create a site using tableauserverclient methods"""
        new_site = TSC.SiteItem(name=self.site_name, content_url=self.url, admin_mode=self.admin_mode,user_quota=self.user_quota, storage_quota=self.storage_quota)
        self.create_site_helper(server, new_site)

    def create_site_helper(self, server, site):
        """ Helper method to catch server errors thrown by tableauserverclient"""
        try:
            new_site = server.sites.create(site)
            logger.info('Successfully created a new site called: %s' % new_site.name)
            return new_site
        except TSC.ServerResponseError as e:
            logger.info('Error: We have already created this project: %s' % new_site.name)

