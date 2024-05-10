from setuptools import setup

setup(
    name='tokens_api',
    install_requires=['fastapi',
					  'uvicorn[standard]',
					  'starlette',
					# 'flask[async]',
                    # 'flask_api',
                    # 'flask_restful',
					# 'flask_cors',
					'mongoengine',
                    'jsonpickle',
                    'requests',
					# "Werkzeug==2.2", # required for flask
					"supertokens-python"],
    zip_safe=False)
