from setuptools import setup

setup(name='Session-Local',
      #   version='0.1',
      description='POC; streaming video to nginx-rtmp, some processing and distribution to cdn',
      packages=['utils', 'shared_model'],
      # these two above are the only possibly shared packages
      # other projects don't have to be mentined in this list
      # since they are not behaving like packages, wont be imported
      zip_safe=False)
