from setuptools import setup

setup(name='client_gateway',
      #   version='0.1',
      description='client gateway for session-local',
      packages=['api', 'services', 'data'],
      install_requires=['flask', 
      'flask_restful', 
      'jsonpickle', 
      'docker',
      'requests'],
      zip_safe=False)
