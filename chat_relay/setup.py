from setuptools import setup


setup(
    name='chat_relay',
    install_requires=["jsonpickle", 
					"requests",
					"fastapi",
					"websockets",
					'asyncio',
					'httpx'
					]
)
