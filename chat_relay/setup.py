from setuptools import setup


setup(
    name='chat_relay',
    install_requires=["jsonpickle==4.1.2", 
					"requests==2.34.2",
					"fastapi==0.136.3",
					"websockets==16.0",
					'asyncio==4.0.0',
					'httpx==0.28.1',
					'uvicorn==0.48.0'
					]
)
