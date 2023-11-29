from setuptools import setup

setup(name='client_gateway',
      description='client gateway for session-local',
      install_requires=['flask',
                        'flask_api',
                        'flask_restful',
						"Werkzeug==2.2",
                        'jsonpickle',
                        'requests'],
      zip_safe=False)
