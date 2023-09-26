from setuptools import setup


setup(
    name='stream_registry',
    install_requires=['flask',
                      'flask_api',
                      'flask_restful',
                      'jsonpickle',
                      'requests',
                      'mongoengine'],
    zip_safe=False)
