from setuptools import setup, find_packages

setup(
    name="DealsBot",
    version="1.0",
    packages=find_packages(),
    author="Antonio Davide Cali",
    description="Bot to scrape website for deals",
    author_email="antoniodavidecali@gmail.com",
    python_requires=">=3.7",
    install_requires=[
        'uvicorn==0.11.8',
        'python-slugify==4.0.1',
        'Pillow==7.2.0',
        'fastapi==0.61.0',
        'telethon==1.16.2',
        'APScheduler==3.6.3',
        'requests==2.24.0',
        'selectorlib==0.16.0',
        'peewee==3.13.3',
        'cfscrape==2.1.1',
        'beautifulsoup4==4.9.3'
    ]
)
