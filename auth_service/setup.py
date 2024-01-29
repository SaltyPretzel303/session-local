from setuptools import setup

setup(name='auth_service',
    install_requires=['flask',
                      'flask_api',
                      'flask_restful',
                      'flask_session',
                      'jsonpickle',
                      'requests',
					  "Werkzeug==2.2",
                      'mongoengine',
					  'python-dateutil',
					  "bcrypt",
					  "flask-cors"],
    zip_safe=False)
