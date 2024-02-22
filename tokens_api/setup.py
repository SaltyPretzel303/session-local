from setuptools import setup

setup(
    name='tokens_api',
    install_requires=['flask[async]',
                    # 'flask_api',
                    # 'flask_restful',
					'flask_cors',
					'mongoengine',
					'flask_api',
                    'jsonpickle',
                    'requests',
					"Werkzeug==2.2",
					"supertokens-python"],
    zip_safe=False)
