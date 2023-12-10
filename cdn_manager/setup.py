try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='cdn_manager',
    install_requires=[
        'flask',
        'flask_api',
        'flask_restful',
		'jsonpickle',
        'Werkzeug==2.2',
        'requests',
        'signals'
	]
)
