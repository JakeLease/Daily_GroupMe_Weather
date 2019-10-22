from setuptools import setup


setup(
    name="GroupMe_Daily_Weather",
    version="1.0",
    description="Auto sends weather report from Open Weather API when certain Text is called",
    author="Jacob Liese",
    author_email="Jakeuplease@gmail.com",
    packages=['GroupMe_Daily_Weather'],
    install_requires=["requests", "uuid", ],
)
