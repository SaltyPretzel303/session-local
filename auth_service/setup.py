from setuptools import setup

setup(
    name='auth_service',
    install_requires=['flask',
                      'flask_api',
                      'flask_restful',
                      'flask_session',
                      'jsonpickle',
                      'requests',
                      'mongoengine',
					  'python-dateutil'],
    zip_safe=False)
