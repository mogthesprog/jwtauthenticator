from setuptools import setup

setup(
    name='jupyterhub-jwtauthenticator',
    version='0.1',
    description='JSONWebToken Authenticator for JupyterHub',
    url='https://github.com/mogthesprog/jwtauthenticator',
    author='mogthesprog',
    author_email='mevanj89@gmail.com',
    license='Apache 2.0',
    tests_require = [
    'unittest2',
    ],
    test_suite = 'unittest2.collector',
    packages=['jwtauthenticator'],
    install_requires=[
        'jupyterhub',
        'python-jose',
    ]
)
