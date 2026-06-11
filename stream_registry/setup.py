from setuptools import setup

setup(
    name='stream_registry',
    install_requires=[
            'fastapi==0.136.0',
					  'uvicorn==0.48.0',
					#   'starlette',
					#   'asyncprocess',
            'jsonpickle==4.1.2',
            'requests==2.34.2',
					  'ffmpeg-python==0.2.0',
					#   "Werkzeug==2.2", 
					# ^ this specific version was required for flasks status.
            'mongoengine==0.29.3'],
    zip_safe=False)
