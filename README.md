# JupyterHub tokenauthenticator - A JWT Token Authenticator for JupyterHub

Authenticate to Jupyterhub using an authenticating proxy that can set the Authorization header with the content of a JSONWebToken.

## Installation

This package can be installed with pip:

```
cd jwtauthenticator pip install .
```

Alternately, you can add this project folder to your PYTHONPATH.

## Configuration

You should edit your :file:`jupyterhub_config.py` to set the authenticator class, the JSONWebTokenLocalAuthenticator provides features such as local user creation. If you already have local users then you should use the JSONWebTokenAuthenticator authenticator class:

##### For authentication and local user creation
```
c.JupyterHub.authenticator_class = 'jwtauthenticator.jwtauthenticator.JSONWebTokenLocalAuthenticator'
```

This class is derived from LocalAuthenticator and therefore provides features such as the ability to add local accounts through the admin interface if configured to do so.

##### For authentication of the token only

```
c.JupyterHub.authenticator_class = 'jwtauthenticator.jwtauthenticator.JSONWebTokenAuthenticator'
```

##### Required configuration

You'll also need to set some configuration options including the location of the signing certificate (in PEM format), field containing the userPrincipalName or sAMAccountName/username, and the expected audience of the JSONWebToken. This last part is optional, if you set audience to an empty string then the authenticator will skip the validation of that field.

```
c.LocalAuthenticator.signing_certificate = '/foo/bar/adfs-signature.crt'    # The certificate used to sign the incoming JSONWebToken, must be in PEM Format
c.LocalAuthenticator.username_claim_field = 'upn'                           # The claim field contianing the username/sAMAccountNAme/userPrincipalName
c.LocalAuthenticator.audience = 'https://myApp.domain.local/'               # This config option should match the aud field of the JSONWebToken, empty string to disable the validation of this field.
#c.LocalAuthenticator.create_system_users = True                            # This will enable local user creation upon authentication, requires JSONWebTokenLocalAuthenticator, see below.
#c.LocalAuthenticator.header_name = 'Authorization'                         # default value
```

You should be able to start jupyterhub. :)

## Issues

If you have any issues or bug reports, all are welcome in the issues section. I'll do my best to respond quickly.

## Contribution

If you want to fix the bugs yourself then raise a PR and I'll take a look :)
