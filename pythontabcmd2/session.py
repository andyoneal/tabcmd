
try:
    from . import tableauserverclient as TSC
    from .constants_errors import Constants
except:
    import tableauserverclient as TSC  
    from constants_errors import Constants
    
import os
import shlex  
import dill as pickle


class Session:
    def __init__(self, server, username=None, password=None, token_name=None, site=None, personal_token=None):
        self.username = username 
        self.password = password 
        self.server = server
        self.site = site
        self.token_name = token_name
        self.personal_token = personal_token

    def create_session(self):

        if self.username: 
            try: 
                tableau_auth = TSC.TableauAuth(self.username, self.password, self.site)
                tableau_server = TSC.Server(self.server, use_server_version=True)
                signed_in_object = tableau_server.auth.sign_in(tableau_auth)
                self.pickle_auth_objects(signed_in_object, tableau_server)
                print("=======Successfully established connection=======")
            except TSC.ServerResponseError as e:
                if e.code == constants_errors.login_error:
                    print("Login Error, Please Login again")

        elif self.token_name:
            try:
                tableau_auth = TSC.PersonalAccessTokenAuth(self.token_name, self.personal_token, self.site)
                tableau_server = TSC.Server(self.server, use_server_version=True)
                signed_in_object = tableau_server.auth.sign_in_with_personal_access_token(tableau_auth)
                self.pickle_auth_objects(signed_in_object, tableau_server)
            except TSC.ServerResponseError as e:
                if e.code == constants_errors.login_error:
                    print("Login Error, Please Login again")

        
    def pickle_auth_objects(self, signed_in_object, tableau_server):
        signed_in_object_str= str(signed_in_object)
        home_path = os.path.expanduser("~")
        file_path = os.path.join(home_path, 'tabcmd.pkl')
        with open(str(file_path), 'wb') as output:
            pickle.dump(signed_in_object_str, output, pickle.HIGHEST_PROTOCOL)
            pickle.dump(tableau_server, output, pickle.HIGHEST_PROTOCOL)
        

