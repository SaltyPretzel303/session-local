from setuptools import setup

setup(
    name='tokens_auth',
    install_requires=['flask[async]',
                    # 'flask_api',
                    # 'flask_restful',
					'flask_cors',
                    'jsonpickle',
                    'requests',
					"Werkzeug==2.2",
					"supertokens-python"],
    zip_safe=False)
