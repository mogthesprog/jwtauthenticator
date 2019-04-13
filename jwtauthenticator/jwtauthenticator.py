from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.utils import url_path_join
from tornado import gen, web
from traitlets import Unicode, Bool
from jose import jwt

import base64

class JSONWebTokenLoginHandler(BaseHandler):

    def get(self):
        header_name = self.authenticator.header_name
        param_name = self.authenticator.param_name
        header_is_authorization = self.authenticator.header_is_authorization

        auth_header_content = self.request.headers.get(header_name, "")
        auth_cookie_content = self.get_cookie(self.authenticator.cookie_name , "")
        signing_certificate = self.authenticator.signing_certificate
        secret = self.authenticator.secret
        username_claim_field = self.authenticator.username_claim_field
        audience = self.authenticator.expected_audience
        tokenParam = self.get_argument(param_name, default=False)
        auth_login_redirect = self.authenticator.login_redirect
        auth_post_login_redirect = self.authenticator.post_login_redirect

        if auth_header_content and tokenParam:
           raise web.HTTPError(400)
        elif auth_header_content:
           if header_is_authorization:
              # we should not see "token" as first word in the AUTHORIZATION header, if we do it could mean someone coming in with a stale API token
              if auth_header_content.split()[0] != "bearer":
                 raise web.HTTPError(403)
              token = auth_header_content.split()[1]
           else:
              token = auth_header_content
        elif auth_cookie_content:
           token = auth_cookie_content
        elif tokenParam:
           token = tokenParam
        else:
    
            #t = base64.b64encode(auth_post_login_redirect.encode('ascii'))
            #print(t)

            _login_url = auth_login_redirect + base64.b64encode(auth_post_login_redirect.encode('ascii')).decode("utf-8")
            print("redirecting to osp logon page: " + _login_url)
            self.redirect(_login_url)

            # See if we've been given location where we can logon
            #if auth_login_redirect and auth_post_login_redirect:
            #raise web.HTTPError(401)


        claims = "";
        if secret:
            claims = self.verify_jwt_using_secret(token, secret, audience)
        elif signing_certificate:
            claims = self.verify_jwt_with_claims(token, signing_certificate, audience)

        username = self.retrieve_username(claims, username_claim_field)
        user = self.user_from_username(username)
        self.set_login_cookie(user)

        _url = url_path_join(self.hub.server.base_url, 'home')
        next_url = self.get_argument('next', default=False)
        if next_url:
            _url = next_url

        self.redirect(_url)

    @staticmethod
    def verify_jwt_with_claims(token, signing_certificate, audience):
        # If no audience is supplied then assume we're not verifying the audience field.
        if audience == "":
            opts = {"verify_aud": False}
        else:
            opts = {}
        with open(signing_certificate, 'r') as rsa_public_key_file:
            return jwt.decode(token, rsa_public_key_file.read(), audience=audience, options=opts)

    @staticmethod
    def verify_jwt_using_secret(json_web_token, secret, audience):
        # If no audience is supplied then assume we're not verifying the audience field.
        if audience == "":
            opts = {"verify_aud": False}
        else:
            opts = {}
        
        return jwt.decode(json_web_token, secret, algorithms=list(jwt.ALGORITHMS.SUPPORTED), audience=audience, options=opts)

    @staticmethod
    def retrieve_username(claims, username_claim_field):
        # retrieve the username from the claims
        username = claims[username_claim_field]
        if "@" in username:
            # process username as if email, pull out string before '@' symbol
            return username.split("@")[0]

        else:
            # assume not username and return the user
            return username


class JSONWebTokenAuthenticator(Authenticator):
    """
    Accept the authenticated JSON Web Token from header.
    """
    signing_certificate = Unicode(
        config=True,
        help="""
        The public certificate of the private key used to sign the incoming JSON Web Tokens.

        Should be a path to an X509 PEM format certificate filesystem.
        """
    )

    username_claim_field = Unicode(
        default_value='upn',
        config=True,
        help="""
        The field in the claims that contains the user name. It can be either a straight username,
        of an email/userPrincipalName.
        """
    )

    expected_audience = Unicode(
        default_value='',
        config=True,
        help="""HTTP header to inspect for the authenticated JSON Web Token."""
    )

    header_name = Unicode(
        default_value='Authorization',
        config=True,
        help="""HTTP header to inspect for the authenticated JSON Web Token.""")
        
    header_is_authorization = Bool(
        default_value=True,
        config=True,
        help="""Treat the inspected header as an Authorization header.""")

    param_name = Unicode(
        config=True,
        default_value='access_token',
        help="""The name of the query parameter used to specify the JWT token""")

    cookie_name = Unicode(
        config=True,
        default_value='XSRF-TOKEN',
        help="""The name of the cookie containing the JWT token""")

    login_redirect = Unicode(
        config=True,
        default_value='',
        help="""If user does not have a JWT, this is where they should go to get one""")

    post_login_redirect = Unicode(
        config=True,
        default_value='',
        help="""The logon url goes to this page after loggin you in""")

    secret = Unicode(
        config=True,
        help="""Shared secret key for siging JWT token.  If defined, it overrides any setting for signing_certificate""")

    def get_handlers(self, app):
        return [
            (r'/login', JSONWebTokenLoginHandler),
        ]

    @gen.coroutine
    def authenticate(self, *args):
        raise NotImplementedError()


class JSONWebTokenLocalAuthenticator(JSONWebTokenAuthenticator, LocalAuthenticator):
    """
    A version of JSONWebTokenAuthenticator that mixes in local system user creation
    """
    pass
