from setuptools import setup

setup(
    name='stream_registry',
    install_requires=['fastapi',
					  'uvicorn[standard]',
					#   'starlette',
					  'asyncprocess',
                      'jsonpickle',
					  'dataclasses',
                      'requests',
					  'ffmpeg-python',
					#   "Werkzeug==2.2", 
					# ^ this specific version was required for flasks status.
                      'mongoengine'],
    zip_safe=False)
