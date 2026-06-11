from setuptools import setup

setup(
    name='tokens_api',
    install_requires=['fastapi==0.136.0',
					  'uvicorn==0.48.0',
					  'starlette==1.2.1',
					# 'flask[async]',
                    # 'flask_api',
                    # 'flask_restful',
					# 'flask_cors',u
					'mongoengine==0.29.3',
                    'jsonpickle==4.1.2',
                    'requests==2.34.2',
					# "Werkzeug==2.2", # required for flask
					"supertokens-python==0.23.1"],
    zip_safe=False)
