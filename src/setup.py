from setuptools import setup

setup(name='Session-Local',
      #   version='0.1',
      description='POC; streaming video from obs to nginx-rtmp, some processing and distribution to cdn',
      packages=['utils', 'client_gateway'],
      # packages=['utils',
      #           'client_gateway.api',
      #           'client_gateway.services',
      #           'client_gateway.data'],
      zip_safe=False)
