from setuptools import setup


setup(
    name='cdn_manager',
    install_requires=[
        'flask==3.1.3',
        'flask_api==3.1',
        'flask_restful==0.3.10',
		'jsonpickle==4.1.2',
        # 'Werkzeug==2.2',
        'requests==2.34.2',
        'signals==0.0.2',
        'pyping==0.0.6'
	]
)
