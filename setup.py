from setuptools import setup, find_packages

setup(
    name='registry_scraper',
    version='0.1.0',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'boto==2.38.0'
    ],
    entry_points={
        'console_scripts': [
            'scrape = registry_scraper.__main__:main'
        ]
    }
)
