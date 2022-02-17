import argparse
import unittest
from tabcmd.commands.auth.session import Session
from tests.e2e import credentials


# pytest -v tests/e2e/integration_tests.py
class E2EJsonTests(unittest.TestCase):

    def test_save_then_read(self):
        test_session = Session()
        test_session.username = 'USN'
        test_session.server = 'SRVR'
        test_session._save_token_to_json_file()
        new_session = Session()
        new_session._read_from_json()
        assert new_session.username == 'USN', new_session.username
        assert hasattr(new_session, 'password') is False, new_session
        assert new_session.server == 'SRVR', new_session.server


class E2EServerTests(unittest.TestCase):

    saved_site_id = ''

    def test_log_in(self):
        args = argparse.Namespace(
            server=credentials.server,
            site=credentials.site,
            token_name=credentials.token_name,
            token=credentials.token,
            username=None,
            password=None,
            logging_level=None,
            no_certcheck=True,
            prompt=True,
            no_prompt=False,
            proxy=None,
            no_cookie=False
        )
        test_session = Session()
        test_session.create_session(args)
        assert test_session.auth_token is not None
        assert test_session.site_id is not None
        assert test_session.user_id is not None
        E2EServerTests.saved_site_id = test_session.site_id

    def test_reuse_session(self):
        args = argparse.Namespace(
            server=None,
            site=None,
            token_name=None,
            token=None,
            username=None,
            password=None,
            logging_level=None,
            no_certcheck=True,
            prompt=True,
            no_prompt=False,
            proxy=None,
            no_cookie=False
        )
        test_session = Session()
        test_session.create_session(args)
        assert test_session.auth_token is not None
        assert test_session.site_id is not None
        assert test_session.user_id is not None
        assert test_session.site_id == E2EServerTests.saved_site_id
