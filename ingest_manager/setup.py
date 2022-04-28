from setuptools import setup

setup(name='ingest_manager',
      #   version='0.1',
      description='video ingest api for session-local',
    #   packages=['api', 'services', 'data'],
      install_requires=['flask',
                        'flask_restful',
                        'jsonpickle',
                        'docker'],
      zip_safe=False)
